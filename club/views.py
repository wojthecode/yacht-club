from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import Permission
from django.db.models import Prefetch, Exists, OuterRef
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from datetime import date, datetime

from club.models import Boat, Event, WorkTask
from club.forms import (
    BoatForm,
    MemberCreationForm,
    MemberUpdateForm,
    PasswordResetForm
)


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


class ManagementRightsRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role.management_rights:    # type: ignore
            return render(request, "club/403.html", status=403)
        return super().dispatch(request, *args, **kwargs)


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
    

class ActivityDetailQueryMixin():
    def get_queryset(self):
        return (
            super()
            .get_queryset()                     # type: ignore
            .select_related("created_by")
        )


class FormLoggedUserMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()      # type: ignore
        kwargs["user"] = self.request.user      # type: ignore
        return kwargs


class ProfileGetUserObjectMixin(LoginRequiredMixin):
    def get_object(self):
        return self.request.user                # type: ignore
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    # type: ignore
        context["profile"] = "Profile"
        return context


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


class EventDetailView(ActivityDetailQueryMixin, generic.DetailView):
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
    paginate_by = 8

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


class WorkTaskDetailView(
        ActivityDetailQueryMixin, ActiveRequiredMixin, generic.DetailView
    ):
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


class WorkTaskArchiveIndexView(ActiveRequiredMixin, generic.ArchiveIndexView):
    model = WorkTask
    date_field = "date"
    paginate_by = 8

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
    return HttpResponseRedirect(
        reverse_lazy("club:worktask-detail", args=[pk])
    )


### Boat Views ###

class BoatListView(generic.ListView):
    model = Boat
    paginate_by = 3
    queryset = Boat.objects.all().select_related("owner")


class BoatDetailView(generic.DetailView):
    model = Boat

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("owner")
            .prefetch_related("keeper")
        )


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


### Member ###

###### => Base Views ###

class MemberListView(ActiveRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 10

    def get_queryset(self):
        is_active_perm = Permission.objects.filter(
            codename="active_member"
        )

        queryset = (
            super()
            .get_queryset()
            .exclude(username="admin")
            .select_related("role")
            .annotate(
                is_active_member=Exists(
                    is_active_perm.filter(user=OuterRef("pk"))
                )
            )
        )
        return queryset


class MemberCreateView(FormLoggedUserMixin, generic.CreateView):
    form_class = MemberCreationForm
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_fields"] = ["is_active", "phone_visibility", "avatar", "password"]
        return context
    
    def get_success_url(self):
        if self.request.user.is_authenticated:
            url = super().get_success_url()
        else:
            url = reverse("club:profile")
        return url


class MemberDetailBaseView(generic.DetailView):
    model = get_user_model()

    def get_queryset(self):
        today = date.today()
        queryset = super().get_queryset()
        return (
            queryset
            .select_related("role", "sailing_permission")
            .prefetch_related(
                "boats_keeped", "boats_owned",
                Prefetch(
                    "event_participant",
                    queryset=Event.objects.filter(date__gte=today),
                ),
                Prefetch(
                    "worktask_participant",
                    queryset=WorkTask.objects.filter(date__gte=today),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = context.get("member")
        user = self.request.user

        context["comming_events"] = list(
            self.object.event_participant.all()         # type: ignore
        )
        context["comming_worktask"] = list(
            self.object.worktask_participant.all()      # type: ignore
        )
        context["boats_owned"] = list(
            self.object.boats_owned.all()               # type: ignore
        )
        context["boats_keeped"] = list(
            self.object.boats_keeped.all()              # type: ignore
        )
        context["phone_visible"] = member.phone and (   # type: ignore
            member.phone_visibility                     # type: ignore
            or user.role.management_rights              # type: ignore
            or member == user
            )
        return context


class MemberUpdateBaseView(FormLoggedUserMixin, generic.UpdateView):
    form_class = MemberUpdateForm
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_fields"] = ["is_active", "phone_visibility", "avatar", "password"]
        return context


class MemberDeleteBaseView(generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("club:index")
    template_name = "club/member_confirm_delete.html"


class MemberResetPasswordView(ManagementRightsRequiredMixin, generic.FormView):
    form_class = PasswordResetForm
    template_name = "club/password_reset_form.html"
    success_url = reverse_lazy("club:member-list")

    def dispatch(self, request, *args, **kwargs):
        self.member = get_user_model().objects.get(pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.member
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.member
        kwargs["user"] = user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


###### => Member Views ###

class MemberDetailView(ActiveRequiredMixin, MemberDetailBaseView):
    pass


class MemberUpdateView(ManagementRightsRequiredMixin, MemberUpdateBaseView):
    pass


class MemberDeleteView(ManagementRightsRequiredMixin, MemberDeleteBaseView):
    success_url = reverse_lazy("club:member-list")


###### => Profile Views ###

class MemberProfileView(ProfileGetUserObjectMixin, MemberDetailBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today().astimezone().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        context["comming_events"] = [
            event 
            for event 
            in context["comming_events"] 
            if event.date >= today]
        context["comming_worktask"] = [
            event 
            for event 
            in context["comming_worktask"] 
            if event.date >= today]
        return context


class MemberProfileUpdateView(ProfileGetUserObjectMixin, MemberUpdateBaseView):
    success_url = reverse_lazy("club:profile")


class MemberProfileDeleteView(ProfileGetUserObjectMixin, MemberDeleteBaseView):
    pass


### Toggle Views ###

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
