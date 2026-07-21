from app.models.user import create_indexes as _user_indexes
from app.models.chat import create_indexes as _chat_indexes
from app.models.message import create_indexes as _message_indexes

def init_indexes() -> None:
    """
    Idempotent — safe to call on every app startup.
    MongoDB just confirms existing indexes rather than recreating them.
    """
    _user_indexes()
    _chat_indexes()
    _message_indexes()
