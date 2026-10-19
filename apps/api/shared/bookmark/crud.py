"""Database access for bookmarks. No validation; the service layer handles that."""

import uuid
from sqlmodel import Session, select

from . import Bookmark
from .schemas import BookmarkCreate


class BookmarkCrud:
    """Queries and writes for the bookmark table."""

    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def read_bookmark(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> Bookmark | None:
        """Return the user's bookmark on this recipe, or None."""
        query = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.recipe_id == recipe_id,
        )
        return self.db.exec(query).first()

    def read_bookmarks(self, offset: int, limit: int, user_id: uuid.UUID) -> list[Bookmark]:
        """Return a page of the user's bookmarks."""
        query = select(Bookmark).where(Bookmark.user_id == user_id)

        return self.db.exec(query.offset(offset).limit(limit)).all()

    def create_bookmark(self, bookmark: BookmarkCreate) -> Bookmark:
        """Insert a bookmark and commit."""

        db_bookmark = Bookmark.model_validate(bookmark)
        self.db.add(db_bookmark)
        self.db.commit()
        self.db.refresh(db_bookmark)
        return db_bookmark

    def delete_bookmark(self, db_bookmark: Bookmark) -> dict:
        """Delete a bookmark and commit."""
        self.db.delete(db_bookmark)
        self.db.commit()
        return {"ok": True}
