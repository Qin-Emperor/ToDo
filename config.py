import os


class Config:
    # General Config
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail Config
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Celery Config
    CELERY_BROKER_URL = os.environ.get("BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("RESULT_BACKEND")

    # JWT Config
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_VERIFY_SUB = False