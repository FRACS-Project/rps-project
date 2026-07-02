##############################################################################################################
#
# Pydantic schemas for image data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning image data through the API endpoints.
#
##############################################################################################################

import uuid

from . import ImageBase
from .models import ImageStatus


class ImagePublic(ImageBase):
    id: uuid.UUID
    data_base64: str | None = None


class ImageCreate(ImageBase):
    owner_id: uuid.UUID
    recipe_id: uuid.UUID


class ImageUpdate(ImageBase):
    status: ImageStatus | None = None
    is_primary: bool | None = None


class ImagePayload(ImageBase):
    id: uuid.UUID | None = None
    data_base64: str
    new: bool | None = False
