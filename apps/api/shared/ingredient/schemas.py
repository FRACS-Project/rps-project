"""Request and response schemas for ingredients."""

from pydantic import field_validator
import re
import uuid
from . import IngredientBase


class IngredientSchemaBase(IngredientBase):
    """Base for ingredient request bodies. Adds validation of the name."""

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        """Strip spaces and allow only letters (accents included), spaces, `'` and `-`."""
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ'\-\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v


class IngredientPublic(IngredientBase):
    """Ingredient returned by the API.

    Attributes:
        id: The ingredient's ID.
    """
    id: uuid.UUID


class IngredientCreate(IngredientSchemaBase):
    """Body for creating an ingredient."""
    pass


class IngredientUpdate(IngredientSchemaBase):
    """Partial update of an ingredient. Only the fields sent are changed."""
    name: str | None = None
