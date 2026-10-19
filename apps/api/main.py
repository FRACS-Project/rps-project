"""FastAPI application entry point.

Creates the app, creates the database tables on startup and registers
every router from `routes.all_routers`.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .db import create_db_and_tables
from contextlib import asynccontextmanager
from .routes import all_routers
import os

from .core.path import FRONTEND_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the database tables when the app starts."""
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

for router in all_routers:
    app.include_router(router)

# # Monter le dossier frontend en /static
# app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="front")


# # Servir index.html à la racine
# @app.get("/")
# def root():
#     index_path = FRONTEND_DIR / "index.html"
#     return FileResponse(index_path)
