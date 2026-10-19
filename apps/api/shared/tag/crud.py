"""Database access for tags. No validation; the service layer handles that.

`pre_create_tag` only flushes, so it can run inside a recipe transaction
that is committed once.
"""

import uuid
from sqlmodel import Session, select

from . import Tag
from .schemas import TagCreate


class TagCrud:
    """Queries and writes for the tag table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_tag(self, tag: TagCreate) -> Tag:
        """Insert a tag and commit."""
        db_tag = Tag.model_validate(tag)
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag
    
    def pre_create_tag(self, tag: TagCreate) -> Tag:
        """Add a tag and flush without committing, so its ID is available."""
        db_tag = Tag.model_validate(tag)
        self.db.add(db_tag)
        self.db.flush()
        return db_tag

    def read_tags(self, offset: int = 0, limit: int = 100) -> list[Tag]:
        """Return a page of tags."""
        return self.db.exec(select(Tag).offset(offset).limit(limit)).all()

    def read_tag(self, tag_id: uuid.UUID) -> Tag | None:
        """Return the tag with this ID, or None."""
        return self.db.get(Tag, tag_id)

    def update_tag(self, db_tag: Tag, tag: dict) -> Tag:
        """Apply the given fields to a tag and commit."""
        db_tag.sqlmodel_update(tag)
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def delete_tag(self, db_tag: Tag) -> dict:
        """Delete a tag and commit."""
        self.db.delete(db_tag)
        self.db.commit()
        return {"ok": True}

    def get_tag_by_name(self, name: str) -> Tag | None:
        """Return the tag with exactly this name, or None."""
        query = select(Tag).where(Tag.name == name)
        return self.db.exec(query).first()
