from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    send_from_directory,
    jsonify,
    request,
)

from db import (
    PostService,
)

from typing import Final

from os.path import join

STATIC: Final[str] = join("..", "static")

routes = Blueprint("views", __name__)


@routes.route("/", defaults={"path": ""})
@routes.route("/<path:path>")
def catch_all(path: str = "") -> Response:
    if path == "":
        return send_from_directory(STATIC, "index.html")
    return send_from_directory(STATIC, path)


@routes.route("/about", methods=["GET"])
def about() -> str:
    return render_template("about.html")


@routes.route("/contact", methods=["GET"])
def contact() -> str:
    return render_template("contact.html")


@routes.route("/blogpost", methods=["GET"], defaults={"post_id": 1})
@routes.route("/blogpost/<int:post_id>")
def post(post_id: int) -> tuple[Response, int]:
    print(f"Post ID: {post_id}")
    post = PostService.get(postid=str(post_id))
    if post is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"post": post.json()}), 200


@routes.route("/blogposts", methods=["GET"])
def posts() -> tuple[Response, int]:
    page = int(request.args.get("page", 0))
    limit = int(request.args.get("limit", 10))
    posts = PostService.list(page=page, limit=limit)
    return (
        jsonify(
            {
                "posts": [post.json() for post in posts],
                "count": len(posts),
            }
        ),
        200,
    )
