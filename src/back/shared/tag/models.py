##############################################################################################################
#
# Database models for tag management.
#
# This module defines the SQLModel classes for tag data persistence,
# including base tag information and the complete tag model with relationships.
#
##############################################################################################################

import uuid
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from ...recipe.components.recipe_tag.models import RecipeTag

if TYPE_CHECKING:
    from ...recipe import Recipe


class TagBase(SQLModel):
    """Base model for tag information.

    Attributes:
        name (str): The tag name.
    """
    name: str = Field(index=True, unique=True)


class Tag(TagBase, table=True):
    """Complete tag model for database storage.

    Extends TagBase to include:
    - Unique identifier
    - Relationship to recipes

    Attributes:
        id (UUID): Unique identifier for the tag.
        recipes (list[Recipe]): The recipes associated with this tag.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipes: list["Recipe"] = Relationship(
        back_populates="tags",
        link_model=RecipeTag,
    )