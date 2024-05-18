from django.conf import settings


SMARTWATCH_HTTP_PORT = getattr(settings, 'SMARTWATCH_HTTP_PORT', 8000)
SMARTWATCH_HTTP_HOST = getattr(settings, 'SMARTWATCH_HTTP_HOST', '0.0.0.0')
SMARTWATCH_WS_PORT = getattr(settings, 'SMARTWATCH_WS_PORT', 8001)
SMARTWATCH_WS_HOST = getattr(settings, 'SMARTWATCH_WS_HOST', '0.0.0.0')

SMARTWATCH_COLLECT_STATIC = getattr(settings, 'SMARTWATCH_COLLECT_STATIC', True)
SMARTWATCH_MIGRATE = getattr(settings, 'SMARTWATCH_MIGRATE', True)