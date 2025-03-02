import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CurrencyExchange.settings')

app = Celery('CurrencyExchange')

# Load Celery configurations from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from Django apps
app.autodiscover_tasks()

# Define periodic tasks manually without needing migrations
app.conf.beat_schedule = {
    'run-every-day-at-midnight': {
        'task': 'exchange_app.tasks.scheduled_historical_exchange_rates',
        'schedule': crontab(hour=0, minute=30),  # Runs at midnight 00:30
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
