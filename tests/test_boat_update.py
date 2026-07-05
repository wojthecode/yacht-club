from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role, Boat

BOAT_UPDATE_URL = reverse("club:boat-update", args=[1])
BOAT_UPDATE_URL_404 = reverse("club:boat-update", args=[999])


class TestPublicBoatUpdateView(TestCase):
    def test_boat_update_login_required(self):
        response = self.client.get(BOAT_UPDATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateBoatUpdateView(TestCase):
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
            description="Boat description contains: Hello Tester!",
            sail_area=10,
            length=5,
            beam=2,
            draft=1,
            crew_min=1,
            crew_max=3,
            owner=self.owner_user,
        )

    def test_boat_update_uses_correct_template(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_UPDATE_URL)
        self.assertTemplateUsed(response, "club/boat_form.html")

    def test_boat_update_owner_sees_correct_data(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_UPDATE_URL)
        self.assertEqual(response.context["boat"], self.boat)
        self.assertContains(response, "Hello Tester!")

    def test_boat_update_no_management_rights_hides_club_fields(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(BOAT_UPDATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertFalse({"club_owner", "owner"}.issubset(form_fields))

    def test_boat_update_permission_denied_for_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(BOAT_UPDATE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_boat_update_manager_sees_correct_data(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(BOAT_UPDATE_URL)
        self.assertEqual(response.context["boat"], self.boat)
        self.assertContains(response, "Hello Tester!")

    def test_boat_update_management_rights_shows_club_fields(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(BOAT_UPDATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertTrue({"club_owner", "owner"}.issubset(form_fields))

    def test_boat_update_404_for_nonexistent_boat(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(BOAT_UPDATE_URL_404)
        self.assertEqual(response.status_code, 404)
