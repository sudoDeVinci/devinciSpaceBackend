from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    request,
    send_from_directory,
    jsonify
)

from server.db import (
    PostService,
)

from typing import Final

from os.path import join

STATIC: Final[str] = join("..", "static")

routes = Blueprint("views", __name__)

@routes.route('/', defaults={'path': ''})
@routes.route('/<path:path>')
def catch_all(path: str = '') -> Response:
    if path == "":
        return send_from_directory(STATIC, "index.html")
    return send_from_directory(STATIC, path)


@routes.route("/about", methods=["GET"])
def about() -> Response:
    return render_template("about.html")


@routes.route("/contact", methods=["GET"])
def contact() -> Response:
    return render_template("contact.html")


@routes.route("/blogposts", methods=["GET"], defaults={"post_id": 1})
@routes.route("/blogposts/<int:post_id>")
def post(post_id: int) -> Response:
    print(f'Post ID: {post_id}')
    post = PostService.get(postid=str(post_id))
    if post is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(post.json())
