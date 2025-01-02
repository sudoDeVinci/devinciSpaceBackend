from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    request,
    send_from_directory,
)

from server.db import (
    PostService,
)

routes = Blueprint("views", __name__)


@routes.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(".", "favicon.ico")


@routes.route("/about", methods=["GET"])
def about() -> Response:
    return render_template("about.html")


@routes.route("/contact", methods=["GET"])
def contact() -> Response:
    return render_template("contact.html")


@routes.route("/blogposts", methods=["GET"])
def posts() -> Response:
    page: int = request.args.get("page", 0, type=int)
    limit: int = request.args.get("limit", 10, type=int)
    posts = PostService.list(page=page, limit=limit)
    return render_template("posts.html", posts=posts)


@routes.route("/blogpost/<int:post_id>", methods=["GET"])
def post(post_id: int) -> Response:
    post = PostService.get(post_id=post_id)
    return render_template("post.html", post=post)
