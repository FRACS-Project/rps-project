##############################################################################################################
#
# Authentication Exceptions
#
# HTTPException subclasses used by the auth service layer for consistent API errors.
#
##############################################################################################################

from fastapi import HTTPException, status


class DuplicateImageError(HTTPException):
    """Raised when an image is already uploaded."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Image already uploaded"
        )


class ImageNotFoundError(HTTPException):
    """Raised when an image lookup fails."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

class WrongImageType(HTTPException):
    """Raised when an image is not image/png, image/jpeg or image/webp"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Image is not within the accepted media type (image/jpeg, image/png, image/webp)"
        )