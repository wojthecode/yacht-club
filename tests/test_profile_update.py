from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

PROFILE_UPDATE_URL = reverse("club:profile-update")


class TestPublicProfileUpdateView(TestCase):
    def test_profile_update_login_required(self):
        response = self.client.get(PROFILE_UPDATE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateProfileUpdateView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.user = User.objects.create_user(
            username="test.user",
            password="pass321",
            email="test@test.com",
        )
        self.client.force_login(self.user)

    def test_profile_update_uses_correct_template(self):
        response = self.client.get(PROFILE_UPDATE_URL)
        self.assertTemplateUsed(response, "club/member_form.html")

    def test_profile_update_contains_correct_data(self):
        response = self.client.get(PROFILE_UPDATE_URL)
        self.assertEqual(response.context["member"], self.user)
        self.assertContains(response, "test@test.com")

    def test_profile_update_hides_admin_fields(self):
        response = self.client.get(PROFILE_UPDATE_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertNotIn("role", form_fields)
