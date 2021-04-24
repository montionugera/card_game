from fastapi import APIRouter

from app.api.api_v1.endpoints import best_scores, games, items, login, users, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(
    best_scores.router, prefix="/best_scores", tags=["best_scores"]
)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
