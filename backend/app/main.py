import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.files import router as files_router
from .api.auth import router as auth_router
from .database import create_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()
    yield
    await app.state.pool.close()


app = FastAPI(title="Secure Drive", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")

if os.environ.get("SERVE_FRONTEND", "0") == "1":
    dist_dir = os.environ.get("FRONTEND_DIST", "")
    if dist_dir:
        dist_path = Path(dist_dir).resolve()
        if dist_path.exists():
            app.mount(
                "/", StaticFiles(directory=str(dist_path), html=True), name="frontend"
            )
else:
    frontend_port = os.environ.get("FRONTEND_PORT")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:" + str(frontend_port),
            "http://127.0.0.1:" + str(frontend_port),
            os.environ.get("BASE_URL", ""),
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    pass
