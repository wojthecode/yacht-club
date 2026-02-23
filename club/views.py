from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date

from club.models import Boat, Event, Member, WorkTask


def index(request:HttpRequest) -> HttpResponse:
    today = date.today()
    upcoming = list(Event.objects.filter(date__gte=today)[:5])
    num_boats = Boat.objects.count()
    num_members = Member.objects.count()

    context = {
        "upcoming": upcoming,
        "num_boats": num_boats,
        "num_members": num_members,
    }

    return render(request, "club/index.html", context=context)


class EventListView(generic.ListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event

class WorkTaskListView(LoginRequiredMixin, generic.ListView):
    model = WorkTask


class WorkTaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = WorkTask


class BoatListView(generic.ListView):
    model = Boat


class BoatDetailView(generic.DetailView):
    model = Boat
