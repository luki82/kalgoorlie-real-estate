#!/usr/bin/env bash
# Render runs this as the build step (see render.yaml).
set -o errexit

pip install -r requirements.txt

cd core
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_admin
