# LMS

## Description

## Installation

```bash
git clone
python -m venv .venv
source .venv/bin/activate
pip install -U pip poetry
poetry install --no-root
pre-commit install
cp .env.dev .env
```

## Configuration

You need create `.env` file with actual variables:

```bash
cp .env.dev .env
```

```
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=lms

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=secret
REDIS_DB=1

SOHO_API_TOKEN=need_to_get_your_token
SECRET_KEY=your_token_for_auth
```

## Running

### Docker

### Localy

### Database Migration

## Using

### API

### Admin

