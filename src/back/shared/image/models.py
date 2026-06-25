##############################################################################################################
#
# Database models for image management.
#
# This module defines the SQLModel classes for image data persistence,
# including base image information and the complete image model.
#
##############################################################################################################

import uuid
from typing import TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


if TYPE_CHECKING:
    from ...user import User
    from ...recipe import Recipe


class ImageStatus(str, Enum):
    PENDING = "pending"
    FINISHING = "finishing"
    ACTIVE = "active"


# class ImageBase(SQLModel):
#     """Base model for image information.

#     Attributes:
#         name (str): The image name.
#         uri (str): The local path to the image.
#     """
#     name: str
#     uri: str


class Image(SQLModel, table=True):
    """Complete image model for database storage.

    Extends ImageBase to include a unique identifier.

    Attributes:
        id (UUID): Unique identifier for the image.
        name (str): The image name.
        uri (str): The local path to the image.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    date_created: datetime = Field(
        default_factory=datetime.now, nullable=False
    )

    owner: "User" = Relationship(back_populates="images")
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    recipe_id: uuid.UUID | None = Field(foreign_key="recipe.id", default=None, ondelete="CASCADE")
    recipe: "Recipe" = Relationship(back_populates="images")
