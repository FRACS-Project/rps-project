"""Tag service.

Tag CRUD for the admin routes, plus the `sync_*` methods that
`RecipeService` calls to link a recipe's tags (creating new ones when
needed) inside its transaction.
"""

import uuid
from sqlmodel import Session

from . import (
    Tag,
    DuplicateTagNameError,
    TagNotFoundError
)

from .schemas import (
    TagCreate,
    TagUpdate,
    TagRef
)

from .crud import TagCrud

from ...recipe import Recipe

from ...utils import LimitQuery, OffsetQuery


class TagService:
    """Business logic for tags."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db
        self.crud = TagCrud(self.db)

    def create_tag(self, tag: TagCreate) -> Tag:
        """Create a tag and commit.

        Raises:
            DuplicateTagNameError: If a tag already has this name.
        """
        if self.crud.get_tag_by_name(tag.name):
            raise DuplicateTagNameError()

        return self.crud.create_tag(tag)
    
    def pre_create_tag(self, tag: TagCreate) -> Tag:
        """Create a tag without committing. Used when saving a recipe.

        Raises:
            DuplicateTagNameError: If a tag already has this name.
        """
        if self.crud.get_tag_by_name(tag.name):
            raise DuplicateTagNameError()

        return self.crud.pre_create_tag(tag)

    def get_tags(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Tag]:
        """Return a page of tags."""
        return self.crud.read_tags(offset, limit)

    def get_tag(self, tag_id: uuid.UUID) -> Tag:
        """Return a tag by ID.

        Raises:
            TagNotFoundError: If no tag has this ID.
        """
        tag = self.crud.read_tag(tag_id)
        if not tag:
            raise TagNotFoundError()

        return tag
    
    def get_tag_by_name(self, name: str) -> Tag:
        """Return a tag by exact name.

        Raises:
            TagNotFoundError: If no tag has this name.
        """
        tag = self.crud.get_tag_by_name(name)
        if not tag:
            raise TagNotFoundError()
                
        return tag

    def update_tag(self, tag_id: uuid.UUID, tag: TagUpdate) -> Tag:
        """Partially update a tag. Does not re-check name uniqueness.

        Args:
            tag_id: ID of the tag.
            tag: Fields to change.

        Returns:
            The updated tag.

        Raises:
            TagNotFoundError: If no tag has this ID.
        """
        db_tag = self.crud.read_tag(tag_id)
        if not db_tag:
            raise TagNotFoundError()

        tag_data = tag.model_dump(exclude_unset=True)

        return self.crud.update_tag(db_tag, tag_data)

    def delete_tag(self, tag_id: uuid.UUID) -> dict:
        """Delete a tag.

        Returns:
            `{"ok": True}`.

        Raises:
            TagNotFoundError: If no tag has this ID.
        """
        db_tag = self.crud.read_tag(tag_id)
        if not db_tag:
            raise TagNotFoundError()

        self.crud.delete_tag(db_tag)
        return {"ok": True}

    def sync_tags_on_create(self, recipe: Recipe, tags: list[TagRef]):
        """Link the tags of a new recipe, creating the `new` ones. Does not commit.

        Args:
            recipe: The new recipe.
            tags: Tags from the `NewRecipe` body.

        Raises:
            TagNotFoundError: If a tag ID does not exist.
            DuplicateTagNameError: If a `new` tag's name already exists.
        """
        for tag in tags:
            if tag.new:
                db_tag = self.pre_create_tag(
                    TagCreate(name=tag.name))
            elif tag.id:
                db_tag = self.get_tag(tag.id)
            recipe.tags.append(db_tag)

    def sync_tags_on_update(self, db_recipe: Recipe, tags: list[TagRef]) -> None:
        """Make the recipe's tags match the payload. Does not commit.

        Tags missing from the payload are unlinked (the tags themselves are kept),
        `new` tags are created, and the others are linked.

        Args:
            db_recipe: Recipe being edited.
            tags: Full list of tags from the `PatchRecipe` body.

        Raises:
            TagNotFoundError: If a tag ID does not exist.
            DuplicateTagNameError: If a `new` tag's name already exists.
        """
        desired_tag_ids: set[uuid.UUID] = set()

        for tag in tags:
            if tag.new:
                created_tag = self.pre_create_tag(
                    TagCreate(name=tag.name))
                desired_tag_ids.add(created_tag.id)
            elif tag.id:
                desired_tag_ids.add(tag.id)

        current_tag_ids = {tag.id for tag in db_recipe.tags}
        tag_ids_to_remove = current_tag_ids - desired_tag_ids
        tag_ids_to_add = desired_tag_ids - current_tag_ids

        db_recipe.tags = [
            tag
            for tag in db_recipe.tags
            if tag.id not in tag_ids_to_remove
        ]

        for tag_id in tag_ids_to_add:
            db_recipe.tags.append(self.get_tag(tag_id))