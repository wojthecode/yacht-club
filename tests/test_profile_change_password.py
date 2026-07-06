from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

PROFILE_CHANGE_PASSWORD_URL = reverse("password_change")


class TestPublicProfileChangePasswordView(TestCase):
    def test_profile_change_password_login_required(self):
        response = self.client.get(PROFILE_CHANGE_PASSWORD_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateProfileChangePasswordView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
            email="test@test.com",
        )
        self.client.force_login(self.test_user)

    def test_profile_change_password_uses_correct_template(self):
        response = self.client.get(PROFILE_CHANGE_PASSWORD_URL)
        self.assertTemplateUsed(response, "registration/password_change_form.html")

    def test_profile_change_password_contains_correct_member(self):
        response = self.client.get(PROFILE_CHANGE_PASSWORD_URL)
        self.assertEqual(response.context["user"], self.test_user)
        # self.assertContains(response, "test@test.com")

    def test_profile_change_password_requires_old_password_field(self):
        response = self.client.get(PROFILE_CHANGE_PASSWORD_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertIn("old_password", form_fields)

    def test_profile_change_password_hides_admin_fields(self):
        response = self.client.get(PROFILE_CHANGE_PASSWORD_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertNotIn("role", form_fields)
