from .gh import (
    Repository,
    User,
    RepoGist,
    RepoSlice,
    schedule_refresh,
    fetch_repositories,
)
from .db import Manager, Post, Comment, PostService, CommentService, TagManager
from flask import Flask  # type: ignore
from typing import Callable


def create_app() -> Flask:
    """
    Create a Flask app with the routes registered.
    Inject builtins like `enumerate` into the Jinja context.
    """
    from .routes import routes

    app = Flask(__name__)
    app.register_blueprint(routes)

    @app.context_processor
    def inject_builtins() -> dict[str, Callable]:
        return {"enumerate": enumerate}

    return app


__version__ = "0.0.1"

__all__ = [
    "Manager",
    "Post",
    "Comment",
    "PostService",
    "CommentService",
    "TagManager",
    "REPOSITORIES",
    "CACHE_LOCK",
    "REFRESH_TIMER",
    "REPOSITORY_JSON",
    "TOKEN",
    "LOG",
    "Repository",
    "User",
    "RepoGist",
    "RepoSlice",
    "schedule_refresh",
    "fetch_repositories",
    "create_app",
]
