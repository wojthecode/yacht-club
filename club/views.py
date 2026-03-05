from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from datetime import date

from club.models import Boat, Event, WorkTask
from club.forms import BoatForm


### Home Page View ###

def index(request:HttpRequest) -> HttpResponse:
    today = date.today()
    upcoming = list(Event.objects.filter(date__gte=today)[:5])
    num_boats = Boat.objects.count()
    num_members = get_user_model().objects.count()

    context = {
        "upcoming": upcoming,
        "num_boats": num_boats,
        "num_members": num_members,
    }

    return render(request, "club/index.html", context=context)


### Base Activity Views ###

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
        form.fields["date"].widget = forms.DateInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        )
        return form

    def form_valid(self, form):
       form.instance.created_by = self.request.user
       return super().form_valid(form)


class BaseActivityUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "club/base_activity_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].widget = forms.DateInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        )
        return form


### Event Views ###

class EventContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # type: ignore
        context["activity"] = "Event"
        return context


class EventListView(BaseActivityListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event


class EventCreateView(EventContextMixin, BaseActivityCreateView):
    model = Event
    fields = ("name", "description", "date", "location")


class EventUpdateView(EventContextMixin, BaseActivityUpdateView):
    model = Event
    fields = ("name", "description", "date", "location")


class EventDeleteView(
        LoginRequiredMixin, EventContextMixin, generic.DeleteView
    ):
    model = Event
    template_name = "club/activity_confirm_delete.html"
    success_url = reverse_lazy("club:event-list")


@login_required
def toggle_event_participation(request, pk):
    event = Event.objects.get(id=pk)
    member = get_user_model().objects.get(id=request.user.id)
    
    if event.participants.filter(pk=member.pk).exists():
        event.participants.remove(member)
    else:
        event.participants.add(member)
    return HttpResponseRedirect(reverse_lazy("club:event-detail", args=[pk]))


### Work Task Wiews ###

class WorkTaskContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # type: ignore
        context["activity"] = "Work Task"
        return context


class WorkTaskListView(LoginRequiredMixin, BaseActivityListView):
    model = WorkTask


class WorkTaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = WorkTask


class WorkTaskCreateView(WorkTaskContextMixin, BaseActivityCreateView):
    model = WorkTask
    fields = ("name", "description", "date", "location", "min_crew")


class WorkTaskUpdateteView(WorkTaskContextMixin, BaseActivityUpdateView):
    model = WorkTask
    fields = ("name", "description", "date", "location", "min_crew")


class WorkTaskDeleteView(
        LoginRequiredMixin, WorkTaskContextMixin, generic.DeleteView
    ):
    model = WorkTask
    success_url = reverse_lazy("club:worktask-list")
    template_name = "club/activity_confirm_delete.html"


@login_required
def toggle_worktask_participation(request, pk):
    worktask = WorkTask.objects.get(id=pk)
    member = get_user_model().objects.get(id=request.user.id)

    if worktask.participants.filter(pk=member.pk).exists():
        worktask.participants.remove(member)
    else:
        worktask.participants.add(member)
    return HttpResponseRedirect(reverse_lazy("club:worktask-detail", args=[pk]))


### Boat Views ###

class BoatFormUserMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()      # type: ignore
        kwargs["user"] = self.request.user      # type: ignore
        return kwargs


class BoatListView(generic.ListView):
    model = Boat
    paginate_by = 4


class BoatDetailView(generic.DetailView):
    model = Boat


class BoatCreateView(
        BoatFormUserMixin, LoginRequiredMixin, generic.CreateView
    ):
    model = Boat
    form_class = BoatForm


class BoatUpdateView(
        BoatFormUserMixin, LoginRequiredMixin, generic.UpdateView
    ):
    model = Boat
    form_class = BoatForm


class BoatDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Boat
    success_url = reverse_lazy("club:boat-list")
    template_name = "club/boat_confirm_delete.html"


### Member Views ###

class MemberListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 10
