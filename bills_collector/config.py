# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()

class Config(object):
    # FLASK_APP = env.str('FLASK_APP')
    ENV = 'development'
    DEBUG = False
    SECRET_KEY = env.str('SECRET_KEY', '')
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    LOG_LEVEL = env.str('LOG_LEVEL', default="INFO")
    PREFERRED_URL_SCHEME = 'https'

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL', '')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Static Assets
    STATIC_FOLDER = '/static/dist'

    #Oauth Client Deets
    GOOGLE_CLIENT_ID = env.str('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = env.str('GOOGLE_CLIENT_SECRET', '')

    #Oauth Client Deets
    ZOHO_CLIENT_ID = env.str('ZOHO_CLIENT_ID', '')
    ZOHO_CLIENT_SECRET = env.str('ZOHO_CLIENT_SECRET', '')
    ZOHO_AUTHORIZE_URL = 'https://accounts.zoho.com/oauth/v2/auth'
    ZOHO_ACCESS_TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token'

    # Celery
    broker_url = env.str('CELERY_BROKER_URL', '')
    broker_transport_options = { 'global_keyprefix': 'bills_collector' }
    # result_backend = env.str('CELERY_RESULT_BACKEND')

class ProductionConfig(Config):
    FLASK_ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = env.str('TEST_DATABASE_URL', 'postgresql+psycopg://myuser:mypassword@localhost:5433/mydatabase_test')
    WTF_CSRF_ENABLED = False
