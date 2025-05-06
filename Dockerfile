FROM python:3.13-slim

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONBUFFERED=1

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD [ \
    "apt-get", "--assume-yes", "install", "curl", "&&", \
    "python", "manage.py", "migrate", "&&", \
    "python", "manage.py", "create_crud_mappings", "&&", \
    "python", "manage.py", "populate_table_lookup",  "&&", \
    "python", "manage.py", "loaddata", "myapp/migrations/data_dumps/*_data.json", "&&", \
    "python", "manage.py", "collectstatic", "--no-input", "&&", \
    "python", "manage.py", "runserver", "0.0.0.0:8000"]
