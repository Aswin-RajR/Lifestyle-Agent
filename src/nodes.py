import os

# 1. Solves USER_AGENT warning (identifies your app safely)
os.environ["USER_AGENT"] = "TimeAndLifestyleAgent/1.0 (Contact: myemail@example.com)"

# 2. Solves HF_TOKEN warning (Silences the notification completely)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1" 

# OPTIONAL: If you want to use an actual HF token for speed, use this instead:
# os.environ["HF_TOKEN"] = "your_actual_hf_token_here"

from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from src.state import GraphState
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

vectorstore = FAISS.load_local("vectorstores/my_faiss_index",embeddings=embeddings
                            ,allow_dangerous_deserialization=True)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

def rag_retrieval_chain(state: GraphState) -> GraphState:

    user_query = state["messages"][-1].content

    docs = retriever.invoke(user_query)

    metadata_sources = []
    for doc in docs:
        source_path = doc.metadata.get("source", "Unknown Local Source")
        metadata_sources.append(source_path)
    
    
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    # Return both the text context AND the metadata sources list
    return {
        "rag_context": context_text,
        "sources": metadata_sources
    }


from langchain_tavily import TavilySearch

def web_search_node(state: GraphState) -> GraphState:
    """Searches the web for information, then scrapes the content from the resulting URLs."""
    print("--- Calling Web Search Node ---")
    user_query = state["messages"][-1].content

    tavily_search = TavilySearch(
        max_results=2,
        search_depth="advanced",
    )
    try:
        # Crucial fix: We pass a dictionary with the 'query' key
        response = tavily_search.invoke({"query": user_query})
        
        # Pull out the actual list of results from the response dictionary
        search_results = response.get("results", [])
        web_urls = []

        scraped_contents = []
        for result in search_results:
            # Now 'result' is a true dictionary, so .get() works perfectly!
            content = result.get("content", "")
            url = result.get("url", "")
            title = result.get("title", "")
            scraped_contents.append(f"Source [{title}] ({url}): {content}")
            if url:
                web_urls.append(url) # 👈 Capture the live website URL
            
        combined_search_data = "\n\n".join(scraped_contents)
    except Exception as e:
        print(f"Error during web search: {e}")
        combined_search_data = "No real-time web search data found."

    return {
        "search_data": combined_search_data,
        "sources": web_urls  # 🌟 This will now APPEND to your RAG sources perfectly!
    }
def generator_node(state: GraphState) -> GraphState:

    user_query = state["messages"][-1].content
    context = state.get("rag_context", "No trusted internal guidelines found.")
    search_data = state.get("search_data", "No real-time web research found.")
    
    system_prompt = f"""
    You are AR, developed by Aswin Raj.

    You are a compassionate Life Alignment Coach who helps people improve:
    - Purpose
    - Family relationships
    - Financial health
    - Physical health
    - Time management
    - Habit building

    Use the following trusted internal knowledge:

    {context}

    Real-time research:

    {search_data}

    Guidelines:
    - Be empathetic and encouraging.
    - Validate the user's emotions when appropriate.
    - Give practical, actionable advice.
    - Prefer small, sustainable habits over drastic changes.
    - Use the RAG context whenever it is relevant.
    - If the context is insufficient, say so and then rely on general best practices.
    - Never invent facts.
    - Structure answers with headings and bullet points when helpful.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]

    response = llm.invoke(messages)

    return {
        "messages": [AIMessage(content=response.content)]
    }