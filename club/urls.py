from django.urls import path

from club.views import (
    index,
    EventListView,
    EventDetailView,
)


urlpatterns = [
    path("", index, name="index"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
]

app_name = "club"
