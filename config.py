import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", 3600))
    
    # ============================
    # DATABASE CONFIG
    # ============================
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
    
    if DB_ENGINE == "mssql":
        # Example env vars:
        # DB_USER : User
        # DB_PASSWORD : Password
        # DB_HOST : Public IP
        # DB_PORT : Port
        # DB_NAME : DB name
        # ODBC_DRIVER : Driver
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
        DB_PORT = os.getenv("DB_PORT", "1433")
        DB_NAME = os.getenv("DB_NAME")
        ODBC_DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

        # create ODBC connection string
        odbc_str = (
            f"DRIVER={{{ODBC_DRIVER}}};"
            f"SERVER={DB_HOST},{DB_PORT};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            "TrustServerCertificate=yes;"
        )

        # encode for SQLAlchemy
        params = urllib.parse.quote_plus(odbc_str)
        SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"

    else:
        # default fallback (SQLite)
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./dev.db")