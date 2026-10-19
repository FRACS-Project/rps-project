"""Recipe-tag link table model."""

import uuid
from sqlmodel import SQLModel, Field, Relationship


class RecipeTag(SQLModel, table=True):
    """Many-to-many link between recipes and tags.

    Attributes:
        recipe_id: ID of the recipe.
        tag_id: ID of the tag.
    """
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)