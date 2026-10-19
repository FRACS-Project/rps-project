"""HTTP errors raised by the image service."""

from fastapi import HTTPException, status


class DuplicateImageError(HTTPException):
    """409: the image was already uploaded. Not raised anywhere yet."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Image already uploaded"
        )


class ImageNotFoundError(HTTPException):
    """404: no image has this ID, or the recipe has no primary image."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

class WrongImageType(HTTPException):
    """415: the file is not a JPEG, PNG or WebP image, or is not valid base64."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Image is not within the accepted media type (image/jpeg, image/png, image/webp)"
        )