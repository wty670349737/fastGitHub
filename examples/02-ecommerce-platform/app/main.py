"""PyShop 电商平台入口。

启动：
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import admin, api, auth, cart, orders, products
from .seed import seed_all

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_all()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="PyShop 电商平台", version="1.0.0", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.middleware("http")
    async def csrf_cookie_middleware(request: Request, call_next):
        token = request.cookies.get("csrf_token")
        need_cookie = token is None
        if token is None:
            token = secrets.token_urlsafe(32)
        request.state.csrf_token = token
        response = await call_next(request)
        if need_cookie:
            response.set_cookie(
                "csrf_token", token, httponly=True, samesite="lax"
            )
        return response

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    app.include_router(admin.router)
    app.include_router(api.router)
    return app


app = create_app()
