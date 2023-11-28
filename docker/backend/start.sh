#! /usr/bin/env sh
set -e

python -m lms.db upgrade head
python -m lms