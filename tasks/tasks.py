from celery import shared_task

import requests
from core.settings import settings

host = settings.HOST


@shared_task()
def product_aggregator():
    # print(5)
    requests.get(host + '/mm/aggregate-products/')
    print("aggregated all products")
    return True


@shared_task()
def launch_matching():
    # print(5)
    requests.get(host + '/mm/lunch-matching-with_local_file/')
    print('launched matching')
    return True


@shared_task()
def price_management():
    # print('5')
    requests.get(host + '/price/price-monitoring/')
    print('price_management')
    return True
