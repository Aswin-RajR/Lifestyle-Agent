from langgraph.graph import START, END, StateGraph
from src.state import GraphState
from src.nodes import rag_retrieval_chain, web_search_node, generator_node


builder = StateGraph(GraphState)

builder.add_node(
    "rag_retriever",rag_retrieval_chain)
builder.add_node("web_searcher", web_search_node)
builder.add_node("groq_generator", generator_node)

builder.add_edge(START, "rag_retriever")
builder.add_edge("rag_retriever","web_searcher")
builder.add_edge("web_searcher","groq_generator")
builder.add_edge("groq_generator", END)

app = builder.compile()