import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .db import engine
from .models import Base
from .api.objects import router as objects_router

app = FastAPI(title="Secure Drive")

# Create tables (minimal approach; later switch to Alembic migrations).
Base.metadata.create_all(bind=engine)

# Dev CORS (React/Vite on :5173 -> API on :8000). You can tighten later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(objects_router, prefix="/api")  # include_router is the standard pattern.

# Optional: Serve built React app from FastAPI (prod-ish mode).
# Build React into: frontend/dist
# Then set SERVE_FRONTEND=1 and FRONTEND_DIST=../frontend/dist (or absolute path).
if os.environ.get("SERVE_FRONTEND", "0") == "1":
    dist_dir = os.environ.get("FRONTEND_DIST", "")
    if dist_dir:
        dist_path = Path(dist_dir).resolve()
        if dist_path.exists():
            # Mount static assets; FastAPI supports StaticFiles mounting.
            app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")
