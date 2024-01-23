FROM python:3.11-slim

RUN pip install -U pip poetry && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/
RUN poetry install --no-interaction --no-ansi --no-root --without dev

COPY ./lms /app/lms

ENV PYTHONPATH=/app