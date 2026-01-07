import pandas as pd
from sentence_transformers import SentenceTransformer, util
import os
from core import settings

class PandasVectorSearch:
    def __init__(self):
        print(f"Loading Knowledge Base from {settings.EXCEL_PATH}...")
        
        if not os.path.exists(settings.EXCEL_PATH):
            # Fallback for safety
            print("Warning: Excel file not found. Creating empty DF.")
            self.df = pd.DataFrame(columns=["Question", "Answer"])
            self.question_embeddings = None
            return

        self.df = pd.read_excel(settings.EXCEL_PATH)
        
        # Load Model
        print(f"Loading Embedding Model: {settings.EMBEDDING_MODEL_PATH}")
        # model_path = './local_model'
        self.encoder = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
        
        # Pre-compute embeddings
        if not self.df.empty:
            self.question_embeddings = self.encoder.encode(
                self.df['Question'].tolist(), 
                convert_to_tensor=True
            )
        print("Knowledge Base Loaded.")

    def search(self, query: str, threshold=0.4):
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