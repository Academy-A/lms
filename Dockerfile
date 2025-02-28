FROM python:3.12-slim

RUN pip install -U pip poetry virtualenv==20.28.1 \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/
RUN poetry install --no-interaction --no-ansi --without dev --no-root

COPY ./lms /app/lms

ENV PYTHONPATH=/app

ENTRYPOINT [ "python", "-m", "lms.db", "upgrade", "head" ]