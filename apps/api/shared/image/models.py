"""Image table model.

Image files live on disk in `UPLOADS_DIR`, named by image ID; the table
only holds metadata.
"""

import uuid
from typing import TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timedelta, timezone


if TYPE_CHECKING:
    from ...user import User
    from ...recipe import Recipe


class ImageStatus(str, Enum):
    """Lifecycle of an image.

    PENDING: the row exists but the file is not saved yet, or the image was
        removed from its recipe. Pending images are deleted after the recipe
        is saved.
    ACTIVE: the file is saved and the image is shown.
    """
    PENDING = "pending"
    ACTIVE = "active"


class ImageBase(SQLModel):
    """Fields shared by the image table and its schemas.

    Attributes:
        status: Pending or active.
        is_primary: Whether this is the recipe's main image.
    """

    status: ImageStatus | None = Field(default=ImageStatus.PENDING)
    is_primary: bool | None = Field(default=False)


class Image(ImageBase, table=True):
    """Image table. Deleted with its owner or its recipe.

    Attributes:
        id: Primary key, also the file name on disk.
        date_created: Creation time (UTC); orders a recipe's images.
        pending_date: One hour after creation. Not used yet.
        owner_id: ID of the user who uploaded it.
        owner: The user who uploaded it.
        recipe_id: ID of the recipe, if it belongs to one.
        recipe: The recipe it belongs to.
    """

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
