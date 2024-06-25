web: gunicorn run:app
worker: celery -A app.celery worker --loglevel=info