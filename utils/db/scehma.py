from sqlite3 import Cursor


def apply_schema(cursor: Cursor) -> None:
    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_online TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL DEFAULT 'VISITOR',
            );
            ''')

    # create the blogposts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogposts (
            Title TEXT NOT NULL UNIQUE,
            Date TEXT NOT NULL,
            Content TEXT NOT NULL,
            Tags TEXT,
            PRIMARY KEY (Title, Date)
        );
        ''')
