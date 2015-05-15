"""Team prize test"""
import datetime
from django.contrib.auth.models import User

from django.test import TransactionTestCase
from apps.managers.team_mgr.models import Group, Team
from apps.utils import test_utils
from apps.managers.challenge_mgr.models import RoundSetting


class DormTeamPrizeTests(TransactionTestCase):
    """
    Tests awarding a prize to a dorm team points winner.
    """

    def setUp(self):
        """
        Sets up a test team prize for the rest of the tests.
        This prize is not saved, as the round field is not yet set.
        """
        self.prize = test_utils.setup_prize(award_to="team_group", competition_type="points")

        self.current_round = "Round 1"
        test_utils.set_competition_round()

        # Create test groups, teams, and users.
        self.groups = [Group(name="Test Group %d" % i) for i in range(0, 2)]
        _ = [d.save() for d in self.groups]

        self.teams = [Team(name=str(i), group=self.groups[i % 2]) for i in range(0, 4)]
        _ = [f.save() for f in self.teams]

        self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 4)]

        # Assign users to teams.
        for index, user in enumerate(self.users):
            user.profile.team = self.teams[index % 4]
            user.profile.save()

    def testRoundLeader(self):
        """
        Tests that we can retrieve the overall individual points leader for a round prize.
        """
        self.prize.round = RoundSetting.objects.get(name="Round 1")
        self.prize.save()

        # Test one user will go ahead in points.
        profile = self.users[0].profile
        profile.add_points(10, datetime.datetime.today() + datetime.timedelta(minutes=1), "test")
        profile.save()

        self.assertEqual(self.prize.leader(profile.team), profile.team,
            "The user's team is not leading in the prize.")

        # Test a user in a different group.
        profile1 = self.users[1].profile
        profile1.add_points(profile.points() + 1,
            datetime.datetime.today() + datetime.timedelta(minutes=1), "test")
        profile1.save()

        self.assertEqual(self.prize.leader(profile.team), profile.team,
            "The leader for this prize in first users dorm should not change.")
        self.assertEqual(self.prize.leader(profile1.team), profile1.team,
            "The leader in profile1's dorm is not profile1.")

        # Test that a user in a different team but same dorm changes the leader for the
        # original user.
        profile2 = self.users[2].profile
        profile2.add_points(profile.points() + 1,
            datetime.datetime.today() + datetime.timedelta(minutes=1), "test")
        profile2.save()

        self.assertEqual(self.prize.leader(profile.team), profile2.team,
            "The leader for this prize did not change.")
        self.assertEqual(self.prize.leader(profile1.team), profile1.team,
            "The leader in profile1's dorm is not profile1.")

    def tearDown(self):
        """
        Deletes the created image file in prizes.
        """
        self.prize.image.delete()
        self.prize.delete()


class OverallTeamPrizeTest(TransactionTestCase):
    """
    Tests awarding a prize to a dorm team points winner.
    """

    def setUp(self):
        """
        Sets up a test team overall prize for the rest of the tests.
        This prize is not saved, as the round field is not yet set.
        """
        self.prize = test_utils.setup_prize(award_to="team_overall", competition_type="points")

        self.current_round = "Round 1"
        test_utils.set_competition_round()
        test_utils.create_teams(self)

    def testRoundLeader(self):
        """
        Tests that we can retrieve the overall individual points leader for a round prize.
        """
        self.prize.round = RoundSetting.objects.get(name="Round 1")
        self.prize.save()

        # Test one user will go ahead in points.
        profile = self.users[0].profile
        profile.add_points(10, datetime.datetime.today() + datetime.timedelta(minutes=1), "test")
        profile.save()

        self.assertEqual(self.prize.leader(profile.team), profile.team,
            "The user's team is not leading in the prize.")

        # Test that a user in a different team changes the leader for the original user.
        profile2 = self.users[2].profile
        profile2.add_points(profile.points() + 1,
            datetime.datetime.today() + datetime.timedelta(minutes=1), "test")
        profile2.save()

        self.assertEqual(self.prize.leader(profile.team), profile2.team,
            "The leader for this prize did not change.")

    def tearDown(self):
        """
        Deletes the created image file in prizes.
        """
        self.prize.image.delete()
        self.prize.delete()
