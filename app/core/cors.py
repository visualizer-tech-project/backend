from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings


def setup_cors(app: FastAPI) -> None:
    origins = (
        settings.cors.debug_origins
        if settings.debug
        else settings.cors.production_origins
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        allow_headers=['Authorization', 'Content-Type', 'X-Requested-With'],
    )
