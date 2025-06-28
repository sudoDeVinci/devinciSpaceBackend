from typing import TypedDict
from datetime import datetime
from uuid import uuid4
from abc import ABC


def dt2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

def str2dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")


class TagManager:
    """
    A utility class to manage tags using binary encoding stored as bytes.
    This class provides class methods to encode and decode tags, as well as
    perform tag-based operations efficiently.
    """

    # Tag-to-bit mapping
    TAGS: dict[str, int] = {
        "backend": 1,
        "frontend": 2,
        "database": 3,
        "security": 4,
        "python": 5,
        "javascript": 6,
        "java": 7,
        "c/c++": 8,
        "arduino": 9,
        "raspberry pi": 10,
        "linux": 11,
        "windows": 12,
        "hardware": 13,
        "software": 14,
        "iot": 15,
        "wearable": 16,
        "ollama": 17,
        "llm": 18,
        "numpy": 19,
        "scipy": 20,
        "opencv": 21,
        "flask": 22,
        "vite": 23,
        "esp32": 24,
        "micropython": 25,
        "multiprocessing": 26,
        "music theory": 27,
        "audio processing": 28,
        "computer vision": 29
    }

    @classmethod
    def encode_tags(cls, tag_list: list[str]) -> bytes:
        """
        Encode a list of tags into a binary representation stored as bytes.

        :param tag_list: List of tag names to encode.
        :return: Encoded tags as a byte object.
        """
        tag_int = 0
        for tag in tag_list:
            if tag in cls.TAGS:
                tag_int |= 1 << cls.TAGS[tag]
            else:
                raise ValueError(f"Tag '{tag}' is not recognized.")
        # Calculate the number of bytes required to store the bits
        num_bytes = (max(cls.TAGS.values()) // 8) + 1
        return tag_int.to_bytes(num_bytes, byteorder="big")

    @classmethod
    def decode_tags(cls, tag_bytes: bytes) -> list[str]:
        """
        Decode a binary representation of tags back into a list of tag names.

        :param tag_bytes: Encoded tags as a byte object.
        :return: List of decoded tag names.
        """
        tag_int = int.from_bytes(tag_bytes, byteorder="big")
        return [tag for tag, bit in cls.TAGS.items() if tag_int & (1 << bit)]

    @classmethod
    def has_tag(cls, tag_bytes: bytes, tag: str) -> bool:
        """
        Check if a specific tag is present in the encoded tag representation.

        :param tag_bytes: Encoded tags as a byte object.
        :param tag: Tag name to check for.
        :return: True if the tag is present, False otherwise.
        """
        if tag not in cls.TAGS:
            raise ValueError(f"Tag '{tag}' is not recognized.")
        tag_int = int.from_bytes(tag_bytes, byteorder="big")
        return bool(tag_int & (1 << cls.TAGS[tag]))

    @classmethod
    def add_tag(cls, tag_bytes: bytes, tag: str) -> bytes:
        """
        Add a tag to the encoded tag representation.

        :param tag_bytes: Encoded tags as a byte object.
        :param tag: Tag name to add.
        :return: New encoded tags with the tag added.
        """
        if tag not in cls.TAGS:
            raise ValueError(f"Tag '{tag}' is not recognized.")
        tag_int = int.from_bytes(tag_bytes, byteorder="big")
        tag_int |= 1 << cls.TAGS[tag]
        num_bytes = len(tag_bytes)
        return tag_int.to_bytes(num_bytes, byteorder="big")

    @classmethod
    def remove_tag(cls, tag_bytes: bytes, tag: str) -> bytes:
        """
        Remove a tag from the encoded tag representation.

        :param tag_bytes: Encoded tags as a byte object.
        :param tag: Tag name to remove.
        :return: New encoded tags with the tag removed.
        """
        if tag not in cls.TAGS:
            raise ValueError(f"Tag '{tag}' is not recognized.")
        tag_int = int.from_bytes(tag_bytes, byteorder="big")
        tag_int &= ~(1 << cls.TAGS[tag])
        num_bytes = len(tag_bytes)
        return tag_int.to_bytes(num_bytes, byteorder="big")

    @classmethod
    def list_available_tags(cls) -> list[str]:
        """
        List all available tags that can be encoded.

        :return: List of all tag names.
        """
        return list(cls.TAGS.keys())


class EntityJSON(TypedDict, total=False):
    uid: str
    created: str
    edited: str

class Entity(ABC):
    """
    A base class for all entities in the database.
    """

    __slots__ = ("_uid", "_created", "_edited")

    _uid: str
    _created: datetime
    _edited: datetime

    def __init__(
        self,
        uid: str = str(uuid4()),
        created: datetime = datetime.now(),
        edited: datetime = datetime.now(),
    ) -> None:
        self._uid = uid
        self._created = created
        self._edited = edited

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def edited(self) -> datetime:
        return self._edited

    @edited.setter
    def edited(self, value: datetime) -> None:
        self._edited = value

    def created_str(self) -> str:
        return dt2str(self._created)

    def edited_str(self) -> str:
        return dt2str(self._edited)

    def is_edited(self) -> bool:
        return self._edited != self._created
    
    def json(self) -> EntityJSON:
        {
            "uid": self._uid,
            "created": dt2str(self._created),
            "edited": dt2str(self._edited),
        }


class CommentJSON(EntityJSON):
    author: str
    title: str
    content: str

class Comment(Entity):
    """
    A class used to represent a timestamped Comment on a given Post.
    """

    __slots__ = (
        "_author",
        "_title",
        "_content"
    )

    def __init__(
        self,
        uid: str = str(uuid4()),
        author: str = "",
        title: str = "",
        content: str = "",
        created: datetime = datetime.now(),
        edited: datetime = datetime.now(),
    ) -> None:
        super().__init__(uid, created, edited)
        self._content = content
        self._title = title
        self._author = author

    @property
    def author(self) -> str:
        return self._author
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def content(self) -> str:
        return self._content

    def json(self) -> CommentJSON:
        out = super().json()
        out.update({
            "author": self._author,
            "title": self._title,
            "content": self._content
        })
        return out


class PostJSON(EntityJSON):
    title: str
    content: str
    tags: str
    comments: list[CommentJSON]

class Post(Entity):
    """
    A singular post within the website's blog.

    Attributes:
        _title : str
            title of the post
        _content : str
            content of the post
        _tags : bytes
            tags associated with the post
        _comments : list[Comments]
            list of comments on the post
    """

    __slots__ = (
        "_title",
        "_content",
        "_tags",
        "comments"
    )

    def __init__(
        self,
        uid: str = str(uuid4()),
        title: str = "",
        content: str = "",
        tags: bytes = bytes(0),
        created: datetime = datetime.now(),
        modified: datetime = datetime.now(),
        comments: list[Comment] | None = None,
    ) -> None:
        super().__init__(uid, created, modified)
        self._title = title
        self._content = content
        self._tags = tags
        self.comments = comments if comments else []

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value

    @property
    def tags(self) -> bytes:
        return self._tags

    @tags.setter
    def tags(self, value: bytes) -> None:
        self._tags = value

    def tags_str(self) -> str:
        return "".join(format(byte, "08b") for byte in self._tags)

    def json(self) -> PostJSON:
        out = super().json()
        out.update({
            "title": self._title,
            "content": self._content,
            "tags": TagManager.decode_tags(self._tags),
            "comments": [comment.json() for comment in self.comments],
        })
        return out


class GuestMessageJSON(EntityJSON, total=False):
    author: str
    content: str

class GuestMessage(Entity):

    __slots__ = (
        "_author",
        "_content"
    )

    def __init__(
        self,
        uid: str = str(uuid4()),
        created: datetime = datetime.now(),
        edited: datetime = datetime.now(),
        author: str = "",
        content: str = ""
    ) -> None:
        super.__init__(uid, created, edited)
        self._author = author
        self._content = content

    def json(self) -> GuestMessageJSON:
        out = super().json()
        out.update({
            "author": self._author,
            "content": self._content
        })