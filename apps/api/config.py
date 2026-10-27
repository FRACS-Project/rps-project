"""Settings read from environment variables.

`SECRET_KEY` signs the JWT tokens; generate one with `openssl rand -hex 32`.
"""

import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"]
    debug: bool = False
    secret_key: str
    algorithm: Literal["HS256"]
    access_token_expire_minutes: int
    database_url: str


settings = Settings()