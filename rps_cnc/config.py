import os
import dj_database_url

REDIS_MASTERS = [os.environ.get('REDIS_URL', 'redis://localhost:6379')]
DEFAULT_DATABASE = dj_database_url.config(default="postgres:///rps-cnc", conn_max_age=500)
