"""
WSGI config for mtaalamux project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtaalamux.settings')

application = get_wsgi_application()
