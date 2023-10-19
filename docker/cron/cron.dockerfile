FROM python:3.11-slim

RUN apt clean && apt update && apt install -y cron && rm -rf /var/lib/apt/lists/*
RUN mkfifo --mode 0666 /var/log/cron.log

RUN pip install -U pip poetry && poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poery.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root --with worker --without backend,dev

COPY ./src /app/src

COPY ./docker/cron/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY ./docker/cron/regular_tasks /etc/cron.d

ENTRYPOINT [ "/docker-entrypoint.sh" ]

ENV PYTHONPATH=/app

CMD ["/bin/bash", "-c", "cron && tail -f /var/log/cron.log"]