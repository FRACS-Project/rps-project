##############################################################################################################
#
# Database models for user management.
#
# This module defines the SQLModel classes for user data persistence,
# including base user information and the complete user model with authentication
# and relationship data.
#
##############################################################################################################

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, VARCHAR, Column

if TYPE_CHECKING:
    from ..recipe import Recipe
    from ..shared import Bookmark, Image


class UserBase(SQLModel):
    """Base model for user information.

    Attributes:
        name (str): The username.
        mail (EmailStr): The user's email address (unique).
        admin (bool, optional): Whether the user has admin privileges. Defaults to False.
        disabled (bool, optional): Whether the user account is disabled. Defaults to False.
    """
    name: str
    mail: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))
    admin: bool | None = False
    disabled: bool | None = False


class User(UserBase, table=True):
    """Complete user model for database storage.

    Extends UserBase to include:
    - Unique identifier
    - Password hash
    - Account creation timestamp
    - Relationship to recipes

    Attributes:
        id (UUID): Unique identifier for the user.
        hashed_password (str): Bcrypt hash of the user's password.
        date_created (datetime): When the user account was created.
        recipes (list[Recipe]): The list of recipes owned by the user.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    recipes: list["Recipe"] = Relationship(back_populates="owner", cascade_delete=True)
    images: list["Image"] = Relationship(back_populates="owner", cascade_delete=True)
    bookmarks: list["Bookmark"] = Relationship()
