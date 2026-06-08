
from .demo_urls import router as demo_router
from .bot_urls import router as bot_router
from .external_urls import router as external_router

__all__ = [
    'demo_router',
    'bot_router',
    'external_router'
]