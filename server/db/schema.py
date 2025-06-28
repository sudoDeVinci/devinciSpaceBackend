from sqlite3 import Cursor


def apply_schema(cursor: Cursor | None) -> None:
    if cursor is None:
        raise ValueError("Cursor is required")
    # create the blogposts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blogposts (
            uid TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            modified TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            tags TEXT NOT NULL DEFAULT 0
        );
        """
    )

    # create the comments table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            uid TEXT PRIMARY KEY,
            post_uid TEXT NOT NULL REFERENCES blogposts(uid),
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            edited TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS guestbook (
            uid TEXT PRIMARY KEY,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            edited TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

