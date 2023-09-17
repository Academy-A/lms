#! /usr/bin/env bash

python /app/src/pre_start.py

alembic -c /app/src/alembic.ini upgrade head

python /app/src/initial_data.py