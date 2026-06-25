##############################################################################################################
#
# Recipe Exceptions
#
# HTTPException subclasses used by the recipe service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status

class BookmarkNotFoundError(HTTPException):
    """Raised when a recipe lookup fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )