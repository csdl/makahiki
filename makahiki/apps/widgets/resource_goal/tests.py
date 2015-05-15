"""Energy Goal Test"""
import datetime

from apps.managers.team_mgr.models import Group
from apps.managers.player_mgr.models import Profile

from django.test import TransactionTestCase
from django.contrib.auth.models import User

from apps.managers.team_mgr.models import Team
from apps.utils import test_utils
from apps.widgets.resource_goal import resource_goal
from apps.widgets.resource_goal.models import EnergyGoalSetting, EnergyBaselineDaily, EnergyGoal
from apps.managers.resource_mgr.models import EnergyUsage


class TeamEnergyGoalTest(TransactionTestCase):
    """Team Energy Goal Test"""
    def setUp(self):
        """setup"""
        test_utils.set_competition_round()

        group = Group.objects.create(name="Test Group")
        group.save()
        self.team = Team.objects.create(
            group=group,
            name="A"
        )

        self.user = User.objects.create_user("user", "user@test.com")
        profile = self.user.profile
        profile.team = self.team
        profile.save()

    def testTeamEnergyGoal(self):
        """Test energy goal"""
        profile = self.user.profile
        points = profile.points()

        goal_settings = EnergyGoalSetting.objects.filter(team=self.team)
        if not goal_settings:
            goal_settings = EnergyGoalSetting(team=self.team,
                goal_percent_reduction=5,
                goal_points=20,
                baseline_method="Fixed",
                manual_entry=True,
                manual_entry_time=datetime.time(hour=15),
            )
            goal_settings.save()
        else:
            goal_settings = goal_settings[0]

        goal_baseline = EnergyBaselineDaily(
            team=self.team,
            day=datetime.date.today().weekday(),
            usage=150,
        )
        goal_baseline.save()
        energy_data = EnergyUsage(
            team=self.team,
            date=datetime.date.today(),
            time=datetime.time(hour=15),
            usage=100,
        )
        energy_data.save()

        today = datetime.date.today()
        resource_goal.check_team_resource_goal("energy", self.team, today)

        profile = Profile.objects.get(user__username="user")
        self.assertEqual(profile.points(), points,
            "User that did not complete the setup process should not be awarded points.")

        profile.setup_complete = True
        profile.save()

        energy_data.usage = 150
        energy_data.save()

        EnergyGoal.objects.filter(team=self.team, date=today).delete()
        resource_goal.check_team_resource_goal("energy", self.team, today)

        profile = Profile.objects.get(user__username="user")
        self.assertEqual(profile.points(), points,
            "Team that failed the goal should not be awarded any points.")

        energy_data.usage = 100
        energy_data.save()
        EnergyGoal.objects.filter(team=self.team, date=today).delete()
        resource_goal.check_team_resource_goal("energy", self.team, today)

        profile = Profile.objects.get(user__username="user")
        self.assertEqual(profile.points(), points + goal_settings.goal_points,
            "User that setup their profile should be awarded points.")
