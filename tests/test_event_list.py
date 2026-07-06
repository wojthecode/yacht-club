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

EVENT_LIST_URL = reverse("club:event-list")


class TestEventListView(TestCase):
    def test_event_list_uses_correct_template(self):
        response = self.client.get(EVENT_LIST_URL)
        self.assertTemplateUsed(response, "club/event_list.html")

    def test_event_list_contains_events(self):
        response = self.client.get(EVENT_LIST_URL)
        self.assertIn("event_list", response.context)

    def test_event_list_shows_only_future_events(self):
        today = date.today()

        past = Event.objects.create(
            name="Past event",
            date=today - timedelta(days=1)
        )
        future = Event.objects.create(
            name="Future event",
            date=today + timedelta(days=1)
        )

        response = self.client.get(EVENT_LIST_URL)
        event_list = response.context["event_list"]

        self.assertIn(future, event_list)
        self.assertNotIn(past, event_list)

    def test_event_list_paginates_by_four(self):
        today = date.today()

        for i in range(7):
            Event.objects.create(
                name=f"Event {i}",
                date=today + timedelta(days=i+1)
            )

        response = self.client.get(EVENT_LIST_URL)
        response_page2 = self.client.get(EVENT_LIST_URL + "?page=2")
        event_list = response.context["event_list"]
        event_list_page2 = response_page2.context["event_list"]

        self.assertEqual(len(event_list), 4)
        self.assertEqual(len(event_list_page2), 3)
