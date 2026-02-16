import os
import re
import json
import hashlib
import unicodedata
import logging
from functools import lru_cache
import dspy
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

# =========================================================
# LLM CONFIG
# =========================================================
dspy.settings.configure(
    lm=dspy.LM(
        model="gpt-5-nano",
        api_key=os.getenv("API_KEY"),
        temperature=1.0,
        max_tokens=16000,
        timeout=20,
    )
)

logger = logging.getLogger(__name__)
logger.info("OpenAI LLM configured: gpt-5-nano")


# =========================================================
# DSPy SIGNATURES
# =========================================================
class AnswerSignature(dspy.Signature):
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField(desc="Clear, concise response")


# =========================================================
# COURSE AGENT (Improved RAG)
# =========================================================
DATASET_PATH = "media/Q_A/Bildung_QA.xlsx"
EMBED_PATH = "media/Q_A/processed/question_embeddings.pt"
EMBED_META_PATH = "media/Q_A/processed/question_embeddings.meta.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class CourseAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(AnswerSignature)
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.df = pd.DataFrame()
        self.embeddings = None
        self._load_knowledge_base()

    # -----------------------------------------------------
    # Load KB + embeddings
    # -----------------------------------------------------
    def _load_knowledge_base(self):
        if not os.path.exists(DATASET_PATH):
            logger.warning("KB not found at %s", DATASET_PATH)
            self.df = pd.DataFrame()
            self.embeddings = None
            return

        logger.info("Loading processed KB from %s", DATASET_PATH)
        raw_df = pd.read_excel(DATASET_PATH)
        self.df = self._preprocess_dataframe(raw_df)

        if self.df.empty:
            logger.warning("KB is empty after preprocessing")
            self.embeddings = None
            return

        dataset_hash = self._dataset_hash(self.df)
        row_count = len(self.df)
        can_use_cache = False

        if os.path.exists(EMBED_PATH) and os.path.exists(EMBED_META_PATH):
            try:
                cached_embeddings = torch.load(EMBED_PATH, map_location="cpu")
                if not isinstance(cached_embeddings, torch.Tensor):
                    raise ValueError("Cached embeddings are not a tensor")

                meta = self._load_embed_meta()
                can_use_cache = self._is_cache_valid(
                    meta=meta,
                    dataset_hash=dataset_hash,
                    row_count=row_count,
                    embedding_rows=int(cached_embeddings.shape[0]),
                )
                if can_use_cache:
                    self.embeddings = cached_embeddings
                    logger.info("Loaded cached embeddings")
            except Exception as exc:
                logger.warning("Failed loading cached embeddings: %s", exc)

        if not can_use_cache:
            logger.info("Generating embeddings (Q + A)")
            self.embeddings = self.encoder.encode(
                self.df["rag_text"].tolist(),
                convert_to_tensor=True,
                normalize_embeddings=True,
                batch_size=64,
                show_progress_bar=False,
            )
            self._save_embeddings_and_meta(dataset_hash=dataset_hash, row_count=row_count)

        total_rows = len(self.df)
        vector_rows = int(self.embeddings.shape[0])
        coverage = (vector_rows / total_rows) * 100 if total_rows > 0 else 0

        logger.info("Vectorization coverage: %.2f%%", coverage)
        logger.info("Embedding shape: %s", tuple(self.embeddings.shape))
        logger.info("KB ready")

    @staticmethod
    def _clean_text(text: str) -> str:
        text = unicodedata.normalize("NFKC", str(text))
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {"Question", "Answer"}
        missing = required - set(df.columns)
        if missing:
            logger.warning("KB missing required columns: %s", ", ".join(sorted(missing)))
            return pd.DataFrame()

        df = df.copy()
        df["Question"] = df["Question"].fillna("").map(self._clean_text)
        df["Answer"] = df["Answer"].fillna("").map(self._clean_text)

        # Keep only usable rows and remove exact duplicate questions.
        df = df[(df["Question"] != "") & (df["Answer"] != "")]
        df = df.drop_duplicates(subset=["Question"], keep="first").reset_index(drop=True)

        df["rag_text"] = "Question: " + df["Question"] + "\nAnswer: " + df["Answer"]
        return df

    @staticmethod
    def _dataset_hash(df: pd.DataFrame) -> str:
        payload = "\n".join(df["Question"].tolist()) + "\n---\n" + "\n".join(df["Answer"].tolist())
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _load_embed_meta() -> dict:
        with open(EMBED_META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _is_cache_valid(meta: dict, dataset_hash: str, row_count: int, embedding_rows: int) -> bool:
        return (
            meta.get("embedding_model") == EMBEDDING_MODEL
            and meta.get("dataset_hash") == dataset_hash
            and int(meta.get("row_count", -1)) == row_count
            and embedding_rows == row_count
        )

    def _save_embeddings_and_meta(self, dataset_hash: str, row_count: int) -> None:
        embed_dir = os.path.dirname(EMBED_PATH)
        if embed_dir:
            os.makedirs(embed_dir, exist_ok=True)

        torch.save(self.embeddings, EMBED_PATH)
        with open(EMBED_META_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "embedding_model": EMBEDDING_MODEL,
                    "dataset_hash": dataset_hash,
                    "row_count": row_count,
                },
                f,
            )

    # -----------------------------------------------------
    # Retrieval
    # -----------------------------------------------------
    @lru_cache(maxsize=256)
    def _retrieve(self, query: str, threshold: float = 0.5, top_k: int = 5):
        if self.df.empty or self.embeddings is None:
            return None, False

        query_vec = self.encoder.encode(
            query,
            convert_to_tensor=True,
            normalize_embeddings=True,
        ).unsqueeze(0)

        hits = util.semantic_search(
            query_vec,
            self.embeddings,
            top_k=min(top_k, len(self.df)),
        )

        if not hits or not hits[0]:
            return None, False

        best_score = hits[0][0]["score"]
        if best_score < threshold:
            return None, False

        contexts = []
        for hit in hits[0]:
            row = self.df.iloc[hit["corpus_id"]]
            contexts.append(f"Question: {row['Question']}\nAnswer: {row['Answer']}")

        return "\n\n".join(contexts), True

    # -----------------------------------------------------
    # Forward
    # -----------------------------------------------------
    def forward(self, question: str):
        normalized_question = self._clean_text(question)
        if not normalized_question:
            return "Please provide a valid question.", False

        context, used_rag = self._retrieve(normalized_question)

        if not used_rag:
            context = """
You are an expert AI tutor for an online learning platform.

If no exact match is found:
- Use general e-learning knowledge
- Avoid inventing platform-specific features
- Be practical and structured
"""

        result = self.generator(context=context, question=normalized_question)
        return result.answer, used_rag


# =========================================================
# GENERAL AGENT
# =========================================================
class GeneralAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.Predict(AnswerSignature)

    def forward(self, question: str):
        context = """
You are a helpful assistant for an e-learning platform.

You can answer questions about:
- Instructor payments
- Policies
- Dashboard usage
- Certificates
- Account management

Use bullet points when helpful.
"""
        result = self.generator(context=context, question=question)
        return result.answer


# =========================================================
# CLASSIFIER AGENT
# =========================================================
class ClassifierAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.course_agent = CourseAgent()
        self.general_agent = GeneralAgent()

    def _fast_classify(self, question: str) -> str:
        keywords = [
            "course", "certificate", "module", "lecture",
            "quiz", "assignment", "enroll", "progress"
        ]
        q = question.lower()
        return "course" if any(k in q for k in keywords) else "general"

    def forward(self, question: str):
        category = self._fast_classify(question)

        if category == "course":
            answer, used_rag = self.course_agent(question)
            return answer, "Course", used_rag

        answer = self.general_agent(question)
        return answer, "General", False
