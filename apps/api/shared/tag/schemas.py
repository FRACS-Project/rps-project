"""Request and response schemas for tags."""

from pydantic import BaseModel, model_validator, field_validator
import uuid, re

from . import TagBase


class TagSchemaBase(TagBase):
    """Base for tag request bodies. Adds validation of the name."""

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        """Strip spaces and allow only letters (accents included) and spaces."""
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v


class TagPublic(TagBase):
    """Tag returned by the API.

    Attributes:
        id: The tag's ID.
    """
    id: uuid.UUID


class TagCreate(TagSchemaBase):
    """Body for creating a tag."""
    pass


class TagUpdate(TagSchemaBase):
    """Partial update of a tag. Only the fields sent are changed."""
    name: str | None = None


class TagRef(BaseModel):
    """One tag in the `NewRecipe` / `PatchRecipe` body.

    Send either `id` for an existing tag, or `new=True` and a `name` to create one.

    Attributes:
        id: ID of an existing tag.
        name: Name of the tag to create.
        new: True to create the tag.
    """
    id: uuid.UUID | None = None
    name: str | None = None
    new: bool = False

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        """Strip and lowercase the name, and allow only letters (accents included) and spaces."""
        v = v.strip().lower()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v

    @model_validator(mode="after")
    def validate_id_or_name(self) -> "TagRef":
        """Require either `id`, or `new=True` with a `name`, but not both."""
        has_id = self.id is not None
        has_name = self.name is not None
        is_new = self.new is True

        if has_id and is_new:
            raise ValueError("Provide either id (existing tag) or new=true (new tag), not both.")
        if is_new and not has_name:
            raise ValueError("When new=true, name is required.")
        if not is_new and not has_id:
            raise ValueError("When new=false, id is required.")
        if has_id and has_name:
            raise ValueError("When id provided, don't provide name.")

        return self