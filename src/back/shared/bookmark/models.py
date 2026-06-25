##############################################################################################################
#
# Database models for recipe-user relationships as favorites.
#
# This module defines the SQLModel class for the recipe-user junction table.
#
##############################################################################################################

import uuid
from sqlmodel import SQLModel, Field


class Bookmark(SQLModel, table=True):
    """Junction table linking recipes and user.

    Attributes:
        recipe_id (UUID): Foreign key reference to the recipe.
        user_id (UUID): Foreign key reference to the user.
    """
    recipe_id: uuid.UUID = Field(foreign_key="recipe.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)