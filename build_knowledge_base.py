import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.document_loader import create_vector_store_from_pdfs

# Define paths
PDF_DIRECTORY = "pdf_data"
INDEX_PATH = "faiss_index"

def main():
    """
    Builds the knowledge base from PDF documents.
    """
    # Initialize the embedding model
    print("Initializing embedding model...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Embedding model initialized.")

    # Create the vector store
    print("Creating vector store from PDFs...")
    create_vector_store_from_pdfs(PDF_DIRECTORY, embedding_model, INDEX_PATH)
    print("Knowledge base built successfully.")

if __name__ == "__main__":
    main()
