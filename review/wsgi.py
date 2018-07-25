"""
WSGI config for review project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
path = '/var/www'
if path not in sys.path:
        sys.path.insert(0, '/var/www/review')
        os.environ['DJANGO_SETTINGS_MODULE'] = 'review.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
