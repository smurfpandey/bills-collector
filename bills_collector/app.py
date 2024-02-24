# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
# Core python packages
import logging
from os import environ
import sys

# 3rd party python packages
from flask import Flask, render_template
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Local module imports
from bills_collector.extensions import (
    bcrypt,
    cache,
    db,
    migrate,
    celery,
    login_manager,
    oauth
)
from bills_collector.routes import views, auth, connect, api

# Initialize Sentry
sentry_sdk.init(
    environ.get('SENTRY_DSN'),
    integrations=[
        FlaskIntegration(),
        CeleryIntegration(),
        SqlalchemyIntegration()
    ]
)

def create_app(config_object="bills_collector.config"):
    """Create application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)

    # config file has STATIC_FOLDER='/static/dist'
    app.static_url_path=app.config.get('STATIC_FOLDER')
    # set the absolute path to the static folder
    app.static_folder=app.root_path + app.static_url_path

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    configure_logger(app)

    app.logger.info("Application startup complete")

    @app.context_processor
    def inject_account_enum():
        account_dict = {
            'gmail': {'name': 'Gmail'},
            'zoho': {'name': 'Zoho Mail'},
            'google_drive': {'name': 'Google Drive'}
        }
        return dict(AccountTypeDict=account_dict)

    return app

def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    celery.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(views.main_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(connect.connect_bp)
    app.register_blueprint(api.api_bp)

def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [400, 404, 500]:
        app.errorhandler(errcode)(render_error)

def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)

def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    app.logger.setLevel(app.config['LOG_LEVEL'].upper())
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    log = logging.getLogger('authlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)
