"""Scoreboard Test."""

import datetime
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.utils import test_utils


class ScoreboardTest(TransactionTestCase):
    """Scoreboard Test."""

    def setUp(self):
        """
        setup
        """
        challenge_mgr.init()

        self.user = test_utils.setup_user(username="user", password="changeme")

        challenge_mgr.register_page_widget("learn", "smartgrid")
        challenge_mgr.register_page_widget("learn", "scoreboard")
        cache_mgr.clear()

        self.client.login(username="user", password="changeme")

    def testScoreboard(self):
        """Test that the scoreboard loads current round information."""

        test_utils.set_competition_round()

        # Give the user points in the round and then check the queryset used in the page.
        profile = self.user.profile
        profile.add_points(10, datetime.datetime.today(), "test")
        profile.save()

        response = self.client.get(reverse("learn_index"))

        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["team_standings"][0]["profile__team__name"],
            profile.team.name,
            "The user's team should be leading.")
        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["profile_standings"][0]["profile__name"],
            profile.name,
            "The user's should be leading the overall standings.")
        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["user_team_standings"][0],
            profile,
            "The user should be leading in their own team.")
        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["team_standings"][0]["points"],
            10,
            "The user's team should have 10 points this round.")
        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["profile_standings"][0]["points"],
            10,
            "The user should have 10 points this round.")
        self.assertEqual(response.context["view_objects"]["scoreboard"][
            "round_standings"]["Round 1"]["user_team_standings"][0].current_round_points(),
            10,
            "The user should have 10 points this round.")
