from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from club.models import Boat, Event, WorkTask


def index(request:HttpRequest) -> HttpResponse:
    return render(request, "club/index.html")


class EventListView(generic.ListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event


class WorkTaskListView(generic.ListView):
    model = WorkTask


class WorkTaskDetailView(generic.DetailView):
    model = WorkTask


class BoatListView(generic.ListView):
    model = Boat


class BoatDetailView(generic.DetailView):
    model = Boat
