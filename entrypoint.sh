#!/bin/sh

flask db upgrade

gunicorn -b 0.0.0.0:5000 "bills_collector.app:create_app()"
