"""Database module: engine, session dependency and table creation.

Also imports every table model so `SQLModel.metadata` knows all tables
before `create_db_and_tables()` runs.
"""

from .database import (
    engine,
    create_db_and_tables,
    get_session,
)

from ..user.models import User
from ..recipe.models import Recipe
from ..shared.tag.models import Tag
from ..shared.ingredient.models import Ingredient
from ..shared.bookmark.models import Bookmark
from ..recipe.components.recipe_tag.models import RecipeTag
from ..recipe.components.recipe_ingredient.models import RecipeIngredient
from ..recipe.components.instruction.models import Instruction

__all__ = [
    "engine",
    "create_db_and_tables",
    "get_session",
    "User",
    "Recipe",
    "Tag",
    "Ingredient",
    "Bookmark",
    "RecipeTag",
    "RecipeIngredient",
    "Instruction",
]