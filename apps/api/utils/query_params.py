"""Reusable pagination query parameters.

`LimitQuery` (1 to 100) and `OffsetQuery` (>= 0) add validation to
`limit` / `offset` parameters in route signatures.
"""

from typing import Annotated
from fastapi import Query

LimitQuery = Annotated[int, Query(le=100, ge=1)]
DEFAULT_LIMIT = 100

OffsetQuery = Annotated[int, Query(ge=0)]
DEFAULT_OFFSET = 0
