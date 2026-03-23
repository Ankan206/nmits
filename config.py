import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

    # Build MySQL URI or fall back to SQLite
    MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT     = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER     = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'nmits_db')

    if MYSQL_PASSWORD:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
    else:
        # SQLite fallback for quick local dev
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL', 'sqlite:///nmits.db'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
