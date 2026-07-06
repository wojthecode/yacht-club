from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

EVENT_CREATE_URL = reverse("club:event-create")


class TestPublicEventCreateView(TestCase):
    def test_event_create_login_required(self):
        response = self.client.get(EVENT_CREATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateEventCreateView(TestCase):
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

    def test_event_create_uses_correct_template(self):
        response = self.client.get(EVENT_CREATE_URL)
        self.assertTemplateUsed(response, "club/activity_form.html")

    def test_event_create_permission_granted(self):
        response = self.client.get(EVENT_CREATE_URL)
        self.assertContains(response, "id_name")
        self.assertNotContains(response, "You don't have permission")

    def test_event_create_permission_denied(self):
        self.test_user.role.management_rights = False   #type: ignore
        self.test_user.role.save()                      #type: ignore
        response = self.client.get(EVENT_CREATE_URL)
        self.assertNotContains(response, "id_name")
        self.assertContains(response, "You don't have permission")
