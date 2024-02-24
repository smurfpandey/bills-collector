# -*- coding: utf-8 -*-
"""Application entry point."""
from bills_collector.app import create_app, celery

app = create_app()

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
