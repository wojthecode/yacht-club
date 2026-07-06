from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

MEMBER_LIST_URL = reverse("club:member-list")


class TestPublicMemberListView(TestCase):
    def test_member_list_login_required(self):
        response = self.client.get(MEMBER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateMemberListView(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.permission = Permission.objects.get(codename="active_member")

        test_role = Role.objects.create(
            name="role_manager",
            management_rights=False,
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.test_user.user_permissions.add(self.permission)

        self.client.force_login(self.test_user)

    def test_member_list_users_correct_template(self):
        response = self.client.get(MEMBER_LIST_URL)
        self.assertTemplateUsed(response, "club/member_list.html")

    def test_member_list_contains_members(self):
        response = self.client.get(MEMBER_LIST_URL)
        self.assertIn("member_list", response.context)

    def test_member_list_paginates_by_ten(self):
        User = get_user_model()
        for i in range(12):
            User.objects.create_user(
                username=f"user_{i}",
            )
        response_page1 = self.client.get(MEMBER_LIST_URL)
        response_page2 = self.client.get(MEMBER_LIST_URL + "?page=2")
        member_list_page1 = response_page1.context["member_list"]
        member_list_page2 = response_page2.context["member_list"]
        self.assertEqual(len(member_list_page1), 10)
        self.assertEqual(len(member_list_page2), 3)

    def test_member_list_access_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        response = self.client.get(MEMBER_LIST_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/no_permissions.html")

    def test_member_list_management_user_sees_toggle_active_member(self):
        self.test_user.role.management_rights = True        #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_LIST_URL)
        self.assertContains(response, "toggle_active_member")

    def test_member_list_regular_user_cant_see_toggle_active_member(self):
        response = self.client.get(MEMBER_LIST_URL)
        self.assertNotContains(response, "toggle_active_member")
