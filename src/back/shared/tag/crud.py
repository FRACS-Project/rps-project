##############################################################################################################
#
# CRUD operations for managing Tags in the application.
#
# This module provides functions to create, read, update, and delete Tag entities
# in the database. It handles all database interactions related to Tags.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import Tag
from .schemas import TagCreate


class TagCrud:

    def __init__(self, db: Session):
        """Initialize TagCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_tag(self, tag: TagCreate) -> Tag:
        """Create a new Tag in the database.

        Args:
            tag (TagCreate): The tag data to create.

        Returns:
            Tag: The newly created tag instance.
        """
        db_tag = Tag.model_validate(tag)
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag
    
    def pre_create_tag(self, tag: TagCreate) -> Tag:
        """Create a new Tag in the database.

        Args:
            tag (TagCreate): The tag data to create.

        Returns:
            Tag: The newly created tag instance.
        """
        db_tag = Tag.model_validate(tag)
        self.db.add(db_tag)
        self.db.flush()
        return db_tag

    def read_tags(self, offset: int = 0, limit: int = 100) -> list[Tag]:
        """Retrieve a paginated list of tags.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[Tag]: A list of Tag instances.
        """
        return self.db.exec(select(Tag).offset(offset).limit(limit)).all()

    def read_tag(self, tag_id: uuid.UUID) -> Tag | None:
        """Retrieve a specific Tag by its ID.

        Args:
            tag_id (uuid.UUID): The unique identifier of the Tag.

        Returns:
            Tag | None: The found Tag instance or None if not found.
        """
        return self.db.get(Tag, tag_id)

    def update_tag(self, db_tag: Tag, tag: dict) -> Tag:
        """Update an existing Tag's information.

        Args:
            db_tag (Tag): The existing Tag instance to update.
            tag (dict): The new tag data to apply.

        Returns:
            Tag: The updated tag instance.
        """
        db_tag.sqlmodel_update(tag)
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def delete_tag(self, db_tag: Tag) -> dict:
        """Delete a Tag from the database.

        Args:
            db_tag (Tag): The Tag instance to delete.

        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_tag)
        self.db.commit()
        return {"ok": True}

    def get_tag_by_name(self, name: str) -> Tag | None:
        """Retrieve a tag by its name.

        Args:
            name (str): The name of the tag to search for.

        Returns:
            Tag | None: The found tag instance or None if not found.
        """
        query = select(Tag).where(Tag.name == name)
        return self.db.exec(query).first()
