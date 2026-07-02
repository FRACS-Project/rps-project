##############################################################################################################
#
# Database models for recipe-tag relationships.
#
# This module defines the SQLModel class for the recipe-tag junction table.
#
##############################################################################################################

import uuid
from sqlmodel import SQLModel, Field, Relationship


class RecipeTag(SQLModel, table=True):
    """Junction table linking recipes and tags.

    Attributes:
        recipe_id (UUID): Foreign key reference to the recipe.
        tag_id (UUID): Foreign key reference to the tag.
    """
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)