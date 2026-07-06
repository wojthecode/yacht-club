from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role, Boat

BOAT_DELETE_URL = reverse("club:boat-delete", args=[1])
BOAT_DELETE_URL_404 = reverse("club:boat-delete", args=[999])


class TestPublicBoatDeleteView(TestCase):
    def test_boat_delete_login_required(self):
        response = self.client.get(BOAT_DELETE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateBoatDeleteView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        
        role_manager = Role.objects.create(
            name="role_manager",
            management_rights=True,
        )
        role_other = Role.objects.create(
            name="role_other",
            management_rights=False,
        )

        self.owner_user = User.objects.create_user(
            username="owner.user",
            password="pass321",
            role=role_other,
        )
        self.manager_user = User.objects.create_user(
            username="manager.user",
            password="pass321",
            role=role_manager,
        )
        self.other_user = User.objects.create_user(
            username="other.user",
            password="pass321",
            role=role_other,
        )

        self.boat = Boat.objects.create(
            name="Boat to delete",
            sail_area=10,
            length=5,
            beam=2,
            draft=1,
            crew_min=1,
            crew_max=3,
            owner=self.owner_user,
        )

    def test_boat_delete_uses_correct_template(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_DELETE_URL)
        self.assertTemplateUsed(response, "club/boat_confirm_delete.html")

    def test_boat_delete_uses_correct_data(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_DELETE_URL)
        self.assertEqual(response.context["boat"], self.boat)
        self.assertContains(response, "Boat to delete")

    def test_boat_delete_owner_can_view_confirmation(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 200)

    def test_boat_delete_owner_can_delete(self):
        self.client.force_login(self.owner_user)
        response = self.client.post(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Boat.objects.filter(id=1).exists())

    def test_boat_delete_manager_can_view_confirmation(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 200)

    def test_boat_delete_manager_can_delete(self):
        self.client.force_login(self.manager_user)
        response = self.client.post(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Boat.objects.filter(id=1).exists())

    def test_boat_delete_permission_denied_for_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_boat_delete_forbidden_for_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(BOAT_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_boat_delete_404_for_nonexistent_boat(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(BOAT_DELETE_URL_404)
        self.assertEqual(response.status_code, 404)
