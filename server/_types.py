from typing import TypedDict, Optional

class TrackJSON(TypedDict):
    title: str
    url: str
    thumbnail: Optional[str]
    artist: Optional[str]

class Track:
    __slots__ = (
        "title",
        "url",
        "thumbnail",
        "artist",
    )

    def __init__(
            self,
            title: str,
            url: str,
            thumbnail: str | None = None,
            artist: str | None = None
    ) -> None:
        self.title = title
        self.url = url
        self.thumbnail = thumbnail
        self.artist = artist

    def __repr__(self) -> str:
        return f"Track(title={self.title}, url={self.url}, thumbnail={self.thumbnail}, artist={self.artist})"
    
    def json(self) -> TrackJSON:
        """
        Convert the Track instance to a JSON serializable dictionary.
        """
        return {
            "title": self.title,
            "url": self.url,
            "thumbnail": self.thumbnail,
            "artist": self.artist
        }