
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
        db = int(query['db'][0])
    else:
        db = 0

    options = {
        'host': parsed.hostname,
        'port': parsed.port,
        'db': db
    }

    if parsed.password:
        options['password'] = parsed.password

    return options

if __name__ == '__main__':
    redis_url = 'redis://username:password@host:1234/?db=1'
    print(parse_redis_url(redis_url))
    exit(0)

from redlock import RedLockFactory

from rps_cnc import settings

lock_factory = RedLockFactory(connection_details=[parse_redis_url(settings.REDIS_URL)])
