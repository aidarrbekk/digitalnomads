import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Core App Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///digitalnomads.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set True in production (HTTPS only)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Email Confirmation Salt
    SECURITY_PASSWORD_SALT = os.environ.get(
        'SECURITY_PASSWORD_SALT',
        'email-confirm-salt'
    )

    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))

    # Convert string to real boolean
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'ssshipaiii@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'retkqmngionadbhg')
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        'ShipAI <ssshipaiii@gmail.com>'
    )


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Enforce HTTPS in production


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}