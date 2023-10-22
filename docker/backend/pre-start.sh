#! /usr/bin/env bash

python /app/lms/pre_start.py

alembic -c /app/lms/alembic.ini upgrade head

python /app/lms/initial_data.py