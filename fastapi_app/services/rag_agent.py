
from typing_extensions import Literal
import os
import faiss
import numpy as np
import pandas as pd
import dspy
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


dspy.settings.configure(
    lm=dspy.LM(
        model="gpt-5-nano",
        api_key=os.getenv("API_KEY"),
        temperature=1.0,
        max_tokens=16000,
        timeout=20,
    )
)

print("✅ OpenAI LLM configured: gpt-5-nano")

DATASET_PATH = "media/Q_A/E-learning_Dataset.xlsx"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 5
SIM_THRESHOLD = 0.40

class AnswerSignature(dspy.Signature):
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()

class CourseAgent(dspy.Module):

    def __init__(self):
        super().__init__()
        self._load_knowledge_base()

    def _load_knowledge_base(self):

        print(f"📄 Loading KB: {DATASET_PATH}")

        if not os.path.exists(DATASET_PATH):
            print("⚠️ KB not found")
            self.df = pd.DataFrame()
            return

        self.df = pd.read_excel(DATASET_PATH)
        self.df = self.df.dropna(subset=["Question", "Answer"])

        self.df["Question"] = self.df["Question"].astype(str)
        self.df["Answer"] = self.df["Answer"].astype(str)

        self.df["combined"] = (
            self.df["Question"] + " " + self.df["Answer"]
        )

        self.encoder = SentenceTransformer(EMBEDDING_MODEL)

        embeddings = self.encoder.encode(
            self.df["combined"].tolist(),
            convert_to_numpy=True,
            show_progress_bar=True
        )

        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        self.embeddings = embeddings

        tokenized_corpus = [
            doc.lower().split()
            for doc in self.df["combined"]
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)


    @lru_cache(maxsize=256)
    def _search_dataset(self, query: str):

        if self.df.empty:
            return None

        query_clean = query.strip().lower()

        exact = self.df[
            self.df["Question"].str.lower().str.strip() == query_clean
        ]
        if not exact.empty:
            return exact.iloc[0]["Answer"]

        query_vec = self.encoder.encode(
            [query],
            convert_to_numpy=True
        )

        faiss.normalize_L2(query_vec)

        similarities, indices = self.index.search(query_vec, TOP_K)

        semantic_scores = similarities[0]
        semantic_indices = indices[0]

        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        keyword_indices = np.argsort(bm25_scores)[::-1][:TOP_K]

        candidate_indices = list(set(semantic_indices) | set(keyword_indices))

        ranked = []
        max_bm25 = max(bm25_scores) + 1e-6

        for idx in candidate_indices:

            sem_score = 0
            if idx in semantic_indices:
                sem_score = semantic_scores[
                    list(semantic_indices).index(idx)
                ]

            bm_score = bm25_scores[idx] / max_bm25

            final_score = (0.7 * sem_score) + (0.3 * bm_score)

            ranked.append((idx, final_score))

        ranked.sort(key=lambda x: x[1], reverse=True)

        if not ranked:
            return None

        best_idx, best_score = ranked[0]

        if best_score >= SIM_THRESHOLD:
            return self.df.iloc[best_idx]["Answer"]

        return None


    def forward(self, question: str):

        context = self._search_dataset(question)

        if context:
            return context, True

        return None, False


class GeneralAgent(dspy.Module):

    def __init__(self):
        super().__init__()
        self.prog = dspy.Predict(AnswerSignature)

    def forward(self, question: str):

        context = """
You are a helpful assistant for an e-learning platform.
Provide clear and helpful explanations.
Use bullet points when useful.
Provide only 4-5 steps which are important.
"""

        result = self.prog(
            context=context,
            question=question
        )
        return result.answer


class ClassifierAgent(dspy.Module):

    def __init__(self):
        super().__init__()
        self.course_agent = CourseAgent()
        self.general_agent = GeneralAgent()

    def forward(self, question: str):

        dataset_answer, found = self.course_agent(question)

        if found:
            return dataset_answer, "Dataset", True

        general_answer = self.general_agent(question)
        return general_answer, "General", False