"""Conector MySQL: credenciales por variables de entorno y rutas portables."""
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import pymysql

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class MySQLConnector:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME")

    def _validate(self):
        missing = [key for key, value in {
            "DB_USER": self.user, "DB_NAME": self.database
        }.items() if not value]
        if missing:
            raise RuntimeError(
                "Configura estas variables en el archivo .env: " + ", ".join(missing)
            )

    def get_connection(self):
        self._validate()
        return pymysql.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, database=self.database,
            connect_timeout=10, read_timeout=30, write_timeout=30,
            charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

    def extract_data(self, query, params=None):
        """Ejecuta una consulta de lectura y devuelve un DataFrame."""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
            return pd.DataFrame(rows)
        finally:
            connection.close()
