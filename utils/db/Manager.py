from sqlite3 import (connect as sqlconnect,
                     Connection,
                     Cursor,
                     Error as SQLError)
from pathlib import Path
import json
from utils.db.schema import apply_schema
from logging import (
    INFO,
    FileHandler,
    Logger,
    StreamHandler,
    basicConfig
)


class Manager:
    """
    Static Management class for Database configuration.

    Attributes:
    -----------
        _connection (Connection):
            Connection object to the SQLite database.
        _dbfile (Path):
            Path to the database file.
        _logfile (Path):
            Path to the log file.
        logger (Logger):
            Logger object for logging messages.
    """
    _connection: Connection | None = None
    _configfile: Path = Path('configs') / 'config.json'
    _dbfile: Path = Path('utils') / 'db' / 'database.db'
    _logfile: Path = Path('logs') / 'db.log'
    logger: Logger | None = None

    @classmethod
    def log(cls, message: str, level: int = INFO) -> None:
        """
        Log a message to the logger.

        Args:
        -----------
            message (str):
                Message to log.
            level (int):
                Level of the message to log.
        """
        if not cls.logger:
            cls.load()

        cls.logger.log(level, message)

    @classmethod
    def load(cls) -> None:
        """
        Load the configuration and logger objects.
        """

        # Create necessary directories
        Path('logs').mkdir(exist_ok=True)
        Path('configs').mkdir(exist_ok=True)
        cls.logger = basicConfig(
            level=INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                StreamHandler(),
                FileHandler(str(cls._logfile)),
            ],
        )

        data = None

        try:
            with open(cls._configfile, 'r') as file:
                data = json.load(file)
                if not data:
                    raise json.JSONDecodeError("Empty file",
                                               cls._configfile,
                                               0)
        except FileNotFoundError as err:
            cls.log(f"Error loading configuration: {err}")
            return {}
        except json.JSONDecodeError as err:
            cls.log(f"Error parsing configuration: {err}")
            return {}

        return data

    @classmethod
    def connected(cls) -> bool:
        """
        Check if the database is connected.

        Returns:
        --------
            bool:
                True if connected, False otherwise.
        """
        return cls._connection is not None

    @classmethod
    def connection(cls) -> Connection | None:
        """
        Get the connection object to the database.

        Returns:
        --------
            Connection:
                Connection object to the SQLite database.
        """
        if not cls.connected():
            cls.connect()
        return cls._connection

    @classmethod
    def cursor(cls) -> Cursor | None:
        """
        Get the cursor object to the database.

        Returns:
        --------
            Cursor:
                Cursor object to the SQLite database.
        """
        return cls.connection().cursor if cls.connected() else None

    @classmethod
    def connect(cls) -> None:
        """
        Connect to the SQLite database.
        """

        cls.load()

        try:
            cls._connection = sqlconnect(str(cls._dbfile))

            if not cls._dbfile.exists():
                cursor = cls._connection.cursor()
                apply_schema(cursor)
                cls._connection.commit()

        except SQLError as err:
            cls._connection = None
            print(f"Error connecting to the database: {err}")
