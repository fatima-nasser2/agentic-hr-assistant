from typing import TypedDict, List, Optional
from langchain_core.documents import Document

class GraphState(TypedDict):
    question: str                      # Original user question
    rewritten_question: str            # Rewritten for better retrieval
    documents: List[Document]          # Retrieved chunks
    generation: str                    # Final answer
    retrieval_attempts: int            # Track retries
    relevance: str                     # "relevant" or "not_relevant"
    route: str                         # "rag" or "unknown"