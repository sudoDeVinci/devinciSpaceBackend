from abc import ABC, abstractmethod
from utils.db.manager import Manager
from utils.db.entities import Post, Comment
from sqlite3 import Error as SQLError
from logging import ERROR


class Service(ABC):
    """
    Abstract class for database services.
    This is the minimum interface that a database
    service must implement.
    """
    @abstractmethod
    def insert(cls, **kwargs):
        """
        Insert a new entity into the database.
        """
        pass

    @abstractmethod
    def get(cls, **kwargs):
        """
        Get an entity from the database.
        """
        pass

    @abstractmethod
    def list(cls, **kwargs):
        """
        List all entities in the database.
        """
        pass

    @abstractmethod
    def update(cls, **kwargs):
        """
        Update an entity in the database.
        """
        pass

    @abstractmethod
    def delete(cls, **kwargs):
        """
        Delete an entity from the database.
        """
        pass


class CommentService(Service):
    @staticmethod
    def get(commentid: str) -> Comment | None:
        """
        Get a Comment entity from the database by its uid.
        """
        query = 'SELECT * FROM comments WHERE uid = ?;'
        result: Comment | None = None

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return None

            cursor.execute(query, (commentid,))
            data = cursor.fetchone()
            if data:
                result = Comment(
                    uid=data[0],
                    author=data[2],
                    title=data[3],
                    content=data[4],
                    created=data[5],
                    edited=data[6]
                )
        except SQLError as err:
            Manager.log(f'Error getting comment: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result
