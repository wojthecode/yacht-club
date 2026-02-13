from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from django.urls import reverse
from decimal import Decimal


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    management_rights = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SailingPermission(models.Model):
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
    sailing_permission = models.ForeignKey(
        to=SailingPermission,
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
    CATEGORIES = [
        ("A", "A (Ocean)"),
        ("B", "B (Offshore)"),
        ("C", "C (Inshore)"),
        ("D", "D (Sheltered Waters)"),
    ]

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

    model = models.CharField(max_length=64)
    rigging = models.CharField(max_length=64)
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default="B",
    )
    sail_area = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    length = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    beam = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    draft = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    crew_min = models.IntegerField(validators=[MinValueValidator(1)])
    crew_max = models.IntegerField()

    engine = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()
        if self.crew_max < self.crew_min:
            raise ValidationError(
                "crew_max must be greater or equal to crew_min"
            )

    def get_absolute_url(self):
        return reverse("club:boat-detail", kwargs={"pk": self.pk})


class BaseActivity(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=128)
    participants = models.ManyToManyField(
        to=Member,
        related_name="%(class)s_participant"
    )
    created_by = models.ForeignKey(
        to=Member,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created"
    )

    class Meta():
        abstract = True


class Event(BaseActivity):
    class Meta:
        ordering = ["date"]

    def get_absolute_url(self):
        return reverse("club:event-detail", kwargs={"pk": self.pk})


class WorkTask(BaseActivity):
    min_crew = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["date"]

    def get_absolute_url(self):
        return reverse("club:worktask-detail", kwargs={"pk": self.pk})
