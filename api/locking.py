from backend import settings
from redlock import RedLockFactory


def parse_redis_url(url):
    from urllib.parse import urlparse, parse_qs
    from urllib.error import URLError

    parsed = urlparse(url)

    if parsed.scheme != 'redis':
        raise URLError('Redis URL does not have the redis scheme')

    path = parsed.path[1:] or ''
    query = parse_qs(parsed.query or '')
    if path:
        db = int(path)
    elif 'db' in query:
        db = int(query['db'])
    else:
        db = 0

    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'db': db
    }


lock_factory = RedLockFactory(connection_details=[parse_redis_url(settings.REDIS_URL)])
