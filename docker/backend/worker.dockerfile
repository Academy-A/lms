FROM python:3.11-slim

RUN pip install -U pip poetry && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root --with worker --without backend,dev

COPY ./src /app/src

ENV PYTHONPATH=/app
CMD ["celery", "-A", "src.tasks.config.celery", "worker", "--loglevel=info", "--logfile=celery.log"]