from langchain.memory import VectorStoreRetrieverMemory
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
from langchain.embeddings.base import Embeddings
import faiss

def create_long_term_memory(embedding_model: Embeddings):
    """
    Creates a long-term memory instance using an in-memory FAISS vector store.

    This memory can store important facts from the conversation and retrieve them
    based on semantic similarity to the current input. This allows the agent to
    remember details across a conversation beyond a simple sliding window.

    Args:
        embedding_model: An initialized LangChain embedding model instance 
                         (e.g., OpenAIEmbeddings, GoogleGenerativeAIEmbeddings).

    Returns:
        An instance of VectorStoreRetrieverMemory.
    """
    # Determine the embedding dimension by embedding a dummy text
    try:
        embedding_size = len(embedding_model.embed_query("test"))
    except Exception as e:
        raise ValueError(f"Could not determine embedding size from the provided model. Error: {e}")

    # Initialize an in-memory FAISS index
    index = faiss.IndexFlatL2(embedding_size)
    
    # Initialize a LangChain vector store with an in-memory docstore
    # This setup is session-specific and will not persist after the app restarts.
    # For persistence, you would replace FAISS with a persistent vector DB like ChromaDB, PGVector, etc.
    vectorstore = FAISS(embedding_model, index, InMemoryDocstore({}), {})
    
    # Initialize the retriever. 'k=1' means it will retrieve the single most relevant document.
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
    
    # The VectorStoreRetrieverMemory object that can be added to an agent chain.
    memory = VectorStoreRetrieverMemory(retriever=retriever)
    
    # Example of how to use it within your agent logic:
    # memory.save_context({"input": "My favorite destination is Paris"}, {"output": "Got it, you like Paris."})
    
    return memory