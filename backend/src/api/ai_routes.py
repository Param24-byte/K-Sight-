from fastapi import APIRouter
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.services.ai.llm_client import llm_client

router = APIRouter()

class AIQuery(BaseModel):
    query: str

@router.post("/ai/ask")
def ask_assistant(payload: AIQuery):
    """Hybrid RAG endpoint that generates intelligence from Graph and Vector DBs"""
    try:
        response = llm_client.ask(payload.query)
        return response
    except Exception as e:
        return {"error": str(e), "message": "Failed to process AI request."}
