"""Bookmark table model: the recipes a user saved."""

import uuid
from sqlmodel import SQLModel, Field


class Bookmark(SQLModel, table=True):
    """Link between a user and a recipe they bookmarked.

    Attributes:
        recipe_id: ID of the bookmarked recipe.
        user_id: ID of the user.
    """
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)