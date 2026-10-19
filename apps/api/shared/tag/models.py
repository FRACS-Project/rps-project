"""Tag table model. Tags are shared by all users and linked to recipes through `RecipeTag`."""

import uuid
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from ...recipe.components.recipe_tag.models import RecipeTag

if TYPE_CHECKING:
    from ...recipe import Recipe


class TagBase(SQLModel):
    """Fields shared by the tag table and its schemas.

    Attributes:
        name: Unique tag name.
    """
    name: str = Field(index=True, unique=True)


class Tag(TagBase, table=True):
    """Tag table.

    Attributes:
        id: Primary key.
        recipes: Recipes that have this tag.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    recipes: list["Recipe"] = Relationship(
        back_populates="tags",
        link_model=RecipeTag,
    )