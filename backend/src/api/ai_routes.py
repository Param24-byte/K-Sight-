from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.services.ai.llm_client import llm_client
from src.api.auth import get_current_user
from src.services.db.models import User

router = APIRouter()

class AIQuery(BaseModel):
    query: str
    language: str = "English"
    history: list = []

@router.post("/ai/ask")
def ask_assistant(payload: AIQuery, current_user: User = Depends(get_current_user)):
    """Hybrid RAG endpoint that generates intelligence from Graph and Vector DBs"""
    try:
        response = llm_client.ask(payload.query, payload.language, payload.history)
        return response
    except Exception as e:
        return {"error": str(e), "message": "Failed to process AI request."}
