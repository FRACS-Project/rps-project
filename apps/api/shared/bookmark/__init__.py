"""Bookmark module: model and exceptions."""

from .models import Bookmark
from .exceptions import BookmarkNotFoundError, DuplicateBookmarkError

__all__ = [
    "Bookmark",
    "BookmarkNotFoundError",
    "DuplicateBookmarkError"
]