from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_core.documents import Document

MEDIA_ROOT = Path("D:/my_project/Bildung/media")

def load_pdfs(pdfs):
    documents = []

    for pdf in pdfs:
        abs_path = MEDIA_ROOT / pdf

        if not abs_path.exists():
            raise ValueError(f"PDF not found: {abs_path}")

        loader = PyPDFLoader(str(abs_path))
        pages = loader.load()   

        for d in pages:         
            documents.append(
                Document(
                    page_content=d.page_content,
                    metadata={
                        **(d.metadata or {}),
                        "source": pdf,         
                        "source_type": "pdf"    
                    }
                )
            )

    return documents
