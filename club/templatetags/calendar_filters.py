from django import template
from datetime import date
from club.models import Event


register = template.Library()


@register.filter
def first_day(value):
    year, month, _ = value.split("-")
    day = date(int(year), int(month), 1)
    return day.strftime("%a").lower()


@register.filter
def range_list(value):
    return range(1, int(value) + 1)


@register.filter
def get_items(value, key):
    return value.get(key)
