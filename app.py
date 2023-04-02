# -*- coding: utf-8 -*-
"""Application entry point."""
from bills_collector.app import create_app, celery

app = create_app()