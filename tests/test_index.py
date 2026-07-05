from datetime import date, timedelta
from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from club.models import Boat, Event

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

INDEX_URL = reverse("club:index")


class TestHomePageView(TestCase):
    def test_index_uses_correct_template(self):
        response = self.client.get(INDEX_URL)
        self.assertTemplateUsed(response, "club/index.html")

    def test_index_counts_boats_members_and_events(self):
        today = date.today()
        User = get_user_model()

        for i in range(3):
            Boat.objects.create(
                name=f"Boat_{i}",
                sail_area=10,
                length=5,
                beam=2,
                draft=1,
                crew_min=1,
                crew_max=3,
            )
        for i in range(7):
            User.objects.create(username=f"User_{i}")
        for i in range(4):
            Event.objects.create(
                name=f"Event {i}",
                date=today + timedelta(days=i+1),
            )

        response = self.client.get(INDEX_URL)

        self.assertEqual(response.context["num_boats"], 3)
        self.assertEqual(response.context["num_members"], 7)
        self.assertEqual(response.context["num_events"], 4)

    def test_index_shows_only_future_events(self):
        today = date.today()

        past = Event.objects.create(
            name="Past event",
            date=today - timedelta(days=1)
        )
        future = Event.objects.create(
            name="Future event",
            date=today + timedelta(days=1)
        )

        response = self.client.get(INDEX_URL)
        upcoming = response.context["upcoming"]

        self.assertIn(future, upcoming)
        self.assertNotIn(past, upcoming)

    def test_index_limits_upcoming_events_to_five(self):
        today = date.today()

        for i in range(7):
            Event.objects.create(
                name=f"Event {i}",
                date=today + timedelta(days=i+1)
            )

        response = self.client.get(INDEX_URL)
        upcoming = response.context["upcoming"]

        self.assertEqual(len(upcoming), 5)
