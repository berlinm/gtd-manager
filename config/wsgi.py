import os

from django.core.wsgi import get_wsgi_application

# Production settings module is TBD. Update this path before deployment.
# See docs/AIR_GAP_DEPLOYMENT.md.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

application = get_wsgi_application()
