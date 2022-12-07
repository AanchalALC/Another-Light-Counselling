FROM python:3.7-alpine
WORKDIR /app

ARG SECRET_KEY
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DEBUG
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_EMAIL

ENV DB_NAME=$DB_NAME
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOST=$DB_HOST
ENV DEBUG=$DEBUG
ENV SECRET_KEY=$SECRET_KEY
ENV DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD
ENV DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN apk add --no-cache npm \
    && npm install --global sass
RUN \
    apk add --no-cache postgresql-libs jpeg-dev zlib-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev python3-dev && \
    python -m pip install -r req.txt --no-cache-dir && \
    apk --purge del .build-deps


RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py createsuperuser --noinput

# CMD sass --watch main/static/scss:main/static/css & python manage.py runserver 0.0.0.0:8000