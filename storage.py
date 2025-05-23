from collections import deque

events = deque(maxlen=100)


def add_event(data):
    events.appendleft(data)


def get_events(event_type):
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
