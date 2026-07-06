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

WORKTASK_TOGGLE_URL = reverse("club:toggle-worktask-participation", args=[1])
WORKTASK_DETAIL_URL = reverse("club:worktask-detail", args=[1])
WORKTASK_TOGGLE_URL_404 = reverse("club:toggle-worktask-participation", args=[999])


class TestPublicWorkTaskToggleParticipation(TestCase):
    def test_worktask_toggle_participation_login_required(self):
        response = self.client.get(WORKTASK_TOGGLE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.headers["Location"])


class TestPrivateWorkTaskToggleParticipation(TestCase):
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
            date=date.today(),
            min_crew=1,
        )

    def test_worktask_toggle_participation_permission_granted(self):
        response = self.client.get(WORKTASK_TOGGLE_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, WORKTASK_DETAIL_URL)

    def test_worktask_toggle_participation_switches_correctly(self):
        self.client.get(WORKTASK_TOGGLE_URL)
        self.assertIn(self.test_user, self.test_worktask.participants.all())
        self.client.get(WORKTASK_TOGGLE_URL)
        self.assertNotIn(
            self.test_user, self.test_worktask.participants.all()
        )

    def test_worktask_toggle_participation_404_for_nonexistent_worktask(self):
        response = self.client.get(WORKTASK_TOGGLE_URL_404)
        self.assertEqual(response.status_code, 404)

    def test_worktask_toggle_participation_permission_required(self):
        self.test_user.user_permissions.remove(self.permission)
        response = self.client.get(WORKTASK_TOGGLE_URL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "club/403.html")
