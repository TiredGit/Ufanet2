from collections import deque

events = deque(maxlen=100)
"""Двусторонняя очередь для хранения приходящих сообщений"""


def add_event(data):
    """Добавление сообщений, приходящих от kafka"""
    events.appendleft(data)


def get_events(event_type):
    """Филтьтрация и вывод нужных сообщений"""
    if event_type == 'city':
        return list(filter(lambda x: x['table'] == 'discounts_app_city', events))
    elif event_type == 'company':
        return list(filter(lambda x: x['table'] == 'discounts_app_company', events))
    elif event_type == 'discount':
        return list(filter(lambda x: x['table'] == 'discounts_app_discountcard', events))
    elif event_type == 'category':
        return list(filter(lambda x: x['table'] == 'discounts_app_discountcategory', events))
    else:
        return list(events)
