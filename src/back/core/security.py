##############################################################################################################
#
# Security and authentication utilities for the application.
#
# This module provides core security functionalities including:
# - Password hashing and verification
# - JWT token generation and validation
# - User authentication and authorization
# - Admin privilege checking
#
##############################################################################################################

from ..user import User
import bcrypt
from passlib.context import CryptContext

from dataclasses import dataclass

from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session

from ..auth.token import TokenData
from ..db import get_session

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Fix bcrypt warning
@dataclass
class SolveBugBcryptWarning:
    """Workaround class to fix bcrypt warning about missing __about__ attribute.
    
    This dataclass provides a mock __about__ attribute to suppress warnings
    from the bcrypt library that expects this attribute to be present.
    
    Attributes:
        __version__ (str): The bcrypt library version string.
    """
    __version__: str = getattr(bcrypt, "__version__")


setattr(bcrypt, "__about__", SolveBugBcryptWarning())

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (alias for hash_password).

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a new JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta | None, optional): Token expiration time. 
            Defaults to 15 minutes if None.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
):
    """Get the current authenticated user from a JWT token.

    Args:
        token (str): The JWT token from the request.
        db (Session): The database session.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    from ..user.crud import UserCrud
    crud = UserCrud(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(email=token_data.username)  # type: ignore
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current user and verify that their account is active.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The current active user.

    Raises:
        HTTPException: If the user account is disabled.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """Get the current user and verify that they have admin privileges.

    Args:
        current_user (User): The current authenticated and active user.

    Returns:
        User: The current admin user.

    Raises:
        HTTPException: If the user doesn't have admin privileges.
    """
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have enough privileges"
        )
    return current_user
