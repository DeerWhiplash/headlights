#!/bin/sh

# This script runs every time the container is started so contains commands that need to execute after each update and deployment.

python manage.py migrate --noinput
python manage.py create_crud_mappings
python manage.py populate_table_lookup
python manage.py loaddata myapp/migrations/data_dumps/auth_group_data.json
python manage.py loaddata myapp/migrations/data_dumps/auth_user_data.json
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
