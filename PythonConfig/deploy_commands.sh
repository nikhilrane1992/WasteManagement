#!/bin/bash

# Collect static files
echo "Collect static files"
python WasteManagement/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python WasteManagement/manage.py migrate

# Create database superuser
echo "Create database superuser"
python WasteManagement/manage.py createprojectsuperuser

# Start server
echo "Starting server"
python WasteManagement/manage.py runserver 0.0.0.0:8000


