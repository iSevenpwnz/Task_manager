#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Ensure admin static files are properly collected
if [ -d "staticfiles/admin" ]; then
    echo "Admin static files are collected."
else
    echo "Manually collecting admin static files..."
    mkdir -p staticfiles/admin
    cp -r $(python -c "import django; print(django.__path__[0])")/contrib/admin/static/admin/* staticfiles/admin/
fi

echo "Applying database migrations..."
python manage.py migrate

if [ "${LOAD_FIXTURES}" = "true" ]; then
    echo "Loading initial data..."
    python manage.py loaddata fixtures.json
fi

# Створення суперкористувача для адміністративного доступу
if [ "${CREATE_SUPERUSER}" = "true" ] && [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL}" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput
fi

echo "Build completed successfully!" 