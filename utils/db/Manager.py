from sqlite3 import (connect as sqlconnect,
                     Connection,
                     Error as SQLError)
from pathlib import Path
from typing import Optional
from utils.db.scehma import apply_schema
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
        _configfile (Path):
            Path to the configuration file.
        _dbfile (Path):
            Path to the database file.
        _logfile (Path):
            Path to the log file.
        logger (Logger):
            Logger object for logging messages.
    """
    _connection: Optional[Connection] = None
    _configfile: Path = Path(__file__).parent.parent / 'configs' / 'db.json'
    _dbfile: Path = Path('database.db')
    _logfile: Path = Path(__file__).parent.parent / 'logs' / 'db.log'
    logger: Logger = None

    @classmethod
    def log(cls, message: str, level: int = INFO) -> None:
        """
        Log a message to the logger.

        Parameters:
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
        if not cls._configfile.exists():
            cls._configfile.touch()
        if not cls._dbfile.exists():
            cls._dbfile.touch()
        if not cls._logfile.exists():
            cls._logfile.touch()

        cls.logger = basicConfig(
            level=INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                StreamHandler(),
                FileHandler('db.log'),
            ],
        )

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
    def connection(cls) -> Connection:
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
    def cursor(cls):
        """
        Get the cursor object to the database.

        Returns:
        --------
            Cursor:
                Cursor object to the SQLite database.
        """
        return cls.connection() if cls.connected() else None

    @classmethod
    def connect(cls) -> None:
        """
        Connect to the SQLite database.
        """

        cls.load()

        try:
            cls._connection = sqlconnect(cls._dbfile)
            cls._connection.row_factory = sqlconnect.Row

            if not cls._dbfile.exists():
                cursor = cls._connection.cursor()
                apply_schema(cursor)
                cls._connection.commit()

        except SQLError as err:
            cls._connection = None
            print(f"Error connecting to the database: {err}")
