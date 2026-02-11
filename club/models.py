from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    management_rights = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SilingPermission(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Member(AbstractUser):
    role = models.ForeignKey(
        to=Role,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
    )
    siling_permission = models.ForeignKey(
        to=SilingPermission,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members"
    )
    phone = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "member"
        verbose_name_plural = "members"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Boat(models.Model):
    name = models.CharField(max_length=64, unique=True)
    owner = models.ManyToManyField(
        to=Member,
        blank=True,
        related_name="boats_owned"
    )
    keeper = models.ManyToManyField(
        to=Member,
        blank=True,
        related_name="boats_keeped"
    )
    club_owner = models.BooleanField(default=False)
    type = models.CharField(max_length=64)
    lenght = models.IntegerField()
    crew_min = models.IntegerField()
    crew_max = models.IntegerField()


class Event(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=128)
    participiants = models.ManyToManyField(
        to=Member,
        related_name="events_participant"
    )
    created_by = models.ForeignKey(
        to=Member,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events_created"
    )


class WorkTask(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=128)
    min_crew = models.IntegerField()
    participiants = models.ManyToManyField(
        to=Member,
        related_name="worktaasks_participant"
    )
    created_by = models.ForeignKey(
        to=Member,
        null=True,
        on_delete=models.SET_NULL,
        related_name="worktasks_created"
    )
