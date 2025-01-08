FROM python:3.13.0-alpine

WORKDIR /app/obiadomat

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY . .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt