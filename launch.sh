#!/bin/sh
cd decide/
cp local_settings.deploy.py local_settings.py

find authentication/migrations/ -name "*.py" -not -name "__init__.py" -delete
rm -rf authentication/migrations/__pycache__/

./manage.py collectstatic --noinput
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser --noinput
# gunicorn -w 5 decide.wsgi:application --timeout=500
./manage.py runserver