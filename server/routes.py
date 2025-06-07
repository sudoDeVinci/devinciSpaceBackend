from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    send_from_directory,
    session,
    jsonify,
    request,
)

from functools import lru_cache

from os.path import join
from typing import Final
from os import getcwd

from .gh.repositories import (
    fetch_repositories,
    schedule_repository_refresh,
    read_repositories
)
from threading import Thread

# Load most recent cache.
read_repositories()
# Start the background thread to refresh repositories.
Thread(target=schedule_repository_refresh, daemon=True).start() 


STATIC: Final[str] = join(getcwd(), "dist")
CSS: Final[str] = join(STATIC, "css")
JS: Final[str] = join(STATIC, "js")
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
@lru_cache()
@routes.route("/css", defaults={"filepath": ""}, methods=["GET"])
@routes.route("/css/<path:filepath>", methods=["GET"])
def css(filepath: str="") -> str:
    return send_from_directory(CSS, filepath)

@lru_cache()
@routes.route("/js", defaults={"filepath": ""}, methods=["GET"])
@routes.route("/js/<path:filepath>", methods=["GET"])
def js(filepath: str="") -> str:
    return send_from_directory(JS, filepath)

@lru_cache()
@routes.route("/icons", defaults={"iconpath": ""}, methods=["GET"])
@routes.route("/icons/<path:iconpath>", methods=["GET"])
def icons(iconpath: str="") -> str:
    return send_from_directory(ICONS, iconpath)

@lru_cache()
@routes.route("/images", methods=["GET"])
@routes.route("/images/<path:imagepath>", methods=["GET"])
def images(imagepath: str="") -> str:
    return send_from_directory(IMAGES, imagepath)

@lru_cache()
@routes.route("/audio", methods=["GET"])
@routes.route("/audio/<path:audiopath>", methods=["GET"])
def audio(audiopath: str="") -> str:
    return send_from_directory(AUDIO, audiopath)

@lru_cache()
@routes.route("/assets/", defaults={"assetpath": ""}, methods=["GET"])
@routes.route("/assets/<path:assetpath>", methods=["GET"])
def assets(assetpath: str="") -> str:
    print(f'>>> ASSET: {assetpath}')
    ext = assetpath.split(".")[-1] if "." in assetpath else ""
    mime = "text/css" if ext == "css" else "application/javascript"
    return send_from_directory(ASSETS, assetpath, mimetype=mime)


"""
Page routes - Each is rendered within separate windows
"""
@lru_cache()    
@routes.route("/about", methods=["GET"])
def about() -> str:
    return render_template("about.html")

@lru_cache()
@routes.route("/welcome", methods=["GET"])
def welcome() -> str:
    return render_template("welcome.html")

@lru_cache()
@routes.route("/contact", methods=["GET"])
def contact() -> str:
    return render_template("contact.html")

@lru_cache()
@routes.route("/doom", methods=["GET"])
def doom() -> str:
    return render_template("doom.html")

@routes.route("/projects", methods=["GET"])
def projects() -> str:
    return render_template("projects.jinja", projects = fetch_repositories()) 