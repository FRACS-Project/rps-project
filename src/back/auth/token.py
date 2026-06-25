##############################################################################################################
#
# Pydantic schemas for authentication tokens.
#
# This module defines the data models used for JWT token handling in the
# authentication system.
#
##############################################################################################################

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token response.
    
    Attributes:
        access_token (str): The JWT token string.
        token_type (str): The type of token (usually "bearer").
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for JWT token payload data.
    
    Attributes:
        username (str | None): The username stored in the token. Defaults to None.
    """
    username: str | None = None