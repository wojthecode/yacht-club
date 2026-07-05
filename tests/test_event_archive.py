from datetime import date, timedelta
from warnings import filterwarnings

from django.test import TestCase
from django.urls import reverse

from club.models import Event

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

EVENT_ARCHIVE_URL = reverse("club:event-archive")


class TestEventArchiveIndexView(TestCase):
    def test_event_archive_uses_correct_template(self):
        response = self.client.get(EVENT_ARCHIVE_URL)
        self.assertTemplateUsed(response, "club/event_archive.html")

    def test_event_archive_contains_events(self):
        response = self.client.get(EVENT_ARCHIVE_URL)
        self.assertIn("latest", response.context)

    def test_event_archive_shows_only_past_events(self):
        today = date.today()

        past = Event.objects.create(
            name="Past event",
            date=today - timedelta(days=1)
        )
        future = Event.objects.create(
            name="Future event",
            date=today + timedelta(days=1)
        )

        response = self.client.get(EVENT_ARCHIVE_URL)
        latest = response.context["latest"]

        self.assertIn(past, latest)
        self.assertNotIn(future, latest)

    def test_event_archive_paginates_by_four(self):
        today = date.today()

        for i in range(10):
            Event.objects.create(
                name=f"Event {i}",
                date=today - timedelta(days=i+1)
            )

        response = self.client.get(EVENT_ARCHIVE_URL)
        response_page2 = self.client.get(EVENT_ARCHIVE_URL + "?page=2")
        latest = response.context["latest"]
        latest_page2 = response_page2.context["latest"]

        self.assertEqual(len(latest), 8)
        self.assertEqual(len(latest_page2), 2)
