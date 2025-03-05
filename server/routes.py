from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    send_from_directory,
    jsonify,
    request,
)
from os.path import join
from typing import Final

from .gh.repositories import get_repositories

STATIC: Final[str] = join("..", "dist")
CSS: Final[str] = join(STATIC, "css")
IMAGES: Final[str] = join(STATIC, "images")
ICONS: Final[str] = join(STATIC, "icons")
AUDIO: Final[str] = join(STATIC, "audio")
VIEWS: Final[str] = join(STATIC, "views")
ASSETS: Final[str] = join(STATIC, "assets")

routes = Blueprint("views", __name__, template_folder=VIEWS, static_folder=STATIC)


@routes.route("/", defaults={"path": ""})
def catch_all(path: str = "") -> Response:
        return send_from_directory(STATIC, "index.html")

# Media routes.

@routes.route("/css", defaults={"filepath": ""}, methods=["GET"])
@routes.route("/css/<path:filepath>", methods=["GET"])
def css(filepath: str="") -> str:
    return send_from_directory(CSS, filepath)

@routes.route("/icons", defaults={"iconpath": ""}, methods=["GET"])
@routes.route("/icons/<path:iconpath>", methods=["GET"])
def icons(iconpath: str="") -> str:
    return send_from_directory(ICONS, iconpath)

@routes.route("/images", methods=["GET"])
@routes.route("/images/<path:imagepath>", methods=["GET"])
def images(imagepath: str="") -> str:
    return send_from_directory(IMAGES, imagepath)

@routes.route("/audio", methods=["GET"])
@routes.route("/audio/<path:audiopath>", methods=["GET"])
def audio(audiopath: str="") -> str:
    return send_from_directory(AUDIO, audiopath)

@routes.route("/assets/", defaults={"assetpath": ""}, methods=["GET"])
@routes.route("/assets/<path:assetpath>", methods=["GET"])
def assets(assetpath: str="") -> str:
    print(f'>>> ASSET: {assetpath}')
    ext = assetpath.split(".")[-1] if "." in assetpath else ""
    mime = "text/css" if ext == "css" else "application/javascript"
    return send_from_directory(ASSETS, assetpath, mimetype=mime)


# API routes

@routes.route("/about", methods=["GET"])
def about() -> str:
    return render_template("about.html")

@routes.route("/welcome", methods=["GET"])
def welcome() -> str:
    return render_template("welcome.html")

@routes.route("/projects", methods=["GET"])
def projects() -> str:
    return render_template("projects.jinja", projects = get_repositories()) 
