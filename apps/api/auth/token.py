"""Pydantic schemas for JWT access tokens."""

from pydantic import BaseModel


class Token(BaseModel):
    """Login response body.

    Attributes:
        access_token: Signed JWT.
        token_type: Always "bearer".
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Claims read back from a decoded JWT.

    Attributes:
        username: The `sub` claim, which holds the user's email.
    """
    username: str | None = None