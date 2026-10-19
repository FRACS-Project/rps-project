"""Bookmark module: model and exceptions."""

from .models import Bookmark
from .exceptions import BookmarkNotFoundError

__all__ = [
    "Bookmark",
    "BookmarkNotFoundError"
]