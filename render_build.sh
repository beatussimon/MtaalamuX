#!/bin/bash
set -e  # Exit immediately if any command fails

# 1. Build frontend
cd frontend
npm install
npm run build
mkdir -p ../static/frontend
mv dist/* ../static/frontend/

# 2. Install backend dependencies
cd ../backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install gunicorn

# 3. Run migrations and collect static
python manage.py migrate
python manage.py collectstatic --noinput
