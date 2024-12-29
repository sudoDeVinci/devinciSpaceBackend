from sqlite3 import Cursor


def apply_schema(cursor: Cursor) -> None:
    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            username TEXT,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_online TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL DEFAULT 'VISITOR',
            );
            ''')

    # create the blogposts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogposts (
            title TEXT NOT NULL UNIQUE,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            modified TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL,
            tags INT NOT NULL DEFAULT 0,
            PRIMARY KEY (title, created)
        );
        ''')
