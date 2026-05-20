from datetime import date

from club.models import Event


def clendar_planed_events(request):
    month = int(date.today().strftime("%m"))
    events = (
        Event.objects
        .filter(date__month=month)
        .only("date", "name", "id")
    )

    events_by_day = {}

    for event in events:
        events_by_day.setdefault(
            int(event.date.strftime("%d")), []
        ).append(event)

    return {"planned_events": events_by_day}
