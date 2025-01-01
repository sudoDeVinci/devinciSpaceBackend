from abc import ABC, abstractmethod
from server.db.manager import Manager
from server.db.entities import Entity, Post, Comment, str2dt, dt2str
from sqlite3 import Error as SQLError
from logging import ERROR
from datetime import datetime
from typing import TypeVar, Generic, List


Ent = TypeVar("Ent", bound=Entity)


class Service(ABC, Generic[Ent]):
    """
    Abstract class for database services.
    This is the minimum interface that a database
    service must implement.
    """

    @abstractmethod
    def insert(**kwargs) -> None:
        """
        Insert a new entity into the database.
        """
        pass

    @abstractmethod
    def get(**kwargs) -> Ent | None:
        """
        Get an entity from the database.
        """
        pass

    @abstractmethod
    def list(**kwargs) -> List[Ent]:
        """
        List all entities in the database.
        """
        pass

    @abstractmethod
    def update(**kwargs) -> None:
        """
        Update an entity in the database.
        """
        pass

    @abstractmethod
    def delete(**kwargs) -> None:
        """
        Delete an entity from the database.
        """
        pass


class CommentService(Service):
    @staticmethod
    def get(**kwargs) -> Comment | None:
        """
        Get a Comment entity from the database by its uid.

        Args:
        - commentid (str):
            unique identifier for the comment

        Returns:
            - Comment | None:
                Comment entity if found, None otherwise
        """
        result: Comment | None = None
        commentid: str | None = kwargs.get("commentid", None)
        if not commentid:
            Manager.log("No comment id provided.", level=ERROR)
            return result
        query = "SELECT * FROM comments WHERE uid = ?;"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
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
                    edited=str2dt(data[6]),
                )
        except SQLError as err:
            Manager.log(f"Error getting comment: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def list(**kwargs) -> List[Comment]:
        """
        List all comments for a given post.

        Args:
            - postid (str):
                unique identifier for the post

        Returns:
            - List[Comment]:
                list of comments for the post
        """
        result: List[Comment] = []
        postid: str | None = kwargs.get("postid", None)
        if not postid:
            Manager.log("No post id provided.", level=ERROR)
            return result
        query = (
            "SELECT * FROM comments WHERE post_uid = ? "
            "ORDER BY created DESC;"
        )

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return result

            cursor.execute(query, (postid,))
            data = cursor.fetchall()
            for row in data:
                result.append(
                    Comment(
                        uid=row[0],
                        author=row[2],
                        title=row[3],
                        content=row[4],
                        created=str2dt(row[5]),
                        edited=str2dt(row[6]),
                    )
                )
        except SQLError as err:
            Manager.log(f"Error listing comments: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def insert(**kwargs) -> None:
        """
        Insert a new Comment entity into the database.

        Args:
            - comment (Comment):
                Comment entity to insert
        """
        comment: Comment | None = kwargs.get("comment", None)
        post_uid: str | None = kwargs.get("post_uid", None)

        if not comment:
            Manager.log("No comment provided.", level=ERROR)
            return

        if not post_uid:
            Manager.log("No post id provided.", level=ERROR)
            return

        query = "INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?);"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return

            cursor.execute(
                query,
                (
                    comment.uid,
                    post_uid,
                    comment.author,
                    comment.title,
                    comment.content,
                    comment.created_str(),
                    comment.edited_str(),
                ),
            )
        except SQLError as err:
            Manager.log(f"Error inserting comment: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def insert_batch(**kwargs) -> None:
        """
        Insert a batch of Comment entities into the database.

        Args:
            - comments (List[Comment]):
                list of Comment entities to insert
            - postid (str):
                unique identifier for the post
        """
        comments: List[Comment] | None = kwargs.get("comments", None)
        postid: str | None = kwargs.get("postid", None)
        if not comments:
            Manager.log("No comments provided.", level=ERROR)
            return
        if not postid:
            Manager.log("No post id provided.", level=ERROR)
            return
        query = "INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?);"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return

            comment_data = tuple(
                (
                    c.uid,
                    postid,
                    c.author,
                    c.title,
                    c.content,
                    c.created_str(),
                    c.edited_str(),
                )
                for c in comments
            )

            cursor.executemany(query, comment_data)
        except SQLError as err:
            Manager.log(f"Error inserting comments: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def update(**kwargs) -> None:
        """
        Update a Comment entity in the database.

        Args:
            - comment (Comment):
                Comment entity to update
        """
        comment: Comment | None = kwargs.get("comment", None)
        if not comment:
            Manager.log("No comment provided.", level=ERROR)
            return
        query = (
            "UPDATE comments SET author = ?, title = ?,"
            " content = ?, edited = ? WHERE uid = ?;"
        )

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return

            cursor.execute(
                query,
                (
                    comment.author,
                    comment.title,
                    comment.content,
                    comment.edited_str(),
                    comment.uid,
                ),
            )
        except SQLError as err:
            Manager.log(f"Error updating comment: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def delete(**kwargs) -> None:
        """
        Delete a Comment entity from the database.

        Args:
            - comment (Comment):
                Comment entity to delete
        """
        comment: Comment | None = kwargs.get("comment", None)
        if not comment:
            Manager.log("No comment provided.", level=ERROR)
            return
        query = "DELETE FROM comments WHERE uid = ?;"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return

            cursor.execute(query, (comment.uid,))
        except SQLError as err:
            Manager.log(f"Error deleting comment: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()


class PostService(Service):
    @staticmethod
    def list(**kwargs) -> List[Post]:
        """
        List all posts in the database.
        Return them in order of creation.

        Returns:
            - List[Post]:
                list of all posts in the database
        """
        result: List[Post] = []
        limit: int = kwargs.get("limit", 20)
        page: int = kwargs.get("page", 0)
        offset = page * limit

        query = (
            "SELECT * FROM blogposts ORDER BY created DESC "
            "LIMIT ? OFFSET ?;"
        )

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return result

            cursor.execute(
                query,
                (
                    limit,
                    offset,
                ),
            )
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                bit_length = (binary.bit_length() + 7) // 8
                binbytes = binary.to_bytes(bit_length, "big")
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes,
                )
                post.comments.extend(CommentService.list(postid=row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f"Error listing posts: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def insert(**kwargs) -> None:
        """
        Insert a new Post entity into the database.

        Args:
            - post (Post):
                Post entity to insert
        """
        post: Post | None = kwargs.get("post", None)
        if post is None:
            Manager.log("No post provided.", level=ERROR)
            return
        query = "INSERT INTO blogposts VALUES (?, ?, ?, ?, ?, ?);"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return

            cursor.execute(
                query,
                (
                    post.uid,
                    post.title,
                    post.content,
                    post.created_str(),
                    post.edited_str(),
                    post.tags_str(),
                ),
            )
            CommentService.insert_batch(
                postid=post.uid, comments=post.comments
            )
        except SQLError as err:
            Manager.log(f"Error inserting post: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_by_date(**kwargs) -> List[Post]:
        """
        Get a Post from the database by its creation date.

        Args:
            - date (datetime):
                date of creation

        Returns:
            - List[Post]:
                list of posts created on the given date
        """
        result: List[Post] = []
        dt: datetime | None = kwargs.get("date", None)
        if not dt:
            Manager.log("No date provided.", level=ERROR)
            return result
        query = "SELECT * FROM blogposts WHERE created = ?;"

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return result

            cursor.execute(
                query,
                dt2str(dt),
            )
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                bit_length = (binary.bit_length() + 7) // 8
                binbytes = binary.to_bytes(bit_length, "big")
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes,
                )
                post.comments.extend(CommentService.list(postid=row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f"Error getting post by date: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result

    @staticmethod
    def get_by_daterange(**kwargs) -> List[Post]:
        """
        Get a list of Posts from the database by a date range.
        We can also specify a limit and offset for pagination.
        """
        dt1: datetime | None = kwargs.get("date1", None)
        dt2: datetime | None = kwargs.get("date2", None)
        limit: int = kwargs.get("limit", 20)
        page: int = kwargs.get("page", 0)
        result: list[Post] = []
        offset = page * limit

        if not dt1 or not dt2:
            Manager.log("Invalid date range provided.", level=ERROR)
            return result

        query = (
            "SELECT * FROM blogposts WHERE created BETWEEN ? AND ? "
            "LIMIT ? OFFSET ?;"
        )

        try:
            cursor = Manager.cursor()
            if not cursor:
                Manager.log("Failed to get cursor.", level=ERROR)
                return result

            cursor.execute(
                query,
                (
                    dt2str(dt1),
                    dt2str(dt2),
                    limit,
                    offset,
                ),
            )
            data = cursor.fetchall()
            for row in data:
                binary = int(row[5], 2)
                bit_length = (binary.bit_length() + 7) // 8
                binbytes = binary.to_bytes(bit_length, "big")
                post = Post(
                    uid=row[0],
                    title=row[1],
                    content=row[2],
                    created=str2dt(row[3]),
                    modified=str2dt(row[4]),
                    tags=binbytes,
                )
                post.comments.extend(CommentService.list(postid=row[0]))
                result.append(post)
        except SQLError as err:
            Manager.log(f"Error getting post: {err}", level=ERROR)
        finally:
            if cursor:
                cursor.close()
            return result
