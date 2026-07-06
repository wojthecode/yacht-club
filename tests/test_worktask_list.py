from datetime import date, timedelta
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

WORKTASK_LIST_URL = reverse("club:worktask-list")


class TestPublicWorkTaskListView(TestCase):
    def test_worktask_list_login_required(self):
        response = self.client.get(WORKTASK_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class TestWorkTaskListView(TestCase):
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

    def test_worktask_list_uses_correct_template(self):
        response = self.client.get(WORKTASK_LIST_URL)
        self.assertTemplateUsed(response, "club/worktask_list.html")

    def test_worktask_list_contains_worktasks(self):
        response = self.client.get(WORKTASK_LIST_URL)
        self.assertIn("worktask_list", response.context)

    def test_worktask_list_shows_only_future_worktasks(self):
        today = date.today()

        past = WorkTask.objects.create(
            name="Past work task",
            date=today - timedelta(days=1),
            min_crew=1,
        )
        future = WorkTask.objects.create(
            name="Future work task",
            date=today + timedelta(days=1),
            min_crew=1,
        )

        response = self.client.get(WORKTASK_LIST_URL)
        worktask_list = response.context["worktask_list"]

        self.assertIn(future, worktask_list)
        self.assertNotIn(past, worktask_list)

    def test_worktask_list_paginates_by_four(self):
        today = date.today()

        for i in range(7):
            WorkTask.objects.create(
                name=f"Work task {i}",
                date=today + timedelta(days=i+1),
                min_crew=1,
            )

        response = self.client.get(WORKTASK_LIST_URL)
        response_page2 = self.client.get(WORKTASK_LIST_URL + "?page=2")
        worktask_list = response.context["worktask_list"]
        worktask_list_page2 = response_page2.context["worktask_list"]

        self.assertEqual(len(worktask_list), 4)
        self.assertEqual(len(worktask_list_page2), 3)

    def test_worktask_list_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        response = self.client.get(WORKTASK_LIST_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/no_permissions.html")
