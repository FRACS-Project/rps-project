"""Request and response schemas for bookmarks."""

import uuid

from . import Bookmark

class BookmarkPublic(Bookmark):
    """Bookmark returned by the API: `recipe_id` and `user_id`."""
    pass


class BookmarkCreate(Bookmark):
    """Bookmark fields used to insert a row: `recipe_id` and `user_id`."""
    pass

