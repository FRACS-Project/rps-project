"""Settings read from environment variables.

`SECRET_KEY` signs the JWT tokens; generate one with `openssl rand -hex 32`.
"""

import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

DATABASE_URL = os.getenv("DATABASE_URL")