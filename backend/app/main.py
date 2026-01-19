import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .db import engine
from .models import Base
from .api.objects import objects_router

app = FastAPI(title="Secure Drive")

Base.metadata.create_all(bind=engine)

app.include_router(objects_router, prefix="/api")

if os.environ.get("SERVE_FRONTEND", "0") == "1":
    dist_dir = os.environ.get("FRONTEND_DIST", "")
    if dist_dir:
        dist_path = Path(dist_dir).resolve()
        if dist_path.exists():
            app.mount(
                "/", StaticFiles(directory=str(dist_path), html=True), name="frontend"
            )
else:
    frontend_port = os.environ.get("FRONTEND_PORT", 5173)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:" + str(frontend_port),
            "http://127.0.0.1:" + str(frontend_port),
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
