"""Auth endpoints under `/auth`.

- `login_router`: log in (OAuth2 form or JSON) and read the current user.
- `register_router`: public signup.

Credential checks live in `UserService`.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from . import (
    Token
)

from ..user.schemas import UserCreate, UserPublic
from ..user.services import UserService
from ..core import get_current_active_user
from ..db import get_session

# ── Login ──────────────────────────────────────────────────────────────────────────────

login_router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    """JSON body for `/auth/login-json`.

    Attributes:
        mail: The user's email or username.
        password: Plain text password.
    """
    mail: str
    password: str


@login_router.post("/login-json", response_model=Token)
def login_json(
    request: LoginRequest,
    db: Session = Depends(get_session)
):
    """Log in with a JSON body and get an access token.

    Accepts an email or a username in `mail`.

    Raises:
        InvalidCredentialsError: 401 if the user does not exist or the password is wrong.
        UserDisabledError: 403 if the account is disabled.
    """
    service = UserService(db)
    return service.authenticate_and_create_token(request.mail, request.password)


@login_router.get("/me-json", response_model=UserPublic)
def get_current_user_json(current_user: UserPublic = Depends(get_current_active_user)):
    """Return the logged-in user. Same as `GET /auth/me`."""
    return current_user


@login_router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """Log in with an OAuth2 password form and get an access token.

    This is the endpoint Swagger's "Authorize" button uses. `username` may be
    an email or a username.

    Raises:
        InvalidCredentialsError: 401 if the user does not exist or the password is wrong.
        UserDisabledError: 403 if the account is disabled.
    """
    service = UserService(db)
    return service.authenticate_and_create_token(form_data.username, form_data.password)


@login_router.get("/me", response_model=UserPublic)
def get_current_user(current_user: UserPublic = Depends(get_current_active_user)):
    """Return the logged-in user."""
    return current_user


# ── Signup ─────────────────────────────────────────────────────────────────────────────


register_router = APIRouter(prefix="/auth", tags=["Auth"])


@register_router.post("/signup", response_model=UserPublic)
def signup(
    user: UserCreate,
    session: Session = Depends(get_session)
):
    """Create a user account.

    The password is hashed before it is stored.

    Raises:
        DuplicateEmailError: 409 if the email is already used.
        DuplicateUsernameError: 409 if the username is already taken.
    """
    service = UserService(session)
    return service.create_user(user)
