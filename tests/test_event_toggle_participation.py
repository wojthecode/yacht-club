from datetime import date
from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Event

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

EVENT_TOGGLE_URL = reverse("club:toggle-event-participation", args=[1])
EVENT_DETAIL_URL = reverse("club:event-detail", args=[1])
EVENT_TOGGLE_URL_404 = reverse("club:toggle-event-participation", args=[999])


class TestPublicEventToggleParticipation(TestCase):
    def test_event_toggle_participation_login_required(self):
        response = self.client.get(EVENT_TOGGLE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.headers["Location"])


class TestPrivateEventToggleParticipation(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
        )
        self.client.force_login(self.test_user)

        self.test_event = Event.objects.create(
            name="Event",
            date=date.today()
        )

    def test_event_toggle_participation_permission_granted(self):
        response = self.client.get(EVENT_TOGGLE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, EVENT_DETAIL_URL)

    def test_event_toggle_participation_switches_correctly(self):
        self.client.get(EVENT_TOGGLE_URL)
        self.assertIn(self.test_user, self.test_event.participants.all())
        self.client.get(EVENT_TOGGLE_URL)
        self.assertNotIn(self.test_user, self.test_event.participants.all())

    def test_event_toggle_participation_404_for_nonexistent_event(self):
        response = self.client.get(EVENT_TOGGLE_URL_404)
        self.assertEqual(response.status_code, 404)
