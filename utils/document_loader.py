import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.base import Embeddings

def create_vector_store_from_pdfs(pdf_directory: str, embedding_model: Embeddings, index_path: str):
    """
    Loads PDF documents from a directory, splits them into chunks, creates a FAISS vector store,
    and saves it to disk.

    Args:
        pdf_directory (str): The path to the directory containing the PDF files.
        embedding_model (Embeddings): The embedding model to use.
        index_path (str): The path to save the FAISS index to.
    """
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    documents = []
    for pdf_file in pdf_files:
        loader = UnstructuredFileLoader(os.path.join(pdf_directory, pdf_file))
        documents.extend(loader.load())

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    vector_store = FAISS.from_documents(docs, embedding_model)
    vector_store.save_local(index_path)
    print(f"Vector store created and saved to {index_path}")
