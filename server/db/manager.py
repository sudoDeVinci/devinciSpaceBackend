from queue import Queue
from sqlite3 import connect, Connection, Cursor, Error as SQLError
from threading import Lock
from typing import Optional, Generator
from pathlib import Path
import json
from logging import INFO, FileHandler, Logger, StreamHandler, basicConfig, getLogger
from contextlib import contextmanager
from .schema import apply_schema


class SQLiteConnectionPool:
    """
    A thread-safe connection pool for SQLite database connections.

    Attributes:
        size (int): Maximum number of connections in the pool
        timeout (float): Timeout in seconds for getting a connection
        database (str): Path to the SQLite database file
    """

    def __init__(self, database: str, size: int = 5, timeout: float = 30.0):
        self.database = database
        self.size = size
        self.timeout = timeout
        self._pool: Queue[Connection] = Queue(maxsize=size)
        self._lock = Lock()
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the connection pool with the specified number of connections."""
        for _ in range(self.size):
            conn = connect(
                database=self.database,
                timeout=self.timeout,
                check_same_thread=False,  # Required for multi-threaded access
            )
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 30000")
            self._pool.put(conn)

    def get_connection(self) -> Optional[Connection]:
        """Get a connection from the pool."""
        try:
            return self._pool.get(timeout=self.timeout)
        except Exception as e:
            print(f"Error getting connection from pool: {e}")
            return None

    def return_connection(self, connection: Connection) -> None:
        """Return a connection to the pool."""
        try:
            self._pool.put(connection, timeout=self.timeout)
        except Exception as e:
            print(f"Error returning connection to pool: {e}")
            connection.close()

    def closeall(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()


class Manager:
    """
    Static Management class for Database configuration.
    """

    _pool: Optional[SQLiteConnectionPool] = None
    _configfile: Path = Path("configs") / "config.json"
    _dbfile: Path = Path(__file__) / "database.db"
    _logfile: Path = Path("logs") / "server.db.log"
    logger: Logger

    @classmethod
    def log(cls, message: str, level: int = INFO) -> None:
        """Log a message to the logger."""
        if not hasattr(cls, "logger"):
            cls.load()
        cls.logger.log(level, message)

    @classmethod
    def load(cls) -> None:
        """Load the configuration and logger objects."""
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("configs").mkdir(exist_ok=True)

        basicConfig(
            level=INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                StreamHandler(),
                FileHandler(str(cls._logfile)),
            ],
        )
        cls.logger = getLogger(__name__)

        try:
            with open(cls._configfile, "r") as file:
                data = json.load(file)
                # TODO: Load configuration data
                if not data:
                    raise json.JSONDecodeError("Empty file", str(cls._configfile), 0)
        except FileNotFoundError as err:
            cls.log(f"Error loading configuration: {err}")
        except json.JSONDecodeError as err:
            cls.log(f"Error parsing configuration: {err}")

    @classmethod
    def connected(cls) -> bool:
        """Check if the database is connected."""
        return cls._pool is not None

    @classmethod
    def connect(cls) -> None:
        """Connect to the SQLite database using the connection pool."""
        cls.load()
        try:
            cls._pool = SQLiteConnectionPool(
                database=str(cls._dbfile),
                size=5,  # Adjust pool size as needed
                timeout=10.0,
            )

            with cls.cursor() as cursor:
                if cursor is None:
                    raise ValueError("Cursor is required")
                apply_schema(cursor)
                cursor.connection.commit()
        except SQLError as err:
            cls._pool = None
            cls.log(f"Error connecting to the database: {err}")

    @classmethod
    @contextmanager
    def connection(cls) -> Generator[Optional[Connection], None, None]:
        """
        Get a connection from the pool. Can be used as a context manager.

        Returns:
        --------
            Connection: Connection object from the SQLite database pool.

        Usage:
        ------
            # As a context manager:
            with Manager.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")

            # Or traditional way:
            conn = Manager.connection()
            try:
                # use connection
                pass
            finally:
                if conn and cls._pool:
                    cls._pool.return_connection(conn)
        """
        if not cls.connected():
            cls.connect()

        conn = cls._pool.get_connection() if cls._pool else None
        try:
            yield conn
        finally:
            if conn and cls._pool:
                cls._pool.return_connection(conn)

    @classmethod
    @contextmanager
    def cursor(cls) -> Generator[Optional[Cursor], None, None]:
        """
        Get a cursor from a pooled connection. Can be used as a context manager.

        Returns:
        --------
            Cursor: Cursor object from the SQLite database connection.

        Usage:
        ------
            # As a context manager:
            with Manager.cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()

            # Or traditional way:
            cursor = Manager.cursor()
            try:
                # use cursor
                pass
            finally:
                if cursor and cursor.connection and cls._pool:
                    cls._pool.return_connection(cursor.connection)
        """
        with cls.connection() as conn:
            if conn:
                cursor = conn.cursor()
                try:
                    yield cursor
                    conn.commit()  # Auto-commit successful transactions
                except Exception:
                    conn.rollback()  # Rollback on error
                    raise
            else:
                yield None

    @classmethod
    def close(cls) -> None:
        """Close all connections in the pool."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
