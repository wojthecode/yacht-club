from django.urls import path

from club.views import (
    WorkTaskListView,
    index,
    EventListView,
    EventDetailView,
)


urlpatterns = [
    path("", index, name="index"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("work_task/", WorkTaskListView.as_view(), name="work_task-list"),
]

app_name = "club"
