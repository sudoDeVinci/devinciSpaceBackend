from pathlib import Path
from typing import Final
from os import getcwd

CWD: Final[Path] = Path(getcwd())
STATIC: Final[Path] = CWD / "dist"
VIEWS: Final[Path] = STATIC / "views"
ICONS: Final[Path] = STATIC / "icons"
ASSETS: Final[Path] = STATIC / "assets"
FONTS: Final[Path] = STATIC / "fonts"
JS: Final[Path] = STATIC / "js"
CSS: Final[Path] = STATIC / "css"
IMAGES: Final[Path] = STATIC / "images"
AUDIO: Final[Path] = STATIC / "audio"
