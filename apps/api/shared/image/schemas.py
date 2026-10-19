"""Request and response schemas for images. Image data travels as base64 strings."""

import uuid

from . import ImageBase
from .models import ImageStatus


class ImagePublic(ImageBase):
    """Image returned by the API.

    Attributes:
        id: The image's ID.
        data_base64: File content as base64.
    """
    id: uuid.UUID
    data_base64: str | None = None


class ImageCreate(ImageBase):
    """Image fields used to insert a row.

    Attributes:
        owner_id: ID of the uploader.
        recipe_id: ID of the recipe.
    """
    owner_id: uuid.UUID
    recipe_id: uuid.UUID


class ImageUpdate(ImageBase):
    """Partial update of an image's status or primary flag."""
    status: ImageStatus | None = None
    is_primary: bool | None = None


class ImagePayload(ImageBase):
    """One image in the `NewRecipe` / `PatchRecipe` body.

    Send `id` to keep an existing image, or `new=True` and `data_base64` to
    upload one.

    Attributes:
        id: ID of an existing image.
        data_base64: File content as base64, for new images.
        new: True to upload this image.
    """
    id: uuid.UUID | None = None
    data_base64: str | None = None
    new: bool | None = False
