from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import Permission
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from datetime import date, datetime

from club.models import Boat, Event, WorkTask
from club.forms import BoatForm, MemberCreationForm


### Mixins ###

class ActiveRequiredMixin(PermissionRequiredMixin):
    permission_required = "club.active_member"
    raise_exception = False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:      # type: ignore
            login_url = reverse("login")
            next = self.request.get_full_path()         # type: ignore
            return redirect(f"{login_url}?next={next}")
        
        page = self.request.path.split("/")[1]          # type: ignore
        NAME = {
            "work_tasks": "Work Tasks",
            "members": "Members",
            "boats": "Boat Create",
        }

        return render(
            self.request,                               # type: ignore
            "club/no_permissions.html",
            {
                "from_url": NAME.get(page, "None"),
            },
            status=403
        )


class EventContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # type: ignore
        context["activity"] = "Event"
        return context


class WorkTaskContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # type: ignore
        context["activity"] = "Work Task"
        return context


class FormLoggedUserMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()      # type: ignore
        kwargs["user"] = self.request.user      # type: ignore
        return kwargs


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
        "home": "home",
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

class EventListView(BaseActivityListView):
    model = Event


class EventDetailView(generic.DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        event_date = date(*[
            int(part) 
            for part 
            in context["event"].date.strftime("%Y-%m-%d").split("-")
        ])

        if event_date < today:
            context["latest"] = "latest"

        return context


class EventCreateView(EventContextMixin, BaseActivityCreateView):
    model = Event
    fields = ("name", "description", "date", "location")


class EventUpdateView(EventContextMixin, BaseActivityUpdateView):
    model = Event
    fields = ("name", "description", "date", "location")


class EventDeleteView(
        ActiveRequiredMixin, EventContextMixin, generic.DeleteView
    ):
    model = Event
    template_name = "club/activity_confirm_delete.html"
    success_url = reverse_lazy("club:event-list")


class EventArchiveIndexView(generic.ArchiveIndexView):
    model = Event
    date_field = "date"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = "event"
        return context


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

class WorkTaskListView(ActiveRequiredMixin, BaseActivityListView):
    model = WorkTask


class WorkTaskDetailView(ActiveRequiredMixin, generic.DetailView):
    model = WorkTask

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        worktask_date = date(*[
            int(part) 
            for part 
            in context["worktask"].date.strftime("%Y-%m-%d").split("-")
        ])

        if worktask_date < today:
            context["latest"] = "latest"

        return context


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


class WorkTaskArchiveIndexView(generic.ArchiveIndexView):
    model = WorkTask
    date_field = "date"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["worktask"] = "worktask"
        return context


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

class BoatListView(generic.ListView):
    model = Boat
    paginate_by = 4


class BoatDetailView(generic.DetailView):
    model = Boat


class BoatCreateView(
        FormLoggedUserMixin, ActiveRequiredMixin, generic.CreateView
    ):
    model = Boat
    form_class = BoatForm


class BoatUpdateView(
        FormLoggedUserMixin, LoginRequiredMixin, generic.UpdateView
    ):
    model = Boat
    form_class = BoatForm


class BoatDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Boat
    success_url = reverse_lazy("club:boat-list")
    template_name = "club/boat_confirm_delete.html"


### Member Views ###

class MemberListView(ActiveRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        for member in queryset:
            member.is_active_member = member.has_perm("club.active_member")
        
        return queryset


class MemberDetailView(ActiveRequiredMixin, generic.DetailView):
    model = get_user_model()

    def get_context_data(self, **kwargs):
        today = date.today()
        context = super().get_context_data(**kwargs)
        context["comming_events"] = (
            self.object.event_participant.filter( # type: ignore
                date__gte=today
            )
        )
        context["comming_worktask"] = (
            self.object.worktask_participant.filter( # type: ignore
                date__gte=today
            )
        )
        return context


class MemberCreateView(
        FormLoggedUserMixin, generic.CreateView
    ):
    model = get_user_model()
    form_class = MemberCreationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_fields"] = ["is_active", "phone_visibility", "avatar"]
        return context


@login_required
def toggle_active_member(request, pk):

    if request.user.role.management_rights:

        member = get_user_model().objects.get(pk=pk)
        permission = Permission.objects.get(codename="active_member")

        if member.has_perm("club.active_member"):
            member.user_permissions.remove(permission)
            member.save()
        else:
            member.user_permissions.add(permission)
            member.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
