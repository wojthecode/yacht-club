from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role

MEMBER_CREATE_URL = reverse("club:member-create")


class TestPublicMemberCreateView(TestCase):
    def test_member_create_uses_correct_template(self):
        response = self.client.get(MEMBER_CREATE_URL)
        self.assertTemplateUsed(response, "club/member_form.html")

    def test_member_create_hides_admin_fields_for_guest(self):
        response = self.client.get(MEMBER_CREATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertNotIn("role", form_fields)


class TestPrivateMemberCreateView(TestCase):
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

    def test_member_create_management_rights_shows_admin_fields(self):
        response = self.client.get(MEMBER_CREATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertIn("role", form_fields)

    def test_member_create_no_management_rights_redirects_to_profile(self):
        self.test_user.role.management_rights = False   #type: ignore
        self.test_user.role.save()                      #type: ignore
        response = self.client.get(MEMBER_CREATE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/profile/", response.headers["Location"])
