##############################################################################################################
#
# Query parameter type definitions for FastAPI endpoints.
#
# This module defines reusable type annotations for common query parameters
# used throughout the application's API endpoints, particularly for pagination.
# 
##############################################################################################################

from typing import Annotated
from fastapi import Query

# Limite maximale pour "limit"
LimitQuery = Annotated[int, Query(le=100, ge=1)]
DEFAULT_LIMIT = 100

# Décalage minimum pour "offset"
OffsetQuery = Annotated[int, Query(ge=0)]
DEFAULT_OFFSET = 0
