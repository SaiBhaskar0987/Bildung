from typing_extensions import Literal
import dspy
from aiassist.search_engine import PandasVectorSearch
from core import settings



# Configuring local Ollama LLM
lm = dspy.LM(settings.OLLAMA_MODEL, api_base=settings.OLLAMA_URL, api_key='')
print("DEBUG: Configured local Ollama LLM.", lm)
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
    def __init__(self, search_engine: PandasVectorSearch):
        super().__init__()
        self.prog = dspy.ChainOfThought(CourseAgentSignature)
        self.search_engine = search_engine

    def forward(self, question):
        retrieved_fact = self.search_engine.search(question)
        if retrieved_fact:
            return self.prog(context=retrieved_fact, question=question), True
        else:
            return self.prog(context="Use general knowledge.", question=question), False






class ClassifierAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        search_engine: PandasVectorSearch = PandasVectorSearch()
        self.predictor = dspy.ChainOfThought(ClassifierSignature)
        self.course_agent = CourseAgent(search_engine)

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
        
