"""
API Routes Package

Contains route handlers for:
- conversations: CRUD operations for user conversations
- generations: Content generation and signals
- feedback: User feedback submission (TODO)
- knowledge: Knowledge base search (TODO)
- experiments: A/B experiment participation (TODO)
- admin: Admin-only operations (costs, user management)
"""

from content_assistant.api.routes import conversations
from content_assistant.api.routes import generations
from content_assistant.api.routes import admin

__all__ = [
    "conversations",
    "generations",
    "admin",
]
