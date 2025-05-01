#!/bin/sh

# This script runs every time the container is started so contains commands that need to execute after each update and deployment.
echo ">>>> ENTRYPOINT.SH EXECUTED <<<<"

python manage.py migrate --no-input
python manage.py create_crud_mappings
python manage.py populate_table_lookup
python manage.py loaddata myapp/migrations/data_dumps/auth_group_data.json
python manage.py loaddata myapp/migrations/data_dumps/auth_user_data.json

if [ "$DJANGO_ENV" = "PROD" ]; then
    echo "Running in production mode"
    
    python manage.py collectstatic --no-input
    gunicorn desd.wsgi:application --bind 0.0.0.0:8000
else
    echo "Running in development mode"

    python manage.py runserver 0.0.0.0:8000
fi
