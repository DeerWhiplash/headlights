# Setup instructions
- Populate valid .env file
- Run `docker compose up --build`

# Accessing front-end
- For most use cases access: `http://127.0.0.1:8000/app/`
- For testing PayPal integration:
    1. Run `docker exec -it django-docker python manage.py show_ngrok_url`
    2. Navigate to the URL given.

# Actions within container
## Tests
- Run `docker exec -it django-docker python manage.py test`

## Linting Fixer
- Run `docker exec -it django-docker ruff check --fix`

## Import data_dumps
- Run `docker exec -it django-docker python manage.py loaddata myapp/migrations/data_dumps/...`
