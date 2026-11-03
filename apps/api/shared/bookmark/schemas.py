"""Request and response schemas for bookmarks."""

import uuid
from pydantic import BaseModel

from . import Bookmark

class BookmarkPublic(Bookmark):
    """Bookmark returned by the API: `recipe_id` and `user_id`."""
    pass


class BookmarkCreate(BaseModel):
    """Bookmark fields used to insert a row: `recipe_id` and `user_id`."""
    recipe_id: uuid.UUID
    user_id: uuid.UUID | None = None

