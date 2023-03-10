from celery import Celery
from celery.schedules import crontab
from core.settings import settings


app = Celery('tasks',
             broker=settings.RABBIT_BROKER_URL,
             include=['tasks.tasks'])


app.conf.beat_schedule = {
    'product aggregator': {
        'task': 'tasks.tasks.product_aggregator',
        'schedule': 5
        # 'schedule': crontab(minute=0, hour=10),
    },
    'launch_matching': {
        'task': 'tasks.tasks.launch_matching',
        'schedule': 5
        # 'schedule': crontab(minute=0, hour=11)
    },
    'price_management': {
        'task': 'tasks.tasks.price_management',
        'schedule': 5
        # 'schedule': crontab(minute=0, hour=12)
    }
}

app.conf.timezone = 'Europe/Moscow'
