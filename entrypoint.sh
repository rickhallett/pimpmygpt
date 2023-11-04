#!/bin/sh

# Initialize the database
flask --app pimpmygpt init-db

# Start Gunicorn
# exec gunicorn -b :8000 "app:app"
