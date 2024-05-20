import os


class Config:
    SECRET_KEY = os.environ.get('portfolio_website_secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = 'smtp.example.com'  # Your email server
    MAIL_PORT = 587  # Your email server port
    MAIL_USE_TLS = True  # Use TLS
    MAIL_USE_SSL = False  # Use SSL
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your email username
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Your email password
    MAIL_RECIPIENT = 'your_email@example.com'  # Where to send contact form submissions


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
