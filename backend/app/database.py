from __future__ import annotations
from collections.abc import AsyncGenerator
import os
import asyncpg
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_APP_ROLE"],
        password=os.environ["POSTGRES_APP_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        min_size=int(os.environ.get("POSTGRES_POOL_MIN_SIZE", "5")),
        max_size=int(os.environ.get("POSTGRES_POOL_MAX_SIZE", "20")),
    )


async def get_db(request: Request) -> AsyncGenerator[asyncpg.Connection, None]:
    async with request.app.state.pool.acquire() as conn:
        yield conn


async def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> AsyncGenerator[str, None]:
    token = credentials.credentials  # the raw token, "Bearer" already stripped
    # validate token, fetch user, etc.
    yield token
