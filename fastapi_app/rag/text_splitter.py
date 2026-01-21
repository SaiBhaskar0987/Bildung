from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_docs(docs):
    """
    Split documents into semantic chunks for embeddings
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       
        chunk_overlap=120,     
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_documents(docs)
