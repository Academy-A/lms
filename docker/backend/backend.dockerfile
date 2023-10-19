FROM python:3.11-slim

RUN pip install -U pip poetry && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/
RUN poetry install --no-interaction --no-ansi --no-root --with backend --without worker,dev

COPY ./docker/backend/pre-start.sh ./docker/backend/start.sh /app/
RUN chmod +x /app/start.sh

COPY ./src /app/src

ENV PYTHONPATH=/app
CMD ["/app/start.sh"]