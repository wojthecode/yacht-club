from django.urls import path

from club.views import (
    index,
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    toggle_event_participation,
    WorkTaskListView,
    WorkTaskDetailView,
    WorkTaskCreateView,
    WorkTaskUpdateteView,
    WorkTaskDeleteView,
    toggle_worktask_participation,
    BoatListView,
    BoatDetailView,
    BoatCreateView,
    BoatUpdateView,
    BoatDeleteView,
    MemberListView,
)


urlpatterns = [
    path("", index, name="index"),

    ### Events ###

    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path(
        "events/update/<int:pk>/",
        EventUpdateView.as_view(),
        name="event-update"
    ),
    path(
        "events/delete/<int:pk>/",
        EventDeleteView.as_view(),
        name="event-delete"
    ),
    path(
        "events/<int:pk>/toggle_event_participation",
        toggle_event_participation,
        name="toggle-event-participation"
    ),

    ### Work Tasks ###

    path("work_tasks/", WorkTaskListView.as_view(), name="worktask-list"),
    path(
        "work_tasks/<int:pk>/",
        WorkTaskDetailView.as_view(),
        name="worktask-detail"
    ),
    path(
        "work_tasks/create/",
        WorkTaskCreateView.as_view(),
        name="worktask-create"
    ),
    path(
        "work_tasks/update/<int:pk>/",
        WorkTaskUpdateteView.as_view(),
        name="worktask-update"
    ),
    path(
        "work_tasks/delete/<int:pk>/",
        WorkTaskDeleteView.as_view(),
        name="worktask-delete"
    ),
    path(
        "work_tasks/<int:pk>/toggle_worktask_participation",
        toggle_worktask_participation,
        name="toggle-worktask-participation"
    ),

    ### Boats ###

    path("boats/", BoatListView.as_view(), name="boat-list"),
    path("boats/<int:pk>/", BoatDetailView.as_view(), name="boat-detail"),
    path("boats/create/", BoatCreateView.as_view(), name="boat-create"),
    path(
        "boats/update/<int:pk>",
        BoatUpdateView.as_view(),
        name="boat-update"
    ),
    path(
        "boats/delete/<int:pk>/",
        BoatDeleteView.as_view(),
        name="boat-delete"
    ),

    ### Members ###

    path("members/", MemberListView.as_view(), name="member-list"),
]

app_name = "club"
