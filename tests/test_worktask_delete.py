from datetime import date
from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from club.models import Role, WorkTask

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

WORKTASK_DELETE_URL = reverse("club:worktask-delete", args=[1])
WORKTASK_DELETE_URL_404 = reverse("club:worktask-delete", args=[999])


class TestPublicWorkTaskDeleteView(TestCase):
    def test_worktask_delete_login_required(self):
        response = self.client.get(WORKTASK_DELETE_URL)
        self.assertNotEqual(response.status_code, 200)


class TestPrivateWorkTaskDeleteView(TestCase):
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

        self.test_worktask = WorkTask.objects.create(
            name="Work Task to delete",
            date=date.today(),
            min_crew=1,
        )

    def test_worktask_delete_uses_correct_template(self):
        response = self.client.get(WORKTASK_DELETE_URL)
        self.assertTemplateUsed(response, "club/activity_confirm_delete.html")

    def test_worktask_delete_permission_granted(self):
        response = self.client.get(WORKTASK_DELETE_URL)
        self.assertEqual(response.status_code, 200)

    def test_worktask_delete_uses_correct_data(self):
        response = self.client.get(WORKTASK_DELETE_URL)
        self.assertEqual(response.context['worktask'], self.test_worktask)
        self.assertContains(response, "Work Task to delete")

    def test_worktask_delete_allowed_for_manager(self):
        response = self.client.post(WORKTASK_DELETE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(WorkTask.objects.filter(id=1).exists())

    def test_worktask_delete_404_for_nonexistent_worktask(self):
        response = self.client.get(WORKTASK_DELETE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_worktask_delete_permission_denied(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.get(WORKTASK_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")

    def test_worktask_delete_forbidden_for_non_manager(self):
        self.test_user.role.management_rights = False       #type: ignore
        self.test_user.role.save()                          #type: ignore
        response = self.client.post(WORKTASK_DELETE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")
