FROM python:3.7-alpine
LABEL AUTHOR Muteshi

ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt

# Installing client libraries and any other package you need
RUN apk update && apk add --no-cache libpq jpeg-dev


RUN apk add  --update --no-cache --virtual .build-deps \
            gcc python3-dev musl-dev postgresql-dev \
             musl-dev zlib zlib-dev libjpeg

RUN pip install -r /requirements.txt

# Delete temp  build dependencies
RUN apk del .build-deps

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D muteshi
RUN chown -R muteshi:muteshi /vol/
RUN chmod -R 755 /vol/web
USER muteshi