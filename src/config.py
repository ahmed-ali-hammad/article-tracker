class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:password@article-tracker-db:5432/article"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "super_secure"

    FLASK_RUN_HOST = "0.0.0.0"
    FLASK_RUN_PORT = 5000
    DEBUG = True
