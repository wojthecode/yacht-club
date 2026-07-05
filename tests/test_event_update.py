from datetime import date
from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Event, Role

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

EVENT_UPDATE_URL = reverse("club:event-update", args=[1])
EVENT_UPDATE_URL_404 = reverse("club:event-update", args=[999])


class TestPublicEventUpdateView(TestCase):
    def test_event_update_login_required(self):
        response = self.client.get(EVENT_UPDATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateEventUpdateView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        test_role = Role.objects.create(
            name="test_role",
            management_rights=True,
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.client.force_login(self.test_user)

        self.test_event = Event.objects.create(
            name="Event",
            description="Event description contains: Hello Tester!",
            date=date.today()
        )

    def test_event_update_uses_correct_template(self):
        response = self.client.get(EVENT_UPDATE_URL)
        self.assertTemplateUsed(response, "club/activity_form.html")

    def test_event_update_permission_granted(self):
        response = self.client.get(EVENT_UPDATE_URL)
        self.assertContains(response, "id_name")
        self.assertNotContains(response, "You don't have permission")

    def test_event_update_uses_correct_data(self):
        response = self.client.get(EVENT_UPDATE_URL)
        self.assertEqual(response.context['event'], self.test_event)
        self.assertContains(response, "Hello Tester!")

    def test_event_update_404_for_nonexistent_event(self):
        response = self.client.get(EVENT_UPDATE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_event_update_permission_denied(self):
        self.test_user.role.management_rights = False   #type: ignore
        self.test_user.role.save()                      #type: ignore
        response = self.client.get(EVENT_UPDATE_URL)
        self.assertNotContains(response, "id_name")
        self.assertContains(response, "You don't have permission")
