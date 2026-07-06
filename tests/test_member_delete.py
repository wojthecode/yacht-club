from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

MEMBER_DELETE_URL = reverse("club:member-delete", args=[1])
MEMBER_DELETE_URL_404 = reverse("club:member-delete", args=[999])


class TestPublicMemberDeleteView(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            username="member.user",
            password="pass321",
        )

    def test_member_delete_login_required(self):
        response = self.client.get(MEMBER_DELETE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateMemberDeleteView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        test_role = Role.objects.create(
            name="test_role",
            management_rights=True,
        )

        # Member to delete
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

    def test_member_delete_uses_correct_template(self):
        response = self.client.get(MEMBER_DELETE_URL)
        self.assertTemplateUsed(response, "club/member_confirm_delete.html")

    def test_member_delete_permission_granted(self):
        response = self.client.get(MEMBER_DELETE_URL)
        self.assertEqual(response.status_code, 200)

    def test_member_delete_contains_correct_data(self):
        response = self.client.get(MEMBER_DELETE_URL)
        self.assertEqual(response.context["member"], self.member)
        self.assertContains(response, "member.user")

    def test_member_delete_allowed_for_manager(self):
        User = get_user_model()
        response = self.client.post(MEMBER_DELETE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=1).exists())

    def test_member_delete_404_for_nonexistent_member(self):
        response = self.client.get(MEMBER_DELETE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_member_delete_permission_denied(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_member_delete_forbidden_for_non_manager(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.post(MEMBER_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")
