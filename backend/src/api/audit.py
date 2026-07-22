from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.db.database import SessionLocal
from src.services.db.models import AuditLog
from jose import jwt
import logging

logger = logging.getLogger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only log actual API calls, skipping standard routes or preflight
        if request.url.path.startswith("/api/v1") and request.method != "OPTIONS":
            user_id = None
            # Extract Bearer token to figure out who is calling
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, "HACKATHON_SUPER_SECRET_KEY", algorithms=["HS256"])
                    user_id = payload.get("sub") # In our mock setup, sub is the username
                except Exception:
                    pass
            
            # Log the action to DB
            db = SessionLocal()
            try:
                log_entry = AuditLog(
                    user_id=1 if user_id else 0, # Hack for demo, store as integer or just ID
                    action=request.method,
                    endpoint=request.url.path
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.error(f"Audit log failed: {e}")
            finally:
                db.close()
                
        response = await call_next(request)
        return response
