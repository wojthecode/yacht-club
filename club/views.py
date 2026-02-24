from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
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


class BaseActivityListView(generic.ListView):
    paginate_by = 4

    def get_queryset(self):
        today = date.today()
        queryset = super().get_queryset().filter(date__gte=today)
        return queryset


class BaseActivityCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "club/base_activity_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].widget = forms.DateInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
        return form

    def form_valid(self, form):
       form.instance.created_by = self.request.user
       return super().form_valid(form)


class BaseActivityUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "club/base_activity_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].widget = forms.DateInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
        return form


class EventListView(BaseActivityListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event


class EventCreateView(BaseActivityCreateView):
    model = Event
    fields = ("name", "description", "date", "location")


class EventUpdateView(BaseActivityUpdateView):
    model = Event
    fields = ("name", "description", "date", "location")


class WorkTaskListView(LoginRequiredMixin, BaseActivityListView):
    model = WorkTask


class WorkTaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = WorkTask


class WorkTaskCreateView(BaseActivityCreateView):
    model = WorkTask
    fields = ("name", "description", "date", "location", "min_crew")


class WorkTaskUpdateteView(BaseActivityUpdateView):
    model = WorkTask
    fields = ("name", "description", "date", "location", "min_crew")


class BoatListView(generic.ListView):
    model = Boat
    paginate_by = 4


class BoatDetailView(generic.DetailView):
    model = Boat
