"""Energy scoreboard Test"""
import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.challenge_mgr.models import GameInfo

from apps.utils import test_utils
from apps.widgets.resource_goal.models import EnergyGoal


class EnergyFunctionalTestCase(TransactionTestCase):
    """Energy Test"""

    fixtures = ["base_settings.json"]

    def setUp(self):
        """Initialize a user and log them in."""
        self.user = test_utils.setup_user(username="user", password="changeme")
        self.team = self.user.profile.team
        test_utils.set_competition_round()

        challenge_mgr.register_page_widget("energy", "resource_scoreboard.energy")
        game, _ = GameInfo.objects.get_or_create(name="Energy Game")
        game.enabled = True
        game.save()

        self.client.login(username="user", password="changeme")

    def testIndex(self):
        """Check that we can load the index page."""
        response = self.client.get(reverse("energy_index"))
        self.failUnlessEqual(response.status_code, 200)

    def testEnergyScoreboard(self):
        """test Energy scoreboard."""
        cache_mgr.clear()
        response = self.client.get(reverse("energy_index"))
        goals = response.context["view_objects"]["resource_scoreboard__energy"][
                "round_resource_goal_ranks"]["Round 1"]
        for goal in goals:
            self.assertEqual(goal["completions"], 0, "No team should have completed a goal.")

        energy_goal = EnergyGoal.objects.create(
            team=self.team,
            date=datetime.date.today(),
            goal_status="Over the goal",
        )

        response = self.client.get(reverse("energy_index"))
        goals = response.context["view_objects"]["resource_scoreboard__energy"][
                "round_resource_goal_ranks"]["Round 1"]
        for goal in goals:
            self.assertEqual(goal["completions"], 0, "No team should have completed a goal.")

        energy_goal.goal_status = "Below the goal"
        energy_goal.save()
        cache_mgr.clear()

        response = self.client.get(reverse("energy_index"))
        goals = response.context["view_objects"]["resource_scoreboard__energy"][
                "round_resource_goal_ranks"]["Round 1"]
        for team in goals:
            if team["team__name"] == self.team.name:
                # print team.teamenergygoal_set.all()
                self.assertEqual(team["completions"], 1,
                    "User's team should have completed 1 goal, but completed %d" % team[
                                                                                    "completions"])
            else:
                self.assertEqual(team["completions"], 0, "No team should have completed a goal.")
