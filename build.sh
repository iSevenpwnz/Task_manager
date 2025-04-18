#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate

if [ "${LOAD_FIXTURES}" = "true" ]; then
    echo "Loading initial data..."
    python manage.py loaddata fixtures.json
fi

echo "Build completed successfully!" 