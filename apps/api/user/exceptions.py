"""HTTP errors raised by the user and auth services."""

from fastapi import HTTPException, status


class DuplicateEmailError(HTTPException):
    """409: the email is already used by another account."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )


class DuplicateUsernameError(HTTPException):
    """409: the username is already taken."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )


class InvalidCredentialsError(HTTPException):
    """401: unknown user or wrong password."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


class UserNotFoundError(HTTPException):
    """404: no user has this ID."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class UserDisabledError(HTTPException):
    """403: the account is disabled."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )