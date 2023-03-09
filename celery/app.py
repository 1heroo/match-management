from celery import Celery
from celery.schedules import crontab
from core.settings import settings


app = Celery('celery',
             broker=settings.RABBIT_BROKER_URL,
             include=['celery.tasks'])


app.conf.beat_schedule = {
    # 'product aggregator': {
    #     'task': 'celery.tasks.product_aggregator',
    #     'schedule': crontab(minute=0, hour=10),
    # },
    # 'launch_matching': {
    #     'task': 'celery.tasks.launch_matching',
    #     'schedule': crontab(minute=0, hour=11)
    # },
    'price_management': {
        'task': 'celery.tasks.price_management',
        'schedule': crontab(minute=0, hour=12)
    }
}

app.conf.timezone = 'Europe/Moscow'
