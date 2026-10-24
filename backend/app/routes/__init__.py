from fastapi import APIRouter

from app.routes import graph, health, links, media, reviews

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(media.router)
api_router.include_router(reviews.router)
api_router.include_router(links.router)
api_router.include_router(graph.router)
