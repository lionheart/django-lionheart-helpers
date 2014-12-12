from django.conf import settings

REDIS = {
    'password': '',
    'port': 6379,
    'host': 'localhost',
}
if hasattr(settings, 'REDIS'):
    REDIS.update(settings.REDIS)

HOME_URL = getattr(settings, 'HOME_URL', '/')
PRIMARY_USER_MODEL = getattr(settings, 'PRIMARY_USER_MODEL', 'app.User')

try:
    from redis import Redis
except ImportError:
    REDIS_AVAILABLE = False
else:
    REDIS_AVAILABLE = True

