##############################################################################################################
#
# Pydantic schemas for image data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning image data through the API endpoints.
#
##############################################################################################################

import re
import uuid

from pydantic import BaseModel

from . import ImageBase
from .models import ImageStatus


class ImagePublic(ImageBase):
    """Schema for publicly viewable image data.

    Attributes:
        id (UUID): The image's unique identifier.
    """
    id: uuid.UUID


class ImageCreate(ImageBase):
    """Schema for creating a new Image.

    Attributes:
        name (str): The image name.
        uri (str): The local path to the image.
    """
    id: uuid.UUID | None = None
    name: str
    data_base64: str


class ImageUpdate(ImageBase):
    """Schema for updating image data.

    All fields are optional to allow partial updates.

    Attributes:
        name (str, optional): The updated imagename.
        uri (str): The local path to the image.
    """
    data_based64: str | None = None

class ImageRecipeCreate(BaseModel):
    status: ImageStatus | None = None
    owner_id: uuid.UUID
    recipe_id: uuid.UUID