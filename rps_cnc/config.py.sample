import random
import string
import os
import dj_database_url

DEBUG = os.environ.get("DEBUG", False)

REDIS_MASTERS = [os.environ.get('REDIS_URL', 'redis://localhost:6379')]
DEFAULT_DATABASE = dj_database_url.config(default="postgres:///rps-cnc", conn_max_age=500)

SECRET_KEY = os.environ.get("SECRET_KEY", "".join(random.choice(string.printable) for i in range(40)))
GCM_SERVER_KEY = os.environ.get("GCM_SERVER_KEY", None)
