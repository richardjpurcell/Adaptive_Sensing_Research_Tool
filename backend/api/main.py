from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import manifests as manifests_router
from api.routers import preview as preview_router
from api.routers import runs as runs_router

def create_app() -> FastAPI:
    app = FastAPI(title="AWSRT API", version="0.1.0")
    # CORS (dev-friendly)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
    # Routers
    app.include_router(manifests_router.router, prefix="/manifests", tags=["manifests"])
    app.include_router(preview_router.router,   prefix="/preview",   tags=["preview"])
    app.include_router(runs_router.router,      prefix="/runs",      tags=["runs"])
    return app

app = create_app()
