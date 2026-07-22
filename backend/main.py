from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.api.routes import router as api_router
from src.api.ai_routes import router as ai_router
from src.api.auth import router as auth_router
from src.api.audit import AuditMiddleware
from src.services.db.database import engine, Base

# Initialize the database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crime Intelligence & Investigation Platform API",
    description="Backend services for Data Ingestion, Graph Analytics, and LLM orchestration with RBAC.",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Logging Middleware
app.add_middleware(AuditMiddleware)

# Include Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(api_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Intelligence Engine API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
