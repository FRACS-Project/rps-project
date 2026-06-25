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


class ImagePublic(BaseModel):
    """Schema for publicly viewable image data.

    Attributes:
        id (UUID): The image's unique identifier.
        name (str): The image name.
        uri (str): The local path to the image.
        data_base64 (str): The image in base64 encode for json payload
    """
    id: uuid.UUID


class ImageCreate(BaseModel):
    """Schema for creating a new Image.

    Attributes:
        name (str): The image name.
        uri (str): The local path to the image.
    """
    id: uuid.UUID | None = None
    name: str
    data_base64: str


class ImageUpdate(BaseModel):
    """Schema for updating image data.

    All fields are optional to allow partial updates.

    Attributes:
        name (str, optional): The updated imagename.
        uri (str): The local path to the image.
    """
    data_based64: str | None = None

class ImageRecipeCreate(BaseModel):
    owner_id: uuid.UUID
    recipe_id: uuid.UUID