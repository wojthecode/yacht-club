from datetime import date
from warnings import filterwarnings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from club.models import WorkTask

filterwarnings(
    "ignore",
    message="DateTimeField .* received a naive datetime",
    category=RuntimeWarning,
)

WORKTASK_DETAIL_URL = reverse("club:worktask-detail", args=[1])
WORKTASK_DETAIL_URL_404 = reverse("club:worktask-detail", args=[999])


class TestPublicWorkTaskDetailView(TestCase):
    def test_worktask_detail_login_required(self):
        response = self.client.get(WORKTASK_DETAIL_URL)
        self.assertNotEqual(response.status_code, 200)


class TestWorkTaskDetailView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.test_user = User.objects.create_user(
            username="test.user",
            password="pass321",
        )
        self.permission = Permission.objects.get(codename="active_member")
        self.test_user.user_permissions.add(self.permission)
        self.client.force_login(self.test_user)

        self.test_worktask = WorkTask.objects.create(
            name="Work Task",
            description="Work Task description contains: Hello Tester!",
            date=date.today(),
            min_crew=1,
        )

    def test_worktask_detail_uses_correct_template(self):
        response = self.client.get(WORKTASK_DETAIL_URL)
        self.assertTemplateUsed(response, "club/worktask_detail.html")

    def test_worktask_detail_view_contains_correct_data(self):
        response = self.client.get(WORKTASK_DETAIL_URL)
        self.assertEqual(response.context['worktask'], self.test_worktask)
        self.assertContains(response, "Hello Tester!")

    def test_worktask_detail_404_for_nonexistent_worktask(self):
        response = self.client.get(WORKTASK_DETAIL_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_worktask_detail_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        self.test_user.save()

        response = self.client.get(WORKTASK_DETAIL_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/no_permissions.html")
