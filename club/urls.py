from django.urls import path

from club.views import (
    BoatListView,
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
    path("work_tasks/", WorkTaskListView.as_view(), name="worktask-list"),
    path("work_tasks/<int:pk>/", WorkTaskDetailView.as_view(), name="worktask-detail"),
    path("boats/", BoatListView.as_view(), name="boat-list"),
]

app_name = "club"
