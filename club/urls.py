from django.urls import path

from club.views import (
    index,
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    WorkTaskListView,
    WorkTaskDetailView,
    BoatListView,
    BoatDetailView,
)


urlpatterns = [
    path("", index, name="index"),
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),

    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/update/<int:pk>/", EventUpdateView.as_view(), name="event-update"),

    path("work_tasks/", WorkTaskListView.as_view(), name="worktask-list"),
    path("work_tasks/<int:pk>/", WorkTaskDetailView.as_view(), name="worktask-detail"),
    path("boats/", BoatListView.as_view(), name="boat-list"),
    path("boats/<int:pk>/", BoatDetailView.as_view(), name="boat-detail"),
]

app_name = "club"
