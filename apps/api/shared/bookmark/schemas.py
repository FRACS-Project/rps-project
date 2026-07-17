##############################################################################################################
#
# Pydantic schemas for recipe data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning recipe data through the API endpoints.
#
##############################################################################################################

import uuid

from . import Bookmark

class BookmarkPublic(Bookmark):
    """Schema for publicly viewable recipe data.
    
    Attributes:
        id (UUID): The recipe's unique identifier.
        name (str): The recipe name.
        preparation_time (int): Preparation time in minutes.
        cooking_time (int): Cooking time in minutes.
        description (str): Recipe description.
    """
    pass


class BookmarkCreate(Bookmark):
    """Schema for creating a new bookmark.
    
    Inherits all base recipe fields that are required for creation.
    """
    pass

