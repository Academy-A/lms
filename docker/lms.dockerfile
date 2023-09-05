FROM python:3.11-slim

RUN pip install -U pip poetry && poetry config virtualenvs.create false


WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src /app/src

ENV PYTHONPATH=/app

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app", "--reload"]