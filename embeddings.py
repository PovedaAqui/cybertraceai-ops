from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from typing import Dict, Any

def setup_vector_store(tool_registry: Dict[str, Any]) -> InMemoryVectorStore:
    """
    Sets up an in-memory vector store using Ollama embeddings for tool lookup.
    
    Args:
        tool_registry: Dictionary mapping tool IDs to tool objects
        
    Returns:
        InMemoryVectorStore: Vector store containing tool embeddings
    """
    # Initialize Ollama embeddings with supported parameters
    ollama_embeddings = OllamaEmbeddings(
        model="nomic-embed-text:latest"
    )

    # Create document objects for each tool
    tool_documents = [
        Document(
            page_content=f"{tool.description} Command: {tool.name}",
            id=id,
            metadata={
                "tool_name": tool.name,
                "command": tool.name.replace("_", " ")
            }
        )
        for id, tool in tool_registry.items()
    ]

    # Initialize and populate vector store
    vector_store = InMemoryVectorStore(embedding=ollama_embeddings)
    document_ids = vector_store.add_documents(tool_documents)
    
    return vector_store

def search_similar_tools(vector_store: InMemoryVectorStore, query: str, k: int = 3):
    """
    Search for tools similar to the query.
    
    Args:
        vector_store: The vector store containing tool embeddings
        query: Search query string
        k: Number of similar results to return (default: 3)
        
    Returns:
        List of similar documents with scores
    """
    return vector_store.similarity_search_with_score(query, k=k) 