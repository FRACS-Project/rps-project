##############################################################################################################
#
# Pydantic schemas for tag data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning tag data through the API endpoints.
#
##############################################################################################################

from pydantic import BaseModel, model_validator, field_validator
import uuid, re

from . import TagBase


class TagSchemaBase(TagBase):

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v


class TagPublic(TagBase):
    """Schema for publicly viewable tag data.
    
    Attributes:
        id (UUID): The tag's unique identifier.
        name (str): The tag name.
    """
    id: uuid.UUID


class TagCreate(TagSchemaBase):
    """Schema for creating a new Tag.
    
    Inherits all base Tag fields that are required for creation.
    """
    pass


class TagUpdate(TagSchemaBase):
    """Schema for updating Tag data.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        name (str, optional): The updated tag name.
    """
    name: str | None = None


class TagRef(BaseModel):
    """Reference schema for linking tags by id or name."""
    id: uuid.UUID | None = None
    name: str | None = None
    new: bool = False

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Name must only contain letters and spaces")
        return v

    @model_validator(mode="after")
    def validate_id_or_name(self) -> "TagRef":
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