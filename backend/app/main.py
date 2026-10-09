from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import init_db
from app.db.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_if_empty()
    yield


# Regex that matches any Azure Static Web Apps host (production + preview slots
# + future regions). Keeps CORS working without editing env vars on every
# SWA redeploy.
_AZURE_SWA_REGEX = r"^https://[a-z0-9-]+\.[a-z0-9]+\.azurestaticapps\.net$"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="E-STATE API", version="0.1.0", lifespan=lifespan)

    origins = list(settings.allowed_origins)
    for dev in ("http://localhost:5173", "http://127.0.0.1:5173"):
        if dev not in origins:
            origins.append(dev)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=_AZURE_SWA_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    from app.api import chat, properties, session
    app.include_router(properties.router, prefix="/api")
    app.include_router(session.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
