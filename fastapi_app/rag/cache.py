import pickle
from pathlib import Path
import hashlib

CACHE_DIR = Path("rag_cache")
CACHE_DIR.mkdir(exist_ok=True)


def cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    hashed = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{hashed}.pkl"


def save_vector_store(quiz_id, vector_store):
    with open(cache_path(quiz_id), "wb") as f:
        pickle.dump(vector_store, f)

def load_vector_store(quiz_id):
    path = cache_path(quiz_id)
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

