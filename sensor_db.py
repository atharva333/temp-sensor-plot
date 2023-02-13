from datetime import datetime
import abc
import sqlite3


class BaseSensorDB(abc.ABC):
    """
    Abstract class for creating sensor reading which writes to database
    """

    def __init__(self):
        ## Set database filepath
        self.database_filepath = "example_sensor.db"

    def _create_db_table(self, table_name="data"):
        # Connect to the database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(self.database_filepath)
        self.conn_cursor = self.conn.cursor()

        # Create a table with timestamp, temperature, humidity fields
        self.conn_cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp datetime, temperature real, humidity real)"
        )
        self.conn.commit()

        self.conn.close()

    @abc.abstractmethod
    def get_new_reading(self) -> bool:
        """
        Interface for inserting new reading into db table
        """
        # Connect to the database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(self.database_filepath)
        self.conn_cursor = self.conn.cursor()

        ## .... get sensor data ....
        timestamp = datetime.now()
        temperature_reading = 0.00
        humidity_reading = 0.00

        # Create a table with timestamp, temperature, humidity fields
        self.conn_cursor.execute(
            "INSERT INTO data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
            (timestamp, temperature_reading, humidity_reading),
        )
        self.conn.commit()

        self.conn.close()

        return True
