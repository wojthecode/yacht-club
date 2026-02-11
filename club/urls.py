from django.urls import path

from club.views import (
    index,
    EventListView,
)


urlpatterns = [
    path("", index, name="index"),
    path("events/", EventListView.as_view(), name="event-list"),
]

app_name = "club"
