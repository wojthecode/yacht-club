from django.urls import path

from club.views import (
    index,
    EventListView,
    EventDetailView,
    WorkTaskListView,
    WorkTaskDetailView,
)


urlpatterns = [
    path("", index, name="index"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("work_task/", WorkTaskListView.as_view(), name="work_task-list"),
    path("work_task/<int:pk>/", WorkTaskDetailView.as_view(), name="work_task-detail"),
]

app_name = "club"
