"""HTTP errors raised by the bookmark service."""

from fastapi import HTTPException, status

class BookmarkNotFoundError(HTTPException):
    """404: the user has not bookmarked this recipe."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )