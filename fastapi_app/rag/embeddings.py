from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def _to_text(item) -> str:
    """
    Convert ANY object into a safe string for embeddings.
    This function MUST always return str.
    """

    if item is None:
        return ""

    if isinstance(item, str):
        return item

    if isinstance(item, Document):
        return item.page_content or ""

    if isinstance(item, dict):
        return (
            item.get("text")
            or item.get("question")
            or item.get("content")
            or str(item)
        )

    return str(item)


def build_vector_store(documents):
    """
    Build FAISS vector store safely from ANY input.
    Accepts:
    - List[str]
    - List[Document]
    - List[dict]
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    normalized_docs = []

    for item in documents:
        text = _to_text(item)

        if not isinstance(text, str):
            raise TypeError(
                f"Embedding input must be str, got {type(text)}"
            )

        if not text.strip():
            continue 

        normalized_docs.append(
            Document(page_content=text)
        )

    if not normalized_docs:
        raise ValueError("No valid documents to embed")

    return FAISS.from_documents(
        normalized_docs,
        embedding=embeddings
    )
