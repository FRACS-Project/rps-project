"""Authentication and authorization.

Provides bcrypt password hashing, JWT access token creation, and the
FastAPI dependencies that resolve the current user from the bearer token
(`get_current_user`, `get_current_active_user`, `get_current_admin_user`).
"""

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

from ..config import settings

# Fix bcrypt warning
@dataclass
class SolveBugBcryptWarning:
    """Expose bcrypt's version under `__about__` for passlib.

    Recent bcrypt releases removed `bcrypt.__about__`, which passlib reads and
    warns about. Setting this object as `bcrypt.__about__` silences the warning.
    """
    __version__: str = getattr(bcrypt, "__version__")


setattr(bcrypt, "__about__", SolveBugBcryptWarning())

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt.

    Args:
        password: Plain text password.

    Returns:
        The bcrypt hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against a bcrypt hash.

    Args:
        plain_password: Password entered by the user.
        hashed_password: Stored bcrypt hash.

    Returns:
        True if the password matches the hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt. Same as `hash_password`.

    Args:
        password: Plain text password.

    Returns:
        The bcrypt hash.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a signed JWT access token.

    Args:
        data: Claims to encode; `sub` should hold the user's email.
        expires_delta: Token lifetime. Defaults to
            `ACCESS_TOKEN_EXPIRE_MINUTES` from the config.

    Returns:
        The encoded JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = (
            datetime.now(timezone.utc) 
            + timedelta(minutes=settings.access_token_expire_minutes)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
):
    """FastAPI dependency: resolve the user from the bearer token.

    Args:
        token: JWT from the `Authorization` header.
        db: Database session.

    Returns:
        The user whose email is in the token's `sub` claim.

    Raises:
        HTTPException: 401 if the token is invalid or the user does not exist.
    """
    from ..user.crud import UserCrud
    crud = UserCrud(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
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
    """FastAPI dependency: the current user, if their account is enabled.

    Args:
        current_user: User resolved from the token.

    Returns:
        The current user.

    Raises:
        HTTPException: 400 if the account is disabled.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """FastAPI dependency: the current user, if they are an admin.

    Args:
        current_user: Active user resolved from the token.

    Returns:
        The current user.

    Raises:
        HTTPException: 403 if the user is not an admin.
    """
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have enough privileges"
        )
    return current_user
