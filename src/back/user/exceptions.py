##############################################################################################################
#
# Authentication Exceptions
#
# HTTPException subclasses used by the auth service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status


class DuplicateEmailError(HTTPException):
    """Raised when an email address is already in use."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )


class DuplicateUsernameError(HTTPException):
    """Raised when a username is already in use."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )


class InvalidCredentialsError(HTTPException):
    """Raised when credentials fail validation."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


class UserNotFoundError(HTTPException):
    """Raised when a user lookup fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class UserDisabledError(HTTPException):
    """Raised when an account is disabled or inactive."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )