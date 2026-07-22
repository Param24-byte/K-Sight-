from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.api.routes import router as api_router
from src.api.ai_routes import router as ai_router

app = FastAPI(
    title="Crime Intelligence & Investigation Platform API",
    description="Backend services for Data Ingestion, Graph Analytics, and LLM orchestration.",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Intelligence Engine API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
