import pickle
from pathlib import Path

CACHE_DIR = Path("rag_cache")
CACHE_DIR.mkdir(exist_ok=True)

def cache_path(quiz_id):
    return CACHE_DIR / f"quiz_{quiz_id}.pkl"

def save_vector_store(quiz_id, vector_store):
    with open(cache_path(quiz_id), "wb") as f:
        pickle.dump(vector_store, f)

def load_vector_store(quiz_id):
    path = cache_path(quiz_id)
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

