"""Energy scoreboard Test"""
import datetime

from django.test import TransactionTestCase
from apps.managers.resource_mgr import resource_mgr
from apps.managers.resource_mgr.models import EnergyUsage
from apps.utils import test_utils


class ResourceManagerTestCase(TransactionTestCase):
    """ResourceManager Test"""

    fixtures = ["base_settings.json"]

    def setUp(self):
        """Initialize a user and log them in."""
        self.user = test_utils.setup_user("user", "changeme")
        test_utils.set_competition_round()
        self.team = self.user.profile.team

    def testEnergy(self):
        """test Energy."""
        date = datetime.date.today()
        EnergyUsage(
            team=self.team,
            date=date,
            time=datetime.time(hour=15),
            usage=100,
        ).save()

        rank = resource_mgr.resource_team_rank_info(self.team, "energy")["rank"]
        usage = resource_mgr.team_resource_usage(date=date, team=self.team, resource="energy")
        self.assertEqual(rank, 1, "The team should be first rank.")
        self.assertEqual(usage, 100, "The team usage is not correct.")
