#!/bin/bash

# Migrate database
python manage.py migrate

# Start gunicorn
gunicorn sqllabs.wsgi:application --bind 0.0.0.0:$PORT
