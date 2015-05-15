"""Scoreboard Test."""

import datetime
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from apps.managers.challenge_mgr import challenge_mgr
from apps.utils import test_utils
from apps.widgets.participation import participation
from apps.managers.cache_mgr import cache_mgr


class ParticipationTest(TransactionTestCase):
    """Scoreboard Test."""

    fixtures = ["base_settings.json", "base_pages.json"]

    def setUp(self):
        """
        setup
        """
        challenge_mgr.init()

        self.user = test_utils.setup_user(username="user", password="changeme")
        test_utils.set_competition_round()
        challenge_mgr.register_page_widget("learn", "participation")
        cache_mgr.clear()
        self.client.login(username="user", password="changeme")

    def testParticipation(self):
        """Test that the participation widget loads current round information."""

        # Give the user points in the round and then check the queryset used in the page.
        profile = self.user.profile
        profile.add_points(60, datetime.datetime.today(), "test")
        profile.save()

        participation.award_participation()

        response = self.client.get(reverse("learn_index"))

        self.assertEqual(response.context["view_objects"]["participation"][
            "round_participation_ranks"]["Round 1"]["participation_100"][0].team,
            profile.team,
            "The user's team should be leading.")
