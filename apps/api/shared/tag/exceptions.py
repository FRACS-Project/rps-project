"""HTTP errors raised by the tag service."""

from fastapi import HTTPException, status

class DuplicateTagNameError(HTTPException):
    """409: a tag with this name already exists."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag name already exists"
        )

class TagNotFoundError(HTTPException):
    """404: no tag has this ID or name."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )