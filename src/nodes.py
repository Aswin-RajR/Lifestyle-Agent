from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

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

def rag_retrieval_chain(query: str) -> str:


    template = """You are a compassionate, deeply insightful Life Alignment Coach. Your purpose is to help modern humans combat stress, overcome existential burnout, reclaim their time, and build intentional habits across four core pillars: Purpose, Family, Financial Health, and Physical Health.

    Use the following trusted wisdom guidelines and real-time research data to craft a balanced, life-changing response. Speak like a supportive, non-judgmental mentor—be highly practical, encouraging, and clear (avoid robotic or overly corporate language).

    Trusted Wisdom Guidelines (Internal RAG):
    {context}

    Real-Time Research / Context (Web Search Data if applicable):
    {search_data}

    Instructions:
    1. Always validate the user's feelings first if they sound overwhelmed or stressed.
    2. Provide an actionable, step-by-step recovery strategy using the metrics, rules, or philosophies found in the Trusted Wisdom section.
    3. Keep the advice incredibly realistic for an everyday person—do not suggest massive lifestyle overhauls all at once. Focus on small, immediate micro-habits.
    4. If the data provided doesn't directly address their exact specific question, lean on your core values of restoring human balance, family connection, and physical health, or transparently state what practical steps they should take next.

    User Question/Current Struggle: {input}
    Empathetic, Actionable Blueprint:"""

    prompt_template = PromptTemplate(
        input_variables=[
            "context",
            "search_data",
            "input"
        ],
        template=template
    )
    document_chain = create_stuff_documents_chain(llm, prompt_template)
    retrieval_chain = create_retrieval_chain(
        retriever,
        document_chain
    )

    result = retrieval_chain.invoke({
        "input": query,
        "search_data": ""
    })

    return result["answer"]
    # print("\nAnswer:")  
    # print(result["answer"])

    # print("\nSources:")
    # for doc in result["context"]:
    #     print("-", doc.metadata.get("source"))

# print(rag_retrieval_chain("I feel like I have no time for myself and my family. How can I reclaim my time and build better habits?"))

from langchain_tavily import TavilySearch

tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    include_domains=None,
    # exclude_domains=None
)
question = "I feel like I have no time for myself and my family. How can I reclaim my time and build better habits?"
search_results = tavily_search.invoke(question)
print("Search Results:", search_results)
for result in search_results.get("results", []):
    print(f"- {result.get('title')}: {result.get('url')}")