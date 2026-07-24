# main.py
import os
from dotenv import load_dotenv
from src.graph import app
from langchain_core.messages import HumanMessage
import sys
# Load API keys from your local secret stash (.env file)
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI()

# Enable CORS for local React development
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user : str
class ChatResponse(BaseModel):
    final_message: str
    sources: list[str]

@api.post("/life-advisor", response_model=ChatResponse)
def run_life_advisor(request: ChatRequest):
    print("[API] Initializing Time & Lifestyle Agent...")
    
    # Simulate an everyday human struggling with modern life constraints
    initial_struggle = (
        request.user
    )
    
    # Initialize your LangGraph starting state payload
    initial_state = {
        "messages": [HumanMessage(content=request.user)],
        "rag_context": "",
        "search_data": ""
    }
    
    final_output = app.invoke(initial_state)
    
    # Extract and display the final, compassionate, structured answer from Groq
    final_message = final_output["messages"][-1].content

    for chunk, metadata in app.stream(initial_state, stream_mode="messages"):
        if metadata.get("langgraph_node") == "groq_generator":
            try:
                sys.stdout.write(chunk.content)
                sys.stdout.flush()
            except Exception:
                try:
                    sys.stdout.write(chunk.content.encode('ascii', errors='replace').decode('ascii'))
                    sys.stdout.flush()
                except Exception:
                    pass
            
    # --- METADATA DISPLAY BLOCK ---
    
    sources = final_output.get("sources", [])
    if sources:
        for idx, source in enumerate(set(sources), 1): # set() avoids printing duplicates
            try:
                print(f" {idx}. {source}")
            except Exception:
                pass
    return ChatResponse(
    final_message=final_message,
    sources=list(set(sources))
    )

