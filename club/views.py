from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from club.models import Event, WorkTask


def index(request:HttpRequest) -> HttpResponse:
    return render(request, "club/index.html")


class EventListView(generic.ListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event


class WorkTaskListView(generic.ListView):
    model = WorkTask
