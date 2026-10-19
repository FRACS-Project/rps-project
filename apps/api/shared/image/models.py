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
from datetime import datetime, timedelta, timezone


if TYPE_CHECKING:
    from ...user import User
    from ...recipe import Recipe


class ImageStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"


class ImageBase(SQLModel):

    status: ImageStatus | None = Field(default=ImageStatus.PENDING)
    is_primary: bool | None = Field(default=False)


class Image(ImageBase, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    date_created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    pending_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1),
        nullable=True
    )

    owner: "User" = Relationship(back_populates="images")
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    recipe_id: uuid.UUID | None = Field(foreign_key="recipe.id", default=None, ondelete="CASCADE")
    recipe: "Recipe" = Relationship(back_populates="images")
