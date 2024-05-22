import os


class Config:
    SECRET_KEY = os.environ.get('PORTFOLIO_WEBSITE_FLASK_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'  # Your email server
    MAIL_PORT = 587  # Your email server port
    MAIL_USE_TLS = True  # Use TLS
    MAIL_USE_SSL = False  # Use SSL
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your email username
    # Email application-specific password (generated for use with Gmail's SMTP server)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/db_name'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
