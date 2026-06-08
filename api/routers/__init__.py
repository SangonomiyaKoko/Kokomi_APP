
from .bot_urls import router as bot_router
from .manager_urls import router as manager_router
from .search_urls import router as search_router
from .external_urls import router as external_router
from .ranking_urls import router as ranking_router

__all__ = [
    'bot_router',
    'manager_router',
    'search_router',
    'external_router',
    'ranking_router'
]