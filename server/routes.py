from flask import (  # type: ignore
    Blueprint,
    Response,
    render_template,
    send_from_directory
)

from functools import lru_cache

from os.path import join
from typing import Final
from os import getcwd

from .gh import (
    fetch_repositories,
    schedule_refresh
)


STATIC: Final[str] = join(getcwd(), "dist")
CSS: Final[str] = join(STATIC, "css")
JS: Final[str] = join(STATIC, "js")
IMAGES: Final[str] = join(STATIC, "images")
ICONS: Final[str] = join(STATIC, "icons")
AUDIO: Final[str] = join(STATIC, "audio")
VIEWS: Final[str] = join(STATIC, "views")
ASSETS: Final[str] = join(STATIC, "assets")
FONTS: Final[str] = join(STATIC, "fonts")

routes = Blueprint("views", __name__, template_folder=VIEWS, static_folder=STATIC)
from threading import Thread
# Start the thread to fetch repositories.
Thread(target=schedule_refresh, daemon=True).start()

@routes.route("/", methods=["GET"])
async def catch_all() -> Response:
        return send_from_directory(STATIC, "index.html")

@routes.route("/favicon.ico", methods=["GET"])
async def favicon() -> Response:
    """
    Serve the favicon.ico file.
    """
    return send_from_directory(ICONS, "favicon.ico", mimetype='image/vnd.microsoft.icon')

@lru_cache()
@routes.route("/ms_sans_serif.woff2", methods=["GET"])
async def ms_sans_serif() -> Response:
    """
    Serve the MS Sans Serif font file.
    This is used for the pixelated font style in the application.
    """
    return send_from_directory(FONTS, "ms_sans_serif.woff2", mimetype='font/woff2')


@lru_cache()
@routes.route("/ms_sans_serif_bold.woff2", methods=["GET"])
async def ms_sans_serif_bold() -> Response:
    """
    Serve the bold version of the MS Sans Serif font file.
    This is used for the pixelated font style in the application.
    """
    return send_from_directory(FONTS, "ms_sans_serif_bold.woff2", mimetype='font/woff2')


# Media routes.
@lru_cache()
@routes.route("/css", defaults={"filepath": ""}, methods=["GET"])
@routes.route("/css/<path:filepath>", methods=["GET"])
async def css(filepath: str="") -> Response:
    return send_from_directory(CSS, filepath)

@lru_cache()
@routes.route("/js", defaults={"filepath": ""}, methods=["GET"])
@routes.route("/js/<path:filepath>", methods=["GET"])
async def js(filepath: str="") -> Response:
    return send_from_directory(JS, filepath)

@lru_cache()
@routes.route("/icons", defaults={"iconpath": ""}, methods=["GET"])
@routes.route("/icons/<path:iconpath>", methods=["GET"])
async def icons(iconpath: str="") -> Response:
    return send_from_directory(ICONS, iconpath)

@lru_cache()
@routes.route("/images", methods=["GET"])
@routes.route("/images/<path:imagepath>", methods=["GET"])
async def images(imagepath: str="") -> Response:
    return send_from_directory(IMAGES, imagepath)

@lru_cache()
@routes.route("/audio", methods=["GET"])
@routes.route("/audio/<path:audiopath>", methods=["GET"])
async def audio(audiopath: str="") -> Response:
    return send_from_directory(AUDIO, audiopath)

@lru_cache()
@routes.route("/assets/", defaults={"assetpath": ""}, methods=["GET"])
@routes.route("/assets/<path:assetpath>", methods=["GET"])
async def assets(assetpath: str="") -> Response:
    print(f'>>> ASSET: {assetpath}')
    ext = assetpath.split(".")[-1] if "." in assetpath else ""
    mime = "text/css" if ext == "css" else "application/javascript"
    return send_from_directory(ASSETS, assetpath, mimetype=mime)

@lru_cache()
@routes.route("/fonts", defaults={"fontpath": ""}, methods=["GET"])
@routes.route("/fonts/<path:fontpath>", methods=["GET"])
async def fonts(fontpath: str="") -> Response:
    return send_from_directory(FONTS, fontpath)

@lru_cache()
@routes.route("/css/fonts", methods=["GET"])
@routes.route("/css/fonts/<path:fontfile>", methods=["GET"])
async def fonts_css(fontfile: str = "") -> Response:
    """
    Serve font files from the fonts directory.
    This is used for CSS font-face declarations.
    """
    return send_from_directory(FONTS, fontfile)



"""
Page routes - Each is rendered within separate windows
"""
@lru_cache()    
@routes.route("/about", methods=["GET"])
async def about() -> str:
    return render_template("about.html")

@lru_cache()
@routes.route("/welcome", methods=["GET"])
async def welcome() -> str:
    return render_template("welcome.html")

@lru_cache()
@routes.route("/contact", methods=["GET"])
async def contact() -> str:
    return render_template("contact.html")

@lru_cache()
@routes.route("/doom", methods=["GET"])
async def doom() -> str:
    return render_template("doom.html")

@routes.route("/projects", methods=["GET"])
async def projects() -> str:
    return render_template("projects.jinja", projects = await fetch_repositories()) 