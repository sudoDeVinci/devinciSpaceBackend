from abc import ABC, abstractmethod
from utils.db.manager import Manager
from utils.db.entities import Entity, Post, Comment, str2dt, dt2str
from sqlite3 import Error as SQLError
from logging import ERROR
from datetime import datetime


class Service(ABC):
    """
    Abstract class for database services.
    This is the minimum interface that a database
    service must implement.
    """
    @abstractmethod
    def insert(cls, **kwargs) -> None:
        """
        Insert a new entity into the database.
        """
        pass

    @abstractmethod
    def get(cls, **kwargs) -> Entity | None:
        """
        Get an entity from the database.
        """
        pass

    @abstractmethod
    def list(cls, **kwargs) -> list[Entity]:
        """
        List all entities in the database.
        """
        pass

    @abstractmethod
    def update(cls, **kwargs) -> None:
        """
        Update an entity in the database.
        """
        pass

    @abstractmethod
    def delete(cls, **kwargs) -> None:
        """
        Delete an entity from the database.
        """
        pass


class CommentService(Service):
    @staticmethod
    def get(commentid: str) -> Comment | None:
        """
        Get a Comment entity from the database by its uid.

        Args:
        - commentid (str):
            unique identifier for the comment

        Returns:
            - Comment | None:
                Comment entity if found, None otherwise
        """
        query = 'SELECT * FROM comments WHERE uid = ?;'
        result: Comment | None = None

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return result

            cursor.execute(query, (commentid,))
            data = cursor.fetchone()
            if data:
                result = Comment(
                    uid=data[0],
                    author=data[2],
                    title=data[3],
                    content=data[4],
                    created=str2dt(data[5]),
                    edited=str2dt(data[6])
                )
        except SQLError as err:
            Manager.log(f'Error getting comment: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def list(postid: str) -> list[Comment]:
        """
        List all comments for a given post.

        Args:
            - postid (str):
                unique identifier for the post

        Returns:
            - list[Comment]:
                list of comments for the post
        """
        query = ('SELECT * FROM comments WHERE post_uid = ? '
                 'ORDER BY created DESC;')
        result: list[Comment] = []

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return result

            cursor.execute(query, (postid,))
            data = cursor.fetchall()
            for row in data:
                result.append(Comment(
                    uid=row[0],
                    author=row[2],
                    title=row[3],
                    content=row[4],
                    created=str2dt(row[5]),
                    edited=str2dt(row[6])
                ))
        except SQLError as err:
            Manager.log(f'Error listing comments: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def insert(post_uid: str, comment: Comment) -> None:
        """
        Insert a new Comment entity into the database.

        Args:
            - comment (Comment):
                Comment entity to insert
        """
        query = 'INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?);'

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return

            cursor.execute(query, (
                comment.uid,
                post_uid,
                comment.author,
                comment.title,
                comment.content,
                comment.created_str(),
                comment.edited_str()
            ))
        except SQLError as err:
            Manager.log(f'Error inserting comment: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def insert_batch(postid: str, comments: list[Comment]) -> None:
        """
        Insert a batch of Comment entities into the database.
        """
        query = 'INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?);'

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return

            comment_data = tuple(
                (c.uid,
                 postid,
                 c.author,
                 c.title,
                 c.content,
                 c.created_str(),
                 c.edited_str()
                 ) for c in comments
            )

            cursor.executemany(query, comment_data)
        except SQLError as err:
            Manager.log(f'Error inserting comments: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def update(comment: Comment) -> None:
        """
        Update a Comment entity in the database.

        Args:
            - comment (Comment):
                Comment entity to update
        """
        query = ('UPDATE comments SET author = ?, title = ?,'
                 ' content = ?, edited = ? WHERE uid = ?;')

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return

            cursor.execute(query, (
                comment.author,
                comment.title,
                comment.content,
                comment.edited_str(),
                comment.uid
            ))
        except SQLError as err:
            Manager.log(f'Error updating comment: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def delete(comment: Comment) -> None:
        """
        Delete a Comment entity from the database.

        Args:
            - comment (Comment):
                Comment entity to delete
        """
        query = 'DELETE FROM comments WHERE uid = ?;'

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return

            cursor.execute(query, (comment.uid,))
        except SQLError as err:
            Manager.log(f'Error deleting comment: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()


class PostService(Service):
    @staticmethod
    def list(limit: int = 20, page: int = 0) -> list[Post]:
        """
        List all posts in the database.
        Return them in order of creation.

        Returns:
            - list[Post]:
                list of all posts in the database
        """
        query = (
            'SELECT * FROM blogposts ORDER BY created DESC '
            'LIMIT ? OFFSET ?;'
        )
        result: list[Post] = []
        offset = page * limit

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return result

            cursor.execute(query, (limit, offset,))
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                binbytes = binary.to_bytes(
                    (binary.bit_length() + 7) // 8, 'big'
                    )
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes
                )
                post.comments.extend(CommentService.list(row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f'Error listing posts: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def insert(post: Post) -> None:
        """
        Insert a new Post entity into the database.
        """
        query = 'INSERT INTO blogposts VALUES (?, ?, ?, ?, ?, ?);'

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return

            cursor.execute(query, (
                post.uid,
                post.title,
                post.content,
                post.created_str(),
                post.modified_str(),
                post.tags_str()
            ))
            CommentService.insert_batch(post.uid, post.comments)
        except SQLError as err:
            Manager.log(f'Error inserting post: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_by_date(dt: datetime) -> list[Post]:
        """
        Get a Post from the database by its creation date.
        """
        query = 'SELECT * FROM blogposts WHERE created = ?;'
        result: list[Post] = []

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return result

            cursor.execute(query, dt2str(dt),)
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                binbytes = binary.to_bytes(
                    (binary.bit_length() + 7) // 8, 'big'
                    )
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes
                )
                post.comments.extend(CommentService.list(row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f'Error getting post by date: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def get_by_daterange(dt1: datetime,
                         dt2: datetime,
                         limit: int = 20,
                         page: int = 0) -> list[Post]:
        """
        Get a list of Posts from the database by a date range.
        We can also specify a limit and offset for pagination.
        """
        query = ('SELECT * FROM blogposts WHERE '
                 'created BETWEEN ? AND ? LIMIT ? OFFSET ?;')
        result: list[Post] = []
        offset = page * limit

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log('Failed to get cursor.', level=ERROR)
                return result

            cursor.execute(query, (dt2str(dt1), dt2str(dt2), limit, offset,))
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                binbytes = binary.to_bytes(
                    (binary.bit_length() + 7) // 8, 'big'
                    )
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes
                )
                post.comments.extend(CommentService.list(row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f'Error getting post by date range: {err}', level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result
