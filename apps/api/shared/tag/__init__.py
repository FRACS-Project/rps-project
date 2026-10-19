"""Tag module: model and exceptions. Services and routers are imported directly to avoid circular imports."""

from .models import Tag, TagBase
from .exceptions import (
    DuplicateTagNameError,
    TagNotFoundError
)

__all__ = [
    "Tag",
    "TagBase",
    "DuplicateTagNameError",
    "TagNotFoundError"
]