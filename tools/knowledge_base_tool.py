import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.tools import tool

INDEX_PATH = "faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Add allow_dangerous_deserialization=True
vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever()

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the knowledge base for information related to the user's query.
    The knowledge base contains information from hotel documents such as the hotel booklet,
    spa menu, bar menu, and more. Use this tool to answer questions about hotel amenities,
    services, and policies.
    """
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])
