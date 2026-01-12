from typing_extensions import Literal
import dspy
from core import settings
from sentence_transformers import SentenceTransformer, util
import os
import pandas as pd


# Configuring local LLM which is being runned using Ollama model runner
# LLM name and LLM url is declared in settings.py
lm = dspy.LM(settings.LOCAL_MODEL_NAME, api_base=settings.LOCAL_MODEL_URL, api_key='')
print("DEBUG: Configured local Model running using Ollama model runner .", lm)
dspy.settings.configure(lm=lm)



# --- Signatures ---

class ClassifierSignature(dspy.Signature):
    """
    Classify a user's query into one of two categories:
    CRITICAL INSTRUCTION: check for keywords first. If the query contains words 'course' or 'certificate' (in any context), the classification MUST be 'course'.
    1. 'course': Questions about courses related modules of a e-learning platform like what is the course structure, how to enroll, how to download certificate etc.
    2. 'general': Questions about account issues, greetings, help and support or non-academic topics.
    """
    # The input field
    question = dspy.InputField(desc="The user's raw question text")
    # The output field with strict typing
    category: Literal['general', 'course'] = dspy.OutputField(desc="The classification label")
    response = dspy.OutputField(desc="Answer (if general) or Reasoning (if course)")



class CourseAgentSignature(dspy.Signature):
    """Answer the question based strictly on the retrieved context."""
    context = dspy.InputField(desc="Verified facts from the FAQ Excel sheet")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="Concise conversational response")





# --- Modules ---
class CourseAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(CourseAgentSignature)
        self.load_dataset_encode()
        

    def forward(self, question):
        retrieved_fact = self.search_dataset(question)
        if retrieved_fact:
            return self.prog(context=retrieved_fact, question=question), True
        else:
            return self.prog(context="Use general knowledge.", question=question), False

    def load_dataset_encode(self):
        print(f"Loading Knowledge Base from {settings.DATASET_PATH}...")

        if not os.path.exists(settings.DATASET_PATH):
            # Fallback for safety
            print("Warning: Excel file not found. Creating empty DF.")
            self.df = pd.DataFrame(columns=["Question", "Answer"])
            self.question_embeddings = None
            return

        self.df = pd.read_excel(settings.DATASET_PATH)
        
        print(f"Loading Embedding Model: {settings.EMBEDDING_MODEL_PATH}")
        # model_path = './local_model' -- this can be used to load a local model if needed
        self.encoder = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
        
        # Pre-compute embeddings
        self.question_embeddings = self.encoder.encode(
            self.df['Question'].tolist(), 
            convert_to_tensor=True
        )
        print("Knowledge Base Loaded.")
        return None
    

    def search_dataset(self, query: str, threshold=0.4):
        if self.df.empty or self.question_embeddings is None:
            return None
            
        query_embedding = self.encoder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.question_embeddings, top_k=1)
        
        if not hits or not hits[0]:
            return None
            
        best_hit = hits[0][0]

        if best_hit['score'] > threshold:
            return self.df.iloc[best_hit['corpus_id']]['Answer']
        
        return None





class ClassifierAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(ClassifierSignature)
        self.course_agent = CourseAgent()

    def forward(self, question):
        prediction = self.predictor(question=question)
        category = prediction.category.lower().strip()
        
        # Logic Flow
        if 'course' in category:
            answer_pred, context_used = self.course_agent(question)
            return answer_pred.answer, "Course", context_used
        else:
            # Default to General
            print("Routing to General response.", prediction)
            return prediction.response, "General", False
        
