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
def planned_events(value):
    year, month, month_len = value.split("-")

    start_day = date(int(year), int(month), 1)
    end_day = date(int(year), int(month), int(month_len))

    events = Event.objects.filter(date__range=(start_day, end_day))

    return {event.date.day for event in events}
