from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


def setup_cors(app: FastAPI) -> None:
    debug = os.getenv("DEBUG", "false").lower() == "true"

    if debug:
        origins = [
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:3000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
            "https://localhost",
            "https://localhost:8080",
            "https://localhost:3000",
        ]
    else:
        origins = [
            "https://our-domain.com",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
