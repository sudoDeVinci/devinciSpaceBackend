from pathlib import Path
from typing import Final
from os import getcwd

CWD: Final[Path] = Path(getcwd())
STATIC: Final[str] = CWD / "dist"
VIEWS: Final[str] = STATIC / "views"
ICONS: Final[str] = STATIC / "icons"
ASSETS: Final[str] = STATIC / "assets"
FONTS: Final[str] = STATIC / "fonts"
JS: Final[str] = STATIC / "js"
CSS: Final[str] = STATIC / "css"
IMAGES: Final[str] = STATIC / "images"
AUDIO: Final[str] = STATIC / "audio"
