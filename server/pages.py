from functools import lru_cache  # type: ignore
from re import search as re_search
from threading import Thread
from typing import Final, no_type_check

from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from werkzeug.wrappers import Response as ResponseWrapper

from ._types import Track
from .gh import fetch_repositories, schedule_refresh
from .utils import ICONS, STATIC, VIEWS

TRACKS: Final[list[Track]] = [
    Track(
        title="Bill_Nye",
        url="/audio/Bill_Nye.wav",
        artist="Tadj Cazaubon & Violet Mirrors",
    ),
    Track(title="Cheesed", url="/audio/Cheesed.wav", artist="Violet Mirrors"),
    Track(title="Jello", url="/audio/jello.mp3", artist="Waykool"),
    Track(
        title="Weather",
        url="/audio/Weather.wav",
        artist="Tadj Cazaubon & Violet Mirrors",
    ),
    Track(
        title="In Awe of The Machine",
        url="/audio/machine.wav",
        artist="Tadj Cazaubon & Violet Mirrors",
    ),
    Track(title="Grey Skies", url="/audio/grey_skies.wav", artist="Molly"),
    Track(
        title="Discotheque Diner", url="/audio/discotheque_diner.wav", artist="Molly"
    ),
    Track(title="Jonathan Seagull", url="/audio/jonathan_seagull.wav", artist="Molly"),
    Track(title="Boomer", url="/audio/boomer.wav", artist="Violet Mirrors"),
]


PageRouter = Blueprint(
    "pages", __name__, template_folder=str(VIEWS), static_folder=str(STATIC)
)
# Start the thread to fetch repositories.
Thread(target=schedule_refresh, daemon=True).start()


@no_type_check
@lru_cache(maxsize=128)
def is_mobile(user_agent: str) -> bool:
    """Detect if user agent is from a mobile device"""
    mobile_patterns = (
        r"Android",
        r"webOS",
        r"iPhone",
        r"iPad",
        r"iPod",
        r"BlackBerry",
        r"Windows Phone",
        r"Mobile",
        r"Opera Mini",
    )
    print(f"USER IS: {user_agent}")
    return any(re_search(pattern, user_agent) for pattern in mobile_patterns)


@no_type_check
@PageRouter.route("/detect")
def detect_device() -> ResponseWrapper | Response | str:
    """
    Detect the device type based on the User-Agent header.
    If the device is mobile, render the mobile version.
    Otherwise, redirect to the main page.
    """
    user_agent = request.headers.get("User-Agent", "")
    if is_mobile(user_agent):
        return render_template("mobile.html", tracks=TRACKS)
    else:
        return redirect("/")


@no_type_check
@PageRouter.route("/mobile")
def mobile_site() -> Response | str:
    """
    Render the mobile site alternative - a long scrolling page with sections.
    """
    projects = fetch_repositories()
    return render_template("mobile.html", projects=projects, tracks=TRACKS)


@no_type_check
@PageRouter.route("/", methods=["GET"])
async def catch_all() -> Response | str:
    """
    Catch-all route to serve the main page.
    This will render the main page with the appropriate content based on the device type.
    Mobile users are automatically redirected to the mobile version.
    """
    user_agent = request.headers.get("User-Agent", "")
    prefer_mobile = request.cookies.get("preferMobile")

    # Auto-redirect mobile users to mobile version
    if is_mobile(user_agent) and prefer_mobile != "false":
        return render_template(
            "mobile.html", tracks=TRACKS, projects=await fetch_repositories()
        )

    return send_from_directory(STATIC, "index.html")


@no_type_check
@PageRouter.route("/doom", methods=["GET"])
async def doom() -> Response | str:
    user_agent = request.headers.get("User-Agent", "")
    prefer_mobile = request.cookies.get("preferMobile")

    if is_mobile(user_agent) and prefer_mobile != "false":
        return render_template("mobile-doom.html")

    return render_template(
        "doom.html",
    )


@no_type_check
@PageRouter.route("/favicon.ico", methods=["GET"])
async def favicon() -> Response | str:
    return send_from_directory(
        ICONS, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@no_type_check
@PageRouter.route("/about", methods=["GET"])
def about() -> Response | str:
    return render_template("about.html")


@no_type_check
@PageRouter.route("/welcome", methods=["GET"])
def welcome() -> Response | str:
    return render_template("welcome.html")


@no_type_check
@PageRouter.route("/contact", methods=["GET"])
def contact() -> Response | str:
    return render_template("contact.html")


@no_type_check
@PageRouter.route("/google5b05a6b637606151.html", methods=["GET"])
def google_verification() -> Response | str:
    return render_template("google5b05a6b637606151.html")


@no_type_check
@PageRouter.route("/sitemap.xml", methods=["GET"])
def sitemap() -> Response:
    return send_from_directory(STATIC, "sitemap.xml", mimetype="application/xml")


@no_type_check
@PageRouter.route("/robots.txt", methods=["GET"])
def robots() -> Response:
    return send_from_directory(STATIC, "robots.txt", mimetype="text/plain")


@no_type_check
@PageRouter.route("/projects", methods=["GET"])
async def projects() -> Response | str:
    return render_template("projects.jinja", projects=await fetch_repositories())


@no_type_check
@PageRouter.route("/secrets", methods=["GET"])
def get_secret() -> Response | str:
    return render_template("secretbase.html")


@no_type_check
@PageRouter.route("/secretcheck", methods=["GET"])
def secret_check() -> Response | str:
    return jsonify({"Access Granted": "The secret code is correct!"})
