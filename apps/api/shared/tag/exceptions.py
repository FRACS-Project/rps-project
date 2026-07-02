##############################################################################################################
#
# Tag Exceptions
#
# HTTPException subclasses used by the Tag service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status

class DuplicateTagNameError(HTTPException):
    """Raised when a tag name is already in use."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag name already exists"
        )

class TagNotFoundError(HTTPException):
    """Raised when a tag lookup fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )