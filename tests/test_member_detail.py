from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

MEMBER_DETAIL_URL = reverse("club:member-detail", args=[1])
MEMBER_DETAIL_URL_404 = reverse("club:member-detail", args=[999])


class TestPublicMemberDetailView(TestCase):
    def test_member_detail_login_required(self):
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateMemberDetailView(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.permission = Permission.objects.get(codename="active_member")

        test_role = Role.objects.create(
            name="test_role",
            management_rights=False,
        )
        member_role = Role.objects.create(
            name="Member",
            management_rights=False,
        )

        self.member = User.objects.create_user(
            username="member.user",
            first_name="Member",
            last_name="Name",
            phone="+01 234 56 78",
            phone_visibility=False,
            password="pass321",
            role=member_role,
        )

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            role=test_role,
        )
        self.test_user.user_permissions.add(self.permission)

        self.client.force_login(self.test_user)

    def test_member_detail_uses_correct_template(self):
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertTemplateUsed(response, "club/member_detail.html")

    def test_member_detail_contains_correct_data(self):
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertEqual(response.context["member"], self.member)
        self.assertContains(response, "Member Name")

    def test_member_detail_404_for_nonexistent_member(self):
        response = self.client.get(MEMBER_DETAIL_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_member_detail_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/no_permissions.html")
        
    def test_member_detail_management_user_sees_toggle_active_member(self):
        self.test_user.role.management_rights = True        #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertContains(response, "toggle_active_member")

    def test_member_detail_regular_user_cant_see_toggle_active_member(self):
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertNotContains(response, "toggle_active_member")
        
    def test_member_detail_management_user_sees_phone_number(self):
        self.test_user.role.management_rights = True        #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertContains(response, "+01 234 56 78")

    def test_member_detail_regular_user_cant_see_phone_number(self):
        response = self.client.get(MEMBER_DETAIL_URL)
        self.assertNotContains(response, "+01 234 56 78")
