from flask import (  # type: ignore
    Blueprint,
    Response,
    send_from_directory
)

from .utils import (
    VIEWS,
    STATIC,
    ICONS,
    FONTS,
    CSS,
    JS,
    IMAGES,
    AUDIO,
    ASSETS
)

from pathlib import Path


AssetRouter = Blueprint("assets", __name__, template_folder=str(VIEWS), static_folder=str(STATIC))


@AssetRouter.route("/favicon.ico", methods=["GET"])
def favicon() -> Response:
    """
    Serve the favicon.ico file.
    """
    return send_from_directory(ICONS, "favicon.ico", mimetype='image/vnd.microsoft.icon')

@AssetRouter.route("/ms_sans_serif.woff2", methods=["GET"])
def ms_sans_serif() -> Response:
    """
    Serve the MS Sans Serif font file.
    This is used for the pixelated font style in the application.
    """
    return send_from_directory(FONTS, "ms_sans_serif.woff2", mimetype='font/woff2')



@AssetRouter.route("/ms_sans_serif_bold.woff2", methods=["GET"])
def ms_sans_serif_bold() -> Response:
    """
    Serve the bold version of the MS Sans Serif font file.
    This is used for the pixelated font style in the application.
    """
    return send_from_directory(FONTS, "ms_sans_serif_bold.woff2", mimetype='font/woff2')

# Media routes.

@AssetRouter.route("/css", defaults={"filepath": ""}, methods=["GET"])
@AssetRouter.route("/css/<path:filepath>", methods=["GET"])
def css(filepath: str="") -> Response:
    return send_from_directory(CSS, filepath)


@AssetRouter.route("/js", defaults={"filepath": ""}, methods=["GET"])
@AssetRouter.route("/js/<path:filepath>", methods=["GET"])
def js(filepath: str="") -> Response:
    return send_from_directory(JS, filepath)


@AssetRouter.route("/icons", defaults={"iconpath": ""}, methods=["GET"])
@AssetRouter.route("/icons/<path:iconpath>", methods=["GET"])
def icons(iconpath: str="") -> Response:
    return send_from_directory(ICONS, iconpath)


@AssetRouter.route("/images", methods=["GET"])
@AssetRouter.route("/images/<path:imagepath>", methods=["GET"])
def images(imagepath: str="") -> Response:
    return send_from_directory(IMAGES, imagepath)


@AssetRouter.route("/audio", methods=["GET"])
@AssetRouter.route("/audio/<path:audiopath>", methods=["GET"])
def audio(audiopath: str="") -> Response:
    return send_from_directory(AUDIO, audiopath)


@AssetRouter.route("/assets/", defaults={"assetpath": ""}, methods=["GET"])
@AssetRouter.route("/assets/<path:assetpath>", methods=["GET"])
def assets(assetpath: str="") -> Response:
    print(f'>>> ASSET: {assetpath}')
    ext = assetpath.split(".")[-1] if "." in assetpath else ""
    
    # Set appropriate MIME type based on file extension
    if ext == "css":
        mime = "text/css"
    elif ext == "wasm":
        mime = "application/wasm"
    else:
        mime = "application/javascript"
    
    return send_from_directory(ASSETS, assetpath, mimetype=mime)


@AssetRouter.route("/fonts", defaults={"fontpath": ""}, methods=["GET"])
@AssetRouter.route("/fonts/<path:fontpath>", methods=["GET"])
def fonts(fontpath: str="") -> Response:
    return send_from_directory(FONTS, fontpath)


@AssetRouter.route("/css/fonts", methods=["GET"])
@AssetRouter.route("/css/fonts/<path:fontfile>", methods=["GET"])
def fonts_css(fontfile: str = "") -> Response:
    """
    Serve font files from the fonts directory.
    This is used for CSS font-face declarations.
    """
    return send_from_directory(FONTS, fontfile)

@AssetRouter.route("/doom.wasm", methods=["GET"])
def doom_wasm() -> Response:
    """
    Serve the Doom WebAssembly module.
    This is used to run the Doom game in the browser.
    """
    return send_from_directory(ASSETS, "doom.wasm", mimetype='application/wasm')