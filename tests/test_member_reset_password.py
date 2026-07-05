from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

MEMBER_RESET_URL = reverse("club:reset-password", args=[1])
MEMBER_RESET_URL_404 = reverse("club:reset-password", args=[999])


class TestPublicMemberResetPasswordView(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            username="member.user",
            password="pass321",
        )

    def test_member_reset_password_login_required(self):
        response = self.client.get(MEMBER_RESET_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateMemberResetPasswordView(TestCase):
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
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.client.force_login(self.test_user)

    def test_member_reset_password_uses_correct_template(self):
        response = self.client.get(MEMBER_RESET_URL)
        self.assertTemplateUsed(response, "club/password_reset_form.html")

    def test_member_reset_password_contains_correct_data(self):
        response = self.client.get(MEMBER_RESET_URL)
        self.assertEqual(response.context["member"], self.member)
        self.assertContains(response, "member.user")

    def test_member_reset_password_old_password_not_required(self):
        response = self.client.get(MEMBER_RESET_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertNotIn("old_password", form_fields)

    def test_member_reset_password_management_rights_required(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_RESET_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_member_reset_password_404_for_nonexistent_member(self):
        response = self.client.get(MEMBER_RESET_URL_404)
        self.assertEqual(response.status_code, 404)
