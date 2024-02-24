# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""

import flask
from authlib.integrations.flask_client import OAuth
from celery import Celery
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

class FlaskCelery(Celery):
    """Flask-ify celery:
        - https://stackoverflow.com/a/14146403/1151361
        - https://github.com/celery/celery/issues/5282
    """
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task    # pylint: disable=invalid-name
        _celery = self

        class ContextTask(TaskBase):    # pylint: disable=too-few-public-methods
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask # pylint: disable=invalid-name,

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config)

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
celery = FlaskCelery()
login_manager = LoginManager()
oauth = OAuth()
