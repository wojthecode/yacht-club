from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

PROFILE_URL = reverse("club:profile")


class TestProfileView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.user = User.objects.create_user(
            username="test.user",
            password="pass321",
            email="test@test.com",
        )

    def test_profile_login_required(self):
        response = self.client.get(PROFILE_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_profile_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(PROFILE_URL)
        self.assertTemplateUsed(response, "club/member_detail.html")

    def test_profile_contains_correct_data(self):
        self.client.force_login(self.user)
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.context["member"], self.user)
        self.assertContains(response, "test@test.com")
