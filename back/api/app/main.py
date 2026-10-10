from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.categories.router import router as categories_router
from app.core.config import settings
from app.transactions.router import router as transactions_router
from app.wallets.router import router as wallets_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(categories_router)
    app.include_router(wallets_router)
    app.include_router(transactions_router)

    @app.get("/")
    def hello() -> dict[str, str]:
        return {"message": "Hola Mundo"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
