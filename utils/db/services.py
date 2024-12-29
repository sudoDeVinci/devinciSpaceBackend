from abc import ABC, abstractmethod
from utils.db.manager import Manager
from utils.db.entities import User
from sqlite3 import Error as SQLError


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


class UserService(Service):

    @classmethod
    def get(cls, id: str):
        """
        Get a user from the database.
        """
        query = 'SELECT * FROM users WHERE id = ?'
        cursor = None
        try:
            cursor = Manager.get_cursor()
            if not cursor:
                Manager.logger.exception(
                    'Failed to get cursor - check connection.'
                )
                return None
            cursor.execute(query, (id,))
            row = cursor.fetchone()

            if row:
                user = User(
                    id=row['id'],
                    email=row['email'],
                    username=row['username'],
                    password=row['password'],
                    role=row['role'],
                    created=row['created'],
                    last_online=row['last_online']         
                )
        except SQLError as err:
            Manager.logger.exception(f'Error getting user: {err}')
            return None
        finally:
            if cursor:
                cursor.close()

        return user
