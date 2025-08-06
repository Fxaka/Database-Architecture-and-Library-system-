import psycopg2
from configparser import ConfigParser


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Establish database connection"""
        try:
            params = self._config()
            self.conn = psycopg2.connect(**params)

            # Test connection
            with self.conn.cursor() as cur:
                cur.execute("SELECT version()")
                print("Database connection established successfully")
            return self.conn

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Connection failed: {error}")
            return None

    def _config(self, filename='database.ini', section='postgresql'):
        """Read database configuration with improved error handling"""
        import os
        from pathlib import Path

        # Get absolute path to config file
        config_path = Path(__file__).parent / filename

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at: {config_path}\n"
                f"Current working directory: {os.getcwd()}\n"
                f"Please create {filename} with [postgresql] section"
            )

        parser = ConfigParser()
        parser.read(config_path)

        if not parser.has_section(section):
            available_sections = parser.sections()
            raise ValueError(
                f"Section '[{section}]' not found in {config_path}\n"
                f"Available sections: {available_sections}\n"
                f"File content:\n{config_path.read_text()}"
            )

        return {param[0]: param[1] for param in parser.items(section)}

    def disconnect(self):
        """Close database connection"""
        if self.conn is not None:
            self.conn.close()
            print("Database connection closed")