#!/bin/bash
set -e  # Exit immediately if any command fails

# 1. Install backend dependencies
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install gunicorn

# 2. Run migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --noinput
