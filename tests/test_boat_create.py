from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

BOAT_CREATE_URL = reverse("club:boat-create")


class TestPublicBoatCreateView(TestCase):
    def test_boat_create_login_required(self):
        response = self.client.get(BOAT_CREATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateBoatCreateView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.permission = Permission.objects.get(codename="active_member")
        test_role = Role.objects.create(
            name="test_role",
            management_rights=False,
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.test_user.user_permissions.add(self.permission)
        self.client.force_login(self.test_user)

    def test_boat_create_uses_correct_template(self):
        response = self.client.get(BOAT_CREATE_URL)
        self.assertTemplateUsed(response, "club/boat_form.html")

    def test_boat_create_no_management_rights_hides_club_fields(self):
        response = self.client.get(BOAT_CREATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertFalse({"club_owner", "owner"}.issubset(form_fields))

    def test_boat_create_management_rights_shows_club_fields(self):
        self.test_user.role.management_rights = True   #type: ignore
        self.test_user.role.save()                      #type: ignore
        response = self.client.get(BOAT_CREATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertTrue({"club_owner", "owner"}.issubset(form_fields))

    def test_boat_create_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        response = self.client.get(BOAT_CREATE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/no_permissions.html")
