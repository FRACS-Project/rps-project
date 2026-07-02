##############################################################################################################
#
# Tag Service Layer - Business Logic and Validation
#
# This module contains the service layer for Tag management.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, existence)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - Tag creation with duplicate name checking
#   - Tag retrieval and pagination
#   - Tag updates and deletion with existence validation
#
##############################################################################################################

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
)

from .crud import TagCrud

from ...utils import LimitQuery, OffsetQuery


class TagService:
    """Service layer for Tag management.

    Handles all business logic related to Tags including creation, validation,
    and lifecycle operations. Coordinates between HTTP routes and database CRUD.
    """

    def __init__(self, db: Session):
        """Initialize TagService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = TagCrud(self.db)

    def create_tag(self, tag: TagCreate) -> Tag:
        """Create a new Tag with duplicate name validation.

        Args:
            tag (TagCreate): The tag data to create.

        Returns:
            Tag: The newly created tag.

        Raises:
            DuplicateTagNameError: If Tag name already exists.
        """
        if self.crud.get_tag_by_name(tag.name):
            raise DuplicateTagNameError()

        return self.crud.create_tag(tag)
    
    def pre_create_tag(self, tag: TagCreate) -> Tag:
        """Create a new Tag with duplicate name validation.

        Args:
            tag (TagCreate): The tag data to create.

        Returns:
            Tag: The newly created tag.

        Raises:
            DuplicateTagNameError: If Tag name already exists.
        """
        if self.crud.get_tag_by_name(tag.name):
            raise DuplicateTagNameError()

        return self.crud.pre_create_tag(tag)

    def get_tags(self, offset: OffsetQuery = 0, limit: LimitQuery = 100) -> list[Tag]:
        """Retrieve a paginated list of Tags.

        Args:
            offset (int): Number of tags to skip (for pagination).
            limit (int): Maximum number of tags to return.

        Returns:
            List[Tag]: List of tags.
        """
        return self.crud.read_tags(offset, limit)

    def get_tag(self, tag_id: uuid.UUID) -> Tag:
        """Retrieve a specific Tag by ID.

        Args:
            tag_id (uuid.UUID): The unique identifier of the tag.

        Returns:
            Tag: The found tag instance.

        Raises:
            TagNotFoundError: If the Tag is not found.
        """
        tag = self.crud.read_tag(tag_id)
        if not tag:
            raise TagNotFoundError()

        return tag
    
    def get_tag_by_name(self, name: str) -> Tag:
        """Retrieve a specific Tag by name.

        Args:
            name (str): The name of the tag.

        Returns:
            Tag: The found tag instance.

        Raises:
            TagNotFoundError: If the Tag is not found.
        """
        tag = self.crud.get_tag_by_name(name)
        if not tag:
            raise TagNotFoundError()
                
        return tag

    def update_tag(self, tag_id: uuid.UUID, tag: TagUpdate) -> Tag:
        """Update an existing Tag's information.

        Args:
            tag_id (uuid.UUID): The unique identifier of the tag.
            tag (TagUpdate): The new tag data to apply.

        Returns:
            Tag: The updated tag instance.

        Raises:
            TagNotFoundError: If the Tag is not found.
        """
        db_tag = self.crud.read_tag(tag_id)
        if not db_tag:
            raise TagNotFoundError()

        tag_data = tag.model_dump(exclude_unset=True)

        return self.crud.update_tag(db_tag, tag_data)

    def delete_tag(self, tag_id: uuid.UUID) -> dict:
        """Delete a Tag by ID.

        Args:
            tag_id (uuid.UUID): The unique identifier of the tag.

        Raises:
            TagNotFoundError: If the Tag is not found.
        """
        db_tag = self.crud.read_tag(tag_id)
        if not db_tag:
            raise TagNotFoundError()

        self.crud.delete_tag(db_tag)
        return {"ok": True}