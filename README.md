# RPS Command & Control server

## Running locally

To run this app locally, you'll need Python, Postgres, and Redis.

Then, to run:

- Install requirements: `pip install -r requirements.txt` (you almost certainly want to do this in a virtualenv).
- Migrate: `DATABASE_URL=postgres:///... python manage.py migrate`
- Or, to run locally with `runserver`, set `DATABASE_URL` and `REDIS_URL` in your environ, then run `python manage.py runserver`.
