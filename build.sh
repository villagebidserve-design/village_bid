#!/bin/bash
set -e  # Exit on any error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running migrations..."
python manage.py migrate --verbosity 2

echo "Build complete!"
