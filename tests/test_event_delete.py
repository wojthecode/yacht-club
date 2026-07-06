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

EVENT_DELETE_URL = reverse("club:event-delete", args=[1])
EVENT_DELETE_URL_404 = reverse("club:event-delete", args=[999])


class TestPublicEventDeleteView(TestCase):
    def test_event_delete_login_required(self):
        response = self.client.get(EVENT_DELETE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateEventDeleteView(TestCase):
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
            name="Event to delete",
            date=date.today()
        )

    def test_event_delete_uses_correct_template(self):
        response = self.client.get(EVENT_DELETE_URL)
        self.assertTemplateUsed(response, "club/activity_confirm_delete.html")

    def test_event_delete_permission_granted(self):
        response = self.client.get(EVENT_DELETE_URL)
        self.assertEqual(response.status_code, 200)

    def test_event_delete_uses_correct_data(self):
        response = self.client.get(EVENT_DELETE_URL)
        self.assertEqual(response.context['event'], self.test_event)
        self.assertContains(response, "Event to delete")

    def test_event_delete_allowed_for_manager(self):
        response = self.client.post(EVENT_DELETE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(id=1).exists())

    def test_event_delete_404_for_nonexistent_event(self):
        response = self.client.get(EVENT_DELETE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_event_delete_permission_denied(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(EVENT_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_event_delete_forbidden_for_non_manager(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.post(EVENT_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")
