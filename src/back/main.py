##############################################################################################################
#
# FastAPI application entry point and configuration.
#
# This module sets up the FastAPI application, including router configuration,
# static file serving, database initialization, and path management for both
# backend and frontend components.
# 
##############################################################################################################

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .db import create_db_and_tables
from contextlib import asynccontextmanager
from .routes import all_routers
import os

# raise Exception("test de reload hahaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

# Racine du projet : on remonte depuis ce fichier jusqu'au dossier contenant "src"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Remonter d'un niveau pour arriver à la racine du projet (si ton script est dans src/acs)
# BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
BASE_DIR = os.path.abspath("/app")
# raise Exception(IMAGE_DIR)

# Dossier src
SRC_DIR = os.path.join(BASE_DIR, "src")

# Dossier de ton package Python (acs)
BACKEND_DIR = os.path.join(SRC_DIR, "back")

# Dossier frontend
FRONTEND_DIR = os.path.join(SRC_DIR, "front")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

for router in all_routers:
    app.include_router(router)

# Monter le dossier frontend en /static
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="front")


# Servir index.html à la racine
@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)