from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

TOGGLE_ACTIVE_URL = reverse("club:toggle-active-member", args=[1])
TOGGLE_ACTIVE_URL_404 = reverse("club:toggle-active-member", args=[999])


class TestPublicToggleActiveMemberView(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            username="member.user",
            password="pass321",
        )

    def test_toggle_active_member_login_required(self):
        response = self.client.get(TOGGLE_ACTIVE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateToggleActiveMemberView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.permission = Permission.objects.get(codename="active_member")
        test_role = Role.objects.create(
            name="test_role",
            management_rights=True,
        )

        # Member to edit
        self.member = User.objects.create_user(
            username="member.user",
            password="pass321",
        )
        self.member.user_permissions.add(self.permission)

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.test_user.user_permissions.add(self.permission)
        self.client.force_login(self.test_user)

    def test_toggle_active_member_toggles_status(self):
        # initial state
        self.assertTrue(self.member.user_permissions.filter(
            id=self.permission.id                               #type: ignore
        ).exists())

        self.client.get(TOGGLE_ACTIVE_URL)
        self.member.refresh_from_db()
        self.assertFalse(self.member.user_permissions.filter(
            id=self.permission.id                               #type: ignore
        ).exists())

        self.client.get(TOGGLE_ACTIVE_URL)
        self.member.refresh_from_db()
        self.assertTrue(self.member.user_permissions.filter(
            id=self.permission.id                               #type: ignore
        ).exists())

    def test_toggle_active_member_404_for_nonexistent_member(self):
        response = self.client.get(TOGGLE_ACTIVE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_toggle_active_member_permission_denied_for_non_manager(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(TOGGLE_ACTIVE_URL)
        self.assertEqual(response.status_code, 403)
