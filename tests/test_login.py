from django.test import TestCase
from django.urls import reverse

LOGIN_URL = reverse("login")


class TestLoginView(TestCase):
    def test_login_uses_correct_template(self):
        response = self.client.get(LOGIN_URL)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_contains_correct_form_fields(self):
        response = self.client.get(LOGIN_URL)
        form_fields = set(response.context["form"].fields.keys())
        self.assertTrue({"username", "password"}.issubset(form_fields))

    def test_login_page_accessible_for_anonymous(self):
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, 200)
