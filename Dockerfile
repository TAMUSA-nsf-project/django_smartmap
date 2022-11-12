FROM python:3.8-slim
WORKDIR /app
COPY ./requirements.txt /requirements.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home django-user

COPY . /app

ENV PATH="/py/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER django-user

# Gunicorn as app server
CMD exec gunicorn --bind 0.0.0.0:80 --workers 1 --threads 8 --timeout 0 django_smartmap.wsgi:application