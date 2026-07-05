from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

MEMBER_UPDATE_URL = reverse("club:member-update", args=[1])
MEMBER_UPDATE_URL_404 = reverse("club:member-update", args=[999])


class TestPublicMemberUpdateView(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            username="member.user",
            password="pass321",
        )

    def test_member_update_login_required(self):
        response = self.client.get(MEMBER_UPDATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateMemberUpdateView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        test_role = Role.objects.create(
            name="test_role",
            management_rights=True,
        )

        # Member to edit
        self.member = User.objects.create_user(
            username="member.user",
            password="pass321",
            email="test@test.com",
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.client.force_login(self.test_user)

    def test_member_update_uses_correct_template(self):
        response = self.client.get(MEMBER_UPDATE_URL)
        self.assertTemplateUsed(response, "club/member_form.html")

    def test_member_update_contains_correct_data(self):
        self.client.force_login(self.test_user)
        response = self.client.get(MEMBER_UPDATE_URL)
        self.assertEqual(response.context["member"], self.member)
        self.assertContains(response, "test@test.com")

    def test_member_update_management_rights_shows_admin_fields(self):
        response = self.client.get(MEMBER_UPDATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertIn("role", form_fields)

    def test_member_update_no_management_rights_required(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_UPDATE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_member_update_404_for_nonexistent_member(self):
        self.client.force_login(self.test_user)
        response = self.client.get(MEMBER_UPDATE_URL_404)
        self.assertEqual(response.status_code, 404)
