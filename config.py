import os


basedir = os.path.abspath(os.path.dirname(__file__))
WTF_CSRF_ENABLED = True


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "ThisShouldBeChanged"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # mail settings
    MAIL_SUBJECT_PREFIX = "[Tracker]"
    MAIL_SENDER = "noreply <noreply@tylergarcia.net>"
    MAIL_PORT = 465
    MAIL_SERVER = "one.mxroute.com"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # file upload settings
    UPLOAD_FOLDER = os.path.join(basedir, "files/")
    ALLOWED_EXTENSIONS = set(["txt", "jpg"])

    # set root admin email here
    TRACKER_ADMIN = os.environ.get("TRACKER_ADMIN") or "dummy@tylergarcia.net"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")

    TICKETS_PER_PAGE = 10


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "app.db")


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite://"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")


class DemoConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEMO_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "demo.db")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "demo": DemoConfig,

    "default": DevelopmentConfig
}
