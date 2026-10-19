"""User table model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, VARCHAR, Column

if TYPE_CHECKING:
    from ..recipe import Recipe
    from ..shared import Bookmark, Image


class UserBase(SQLModel):
    """Fields shared by the user table and its schemas.

    Attributes:
        name: Unique username.
        mail: Unique email, stored in the `email` column.
        admin: Whether the user can use admin endpoints.
        disabled: Whether the account is blocked from logging in.
    """
    name: str
    mail: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))
    admin: bool | None = False
    disabled: bool | None = False


class User(UserBase, table=True):
    """User table.

    Deleting a user also deletes their recipes and images.

    Attributes:
        id: Primary key.
        hashed_password: Bcrypt hash; the plain password is never stored.
        date_created: Creation time (UTC).
        recipes: Recipes owned by the user.
        images: Images uploaded by the user.
        bookmarks: Recipes the user bookmarked.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    recipes: list["Recipe"] = Relationship(back_populates="owner", cascade_delete=True)
    images: list["Image"] = Relationship(back_populates="owner", cascade_delete=True)
    bookmarks: list["Bookmark"] = Relationship()
