# src/state.py
from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages
import operator

class GraphState(TypedDict):
    """
    The state object for our Time & Lifestyle Agent.
    It tracks the conversational memory and the data gathered by tools.
    """
    
    # Annotated[List, add_messages] tells LangGraph to APPEND new user/AI 
    # messages to this list, rather than overwriting it every turn.
    messages: Annotated[List, add_messages]
    
    # Stores the raw text pulled from your local markdown files (RAG)
    rag_context: str
    
    # Stores the text pulled from the Tavily internet search
    search_data: str

    sources: Annotated[List[str], operator.add]