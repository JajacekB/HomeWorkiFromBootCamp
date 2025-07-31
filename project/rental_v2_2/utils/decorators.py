from functools import wraps
from database.base import Session


def with_session_if_needed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = kwargs.get("session", None)
        if session is None:
            with Session() as new_session:
                kwargs["session"] = new_session
                return func(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper