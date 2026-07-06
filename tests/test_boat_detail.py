from django.test import TestCase
from django.urls import reverse

from club.models import Boat

BOAT_DETAIL_URL = reverse("club:boat-detail", args=[1])
BOAT_DETAIL_URL_404 = reverse("club:boat-detail", args=[999])


class TestBoatDetailView(TestCase):
    def setUp(self):
        self.boat = Boat.objects.create(
            name="Boat",
            description="Boat description contains: Hello Tester!",
            sail_area=10,
            length=5,
            beam=2,
            draft=1,
            crew_min=1,
            crew_max=3,
        )

    def test_boat_detail_uses_correct_template(self):
        response = self.client.get(BOAT_DETAIL_URL)
        self.assertTemplateUsed(response, "club/boat_detail.html")

    def test_boat_detail_contains_correct_data(self):
        response = self.client.get(BOAT_DETAIL_URL)
        self.assertEqual(response.context["boat"], self.boat)
        self.assertContains(response, "Hello Tester!")

    def test_boat_detail_404_for_nonexistent_boat(self):
        response = self.client.get(BOAT_DETAIL_URL_404)
        self.assertEqual(response.status_code, 404)
