from typing_extensions import Literal
import os
import dspy
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
from core import settings

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


class ClassifierSignature(dspy.Signature):
    """
    Decide if a question is about course-related content or general platform usage.
    """
    question = dspy.InputField()
    category: Literal["course", "general"] = dspy.OutputField()


class AnswerSignature(dspy.Signature):
    """
    Generate a helpful response based on provided context.
    """
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField(desc="Clear, concise response")


DATASET_PATH = "media/Q_A/Bildung_QA.xlsx"
EMBEDDING_MODEL_PATH = 'all-MiniLM-L6-v2'

class CourseAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(AnswerSignature)
        self._load_knowledge_base()

    def forward(self, question: str):
        context = self._search_dataset(question)

        if not context:
            context = """
You are an AI assistant for an online learning platform.
Explain clearly using bullet points if helpful.
"""

        result = self.prog(context=context, question=question)
        return result.answer, bool(context)

    def _load_knowledge_base(self):
        print(f"📄 Loading KB: {DATASET_PATH}")

        if not os.path.exists(DATASET_PATH):
            print("⚠️ KB not found – running without RAG")
            self.df = pd.DataFrame()
            self.embeddings = None
            return

        self.df = pd.read_excel(DATASET_PATH)
        self.encoder = SentenceTransformer(EMBEDDING_MODEL_PATH)

        self.embeddings = self.encoder.encode(
            self.df["Question"].tolist(),
            convert_to_tensor=True
        )

        print("✅ Knowledge Base loaded")

    @lru_cache(maxsize=256)
    def _search_dataset(self, query: str, threshold: float = 0.4):
        if self.df.empty or self.embeddings is None:
            return None

        query_vec = self.encoder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_vec, self.embeddings, top_k=1)

        if hits and hits[0][0]["score"] >= threshold:
            return self.df.iloc[hits[0][0]["corpus_id"]]["Answer"]

        return None


class GeneralAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.Predict(AnswerSignature)

    def forward(self, question: str):
        context = """
You are a helpful assistant for an e-learning platform.

You can answer questions about:
- Instructor payments
- Platform policies
- Account & dashboard usage
- Certificates & verification
- General help

Use bullet points when useful.
"""
        result = self.prog(context=context, question=question)
        return result.answer


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
            answer, used_context = self.course_agent(question)
            return answer, "Course", used_context

        answer = self.general_agent(question)
        return answer, "General", False
