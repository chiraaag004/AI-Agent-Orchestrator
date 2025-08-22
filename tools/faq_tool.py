import os
from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class FAQInput(BaseModel):
    """Input for the FAQ tool."""
    query: str = Field(description="The user's question to search for in the FAQ knowledge base.")

def _create_faq_retriever():
    """Creates a retriever for the FAQ knowledge base."""
    # For production, you would initialize this once and reuse it.
    # For this example, we create it on the fly.
    faq_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.md')
    loader = UnstructuredMarkdownLoader(faq_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(docs, embeddings)
    
    return vector_store.as_retriever(search_kwargs={"k": 2})

faq_retriever = _create_faq_retriever()

@tool(args_schema=FAQInput)
def faq_tool(query: str) -> str:
    """
    Use this tool to answer general questions about policies, services, or how to use the assistant.
    It searches a knowledge base of frequently asked questions.
    """
    docs = faq_retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])