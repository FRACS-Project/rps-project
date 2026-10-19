"""Router registry.

Collects the routers of every feature module into `all_routers`, which
`main.py` registers on the FastAPI app.
"""

from .user.routers import user_router
from .auth.routers import login_router, register_router
from .recipe.routers import router as recipe_router
from .shared.ingredient.routers import router as ingredient_router
from .recipe.components.instruction.routers import router as instruction_router
from .recipe.components.recipe_ingredient.routers import router as rec_ing_router
from .shared.tag.routers import router as tag_router
from .shared.bookmark.routers import router as bookmark_router
from .shared.image.routers import router as image_router

all_routers = [
    user_router,
    login_router,
    register_router,
    recipe_router,
    ingredient_router,
    rec_ing_router,
    tag_router,
    instruction_router,
    bookmark_router,
    image_router,
]