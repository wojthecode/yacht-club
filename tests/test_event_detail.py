from datetime import date
from warnings import filterwarnings

from django.test import TestCase
from django.urls import reverse

from club.models import Event

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

EVENT_DETAIL_URL = reverse("club:event-detail", args=[1])
EVENT_DETAIL_URL_404 = reverse("club:event-detail", args=[999])


class TestEventDetailView(TestCase):
    def setUp(self):
        self.test_event = Event.objects.create(
            name="Event",
            description="Event description contains: Hello Tester!",
            date=date.today()
        )

    def test_event_detail_uses_correct_template(self):
        response = self.client.get(EVENT_DETAIL_URL)
        self.assertTemplateUsed(response, "club/event_detail.html")

    def test_event_detail_view_contains_correct_data(self):
        response = self.client.get(EVENT_DETAIL_URL)
        self.assertEqual(response.context['event'], self.test_event)
        self.assertContains(response, "Hello Tester!")

    def test_event_detail_404_for_nonexistent_event(self):
        response = self.client.get(EVENT_DETAIL_URL_404)
        self.assertEqual(response.status_code, 404)
