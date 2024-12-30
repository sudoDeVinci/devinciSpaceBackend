from datetime import datetime
from uuid import uuid4


class Comment:
    """
    A class used to represent a timestamped Comment on a given Post.
    """

    __slots__ = ('uid',
                 'title',
                 'content',
                 'author',
                 'created',
                 'edited')

    def __init__(self,
                 uid: str = str(uuid4()),
                 author: str = '',
                 title: str = '',
                 content: str = '',
                 created: datetime = datetime.now(),
                 edited: datetime = datetime.now()
                 ) -> None:
        self.uid = uid
        self.content = content
        self.title = title
        self.author = author
        self.created = created
        self.edited = edited


class TagManager:
    """
    A utility class to manage tags using binary encoding stored as bytes.
    This class provides class methods to encode and decode tags, as well as
    perform tag-based operations efficiently.
    """

    __slots__ = ('TAGS')

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
        "Arduino": 9,
        "Raspberry Pi": 10,
        "Linux": 11,
        "Windows": 12,
        "hardware": 13,
        "software": 14
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
                tag_int |= (1 << cls.TAGS[tag])
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
        return [
            tag for tag, bit in cls.TAGS.items() if tag_int & (1 << bit)
        ]

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
        tag_int |= (1 << cls.TAGS[tag])
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


class Post:
    """
    A class used to represent a Post.

    Attributes:
        _uid : str
            unique identifier for the post
        _title : str
            title of the post
        _created : str
            creation timestamp of the post
        _modified : str
            last modified timestamp of the post
        _content : str
            content of the post
        _tags : bytes
            tags associated with the post
        _comments : list[Comments]
            list of comments on the post
    """
    __slots__ = ('_title',
                 '_created',
                 '_modified',
                 '_content',
                 '_tags',
                 '_uid',
                 '_comments')

    _title: str = None
    _created: datetime = None
    _modified: datetime = None
    _content: str = None
    _tags: bytes = 0b0
    _uid: str = None
    _comments: list[Comment] = []

    def __init__(self,
                 uid: str = str(uuid4()),
                 title: str = '',
                 content: str = '',
                 tags: bytes = 0b0,
                 created: str = datetime.now(),
                 modified: str = datetime.now(),
                 comments: list[Comment] = []
                 ) -> None:
        self._uid = uid
        self._title = title
        self._content = content
        self._tags = tags
        self._created = created
        self._modified = modified
        self._comments = comments

    @property
    def comments(self) -> list[Comment]:
        return self._comments

    def add_comment(self, comment: Comment) -> None:
        self._comments.append(comment)

    @property
    def uid(self) -> str:
        return self._uid

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

    @property
    def created(self) -> datetime:
        return self._created

    def created_str(self) -> str:
        return self._created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def modified(self) -> datetime:
        return self._modified

    def modified_str(self) -> str:
        return self._modified.strftime("%Y-%m-%d %H:%M:%S")

    @modified.setter
    def modified(self, value: str) -> None:
        self._modified = value
