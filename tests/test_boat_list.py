from django.test import TestCase
from django.urls import reverse

from club.models import Boat

BOAT_LIST_URL = reverse("club:boat-list")


class TestBoatListView(TestCase):
    def setUp(self):
        names = ["Boatone", "Boattwo", "Boathree", "Boatfour", "TheShip"]
        for i in range(5):
            Boat.objects.create(
                name=names[i],
                sail_area=10,
                length=5,
                beam=2,
                draft=1,
                crew_min=1,
                crew_max=3,
            )

    def test_boat_list_uses_correct_template(self):
        response = self.client.get(BOAT_LIST_URL)
        self.assertTemplateUsed(response, "club/boat_list.html")

    def test_boat_list_contains_boats(self):
        response = self.client.get(BOAT_LIST_URL)
        self.assertIn("boat_list", response.context)

    def test_boat_list_paginates_by_three(self):
        response = self.client.get(BOAT_LIST_URL)
        response_page2 = self.client.get(BOAT_LIST_URL + "?page=2")
        boat_list = response.context["boat_list"]
        boat_list_page2 = response_page2.context["boat_list"]

        self.assertEqual(len(boat_list), 3)
        self.assertEqual(len(boat_list_page2), 2)

    def test_boat_list_search(self):
        boats = Boat.objects.filter(name__icontains="Ship")
        response = self.client.get(BOAT_LIST_URL + "?name=Ship")
        self.assertEqual(list(boats), list(response.context["boat_list"]))

    def test_boat_list_search_with_pagination(self):
        response = self.client.get(BOAT_LIST_URL + "?name=Boat")
        response_page2 = self.client.get(BOAT_LIST_URL + "?name=Boat&page=2")
        boat_list = response.context["boat_list"]
        boat_list_page2 = response_page2.context["boat_list"]

        self.assertEqual(len(boat_list), 3)
        self.assertEqual(len(boat_list_page2), 1)
