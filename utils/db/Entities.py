from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin
from enum import Enum
from functools import lru_cache


def dt2str(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y %I:%M%p")


class User(UserMixin):
    """
    A class used to represent a User.

    Attributes:
        id : str
            unique identifier for the user
        email : str
            email address of the user
        password : str
            password of the user
        username : str
            username of the user
        created : str
            creation timestamp of the user
        last_online : str
            last online timestamp of the user
        role : User.Role
            role of the user
    """

    __slots__ = ('_id',
                 '_email',
                 '_password',
                 '_username',
                 '_created',
                 '_last_online',
                 '_role')

    class Role(Enum):
        ADMIN = "admin"
        MEMBER = "member"
        VISITOR = "visitor"

        @classmethod
        @lru_cache(maxsize=None)
        def match(cls, role: str):
            """
            Match input string to user role.
            """
            role = role.lower()
            return cls[role] if role in cls.__members__.items() \
                else cls.VISITOR

        @classmethod
        @lru_cache(maxsize=None)
        def __contains__(cls, role: str) -> bool:
            """
            Check if a role is present in the enum.
            """
            return role.lower() in cls.__members__.values()

    _id: str = None
    _email: str = None
    _password: str = None
    _username: str = None
    _created: str = None
    _role: Role = Role.VISITOR
    _last_online: str = None

    def __init__(self,
                 id: str = str(uuid4()),
                 email: str = '',
                 username: str = f'Anon-{uuid4()}',
                 password: str = None,
                 role: str = Role.VISITOR,
                 created: str = dt2str(datetime.now()),
                 last_online: str = dt2str(datetime.now())):
        self._id = id
        self._email = email
        self._username = username
        self._password = password
        self._created = created
        self._last_online = last_online
        self._role = self.Role.match(role)

    @property
    def id(self) -> str:
        return self._id

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def role(self) -> str:
        return self._role

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @property
    def created(self) -> str:
        return self._created

    @property
    def last_online(self) -> str:
        return self._last_online

    @last_online.setter
    def last_online(self, value: str) -> None:
        self._last_online = value


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
        _id : str
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
    """
    __slots__ = ('_title',
                 '_created',
                 '_modified',
                 '_content',
                 '_tags')

    _title: str = None
    _created: datetime = None
    _modified: datetime = None
    _content: str = None
    _tags: bytes = 0b0

    def __init__(self,
                 id: str = str(uuid4()),
                 title: str = '',
                 content: str = '',
                 tags: bytes = 0b0,
                 created: str = dt2str(datetime.now()),
                 modified: str = dt2str(datetime.now())):
        self._id = id
        self._title = title
        self._content = content
        self._tags = tags
        self._created = created
        self._modified = created

    @property
    def id(self) -> str:
        return self._id

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
    def created(self) -> str:
        return self._created

    @property
    def modified(self) -> str:
        return self._modified

    @modified.setter
    def modified(self, value: str) -> None:
        self._modified = value
