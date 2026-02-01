# MtaalamuX - Django REST Framework Backend

## Setup Instructions

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

Access the API documentation at: `http://localhost:8000/api/schema/`

## Project Structure

```
backend/
├── mtaalamux/          # Main Django project settings
├── core/               # Main application
│   ├── models.py       # Data models
│   ├── serializers.py  # DRF serializers
│   ├── views.py        # API views
│   ├── urls.py         # URL routing
│   ├── permissions.py  # Custom permissions
│   ├── throttling.py   # Custom throttling
│   └── tests/          # Tests
├── media/              # Uploaded files
├── requirements.txt    # Python dependencies
├── manage.py           # Django management script
└── .env.example        # Environment variables template
```

## Features

- JWT Authentication
- API Documentation with drf-spectacular
- Request Throttling
- Django Silk Profiling
- Comprehensive Tests
