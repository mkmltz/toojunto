from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models  # noqa: F401
from .auth.router import router as auth_router
from .groups.router import router as groups_router
from .invites.router import router as invites_router

app = FastAPI(title="TooJunto API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
app.include_router(groups_router)
app.include_router(invites_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "toojunto-api", "version": "0.1.0"}

@app.get("/health/db")
def health_db():
    from .db import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
