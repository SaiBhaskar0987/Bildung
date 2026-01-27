from fastapi_app.rag.text_splitter import split_docs
from fastapi_app.rag.embeddings import build_vector_store
from fastapi_app.rag.pdf_loader import load_pdfs
from fastapi_app.rag.video_loader import load_videos
from fastapi_app.rag.cache import load_vector_store, save_vector_store
from fastapi_app.services.quiz_access import (get_quiz_pdfs, get_quiz_videos,)

def get_or_create_vector_store(
    quiz_id: int,
    scope: str,
    source: str,
    db
):
    VALID_SOURCES = {"pdf", "video", "both"}
    if source not in VALID_SOURCES:
        raise ValueError(f"Invalid source: {source}")

    cache_key = f"quiz:{quiz_id}|scope:{scope}|source:{source}"
    vector_store = load_vector_store(cache_key)
    if vector_store:
        return vector_store

    documents = []

    if source in ("pdf", "both"):
        pdfs = get_quiz_pdfs(quiz_id, scope, db)
        if pdfs:
            documents.extend(load_pdfs(pdfs))

    if source in ("video", "both"):
        videos = get_quiz_videos(quiz_id, scope, db)
        if videos:
            documents.extend(load_videos(videos))

    if not documents:
        return None

    chunks = split_docs(documents)
    vector_store = build_vector_store(chunks)

    save_vector_store(cache_key, vector_store)
    return vector_store
