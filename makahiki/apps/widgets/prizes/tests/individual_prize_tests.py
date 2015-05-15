"""Individual test"""
import datetime

from django.test import TransactionTestCase
from django.contrib.auth.models import User

from apps.managers.player_mgr.models import Profile
from apps.utils import test_utils
from apps.managers.challenge_mgr.models import RoundSetting


class OverallPrizeTest(TransactionTestCase):
    """
    Tests awarding a prize to the individual overall points winner.
    """

    def setUp(self):
        """
        Sets up a test individual prize for the rest of the tests.
        This prize is not saved, as the round field is not yet set.
        """
        self.prize = test_utils.setup_prize(award_to="individual_overall",
                                            competition_type="points")

        self.current_round = "Round 1"

        test_utils.set_competition_round()

        # Create test users.
        self.users = [User.objects.create_user("test%d" % i, "test@test.com") for i in range(0, 3)]

    def testRoundLeader(self):
        """
        Tests that we can retrieve the overall individual points leader for a round prize.
        """
        self.prize.round = RoundSetting.objects.get(name="Round 1")
        self.prize.save()

        # Test one user
        profile = self.users[0].profile
        top_points = Profile.objects.all()[0].points()
        profile.add_points(top_points + 1,
                           datetime.datetime.today() - datetime.timedelta(minutes=1),
                           "test")
        profile.save()

        self.assertEqual(self.prize.leader(), profile,
            "Current prize leader is not the leading user.")

        # Have another user move ahead in points
        profile2 = self.users[1].profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(), "test")
        profile2.save()

        self.assertEqual(self.prize.leader(), profile2, "User 2 should be the leading profile.")

        # Have this user get the same amount of points, but an earlier award date.
        profile3 = self.users[2].profile
        profile3.add_points(profile2.points(),
            datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
        profile3.save()

        self.assertEqual(self.prize.leader(), profile2,
            "User 2 should still be the leading profile.")

    def tearDown(self):
        """
        Deletes the created image file in prizes.
        """
        self.prize.image.delete()
        self.prize.delete()


class TeamPrizeTest(TransactionTestCase):
    """
    Tests awarding a prize to the individual on each team with the most points.
    """

    def setUp(self):
        """
        Sets up a test individual prize for the rest of the tests.
        This prize is not saved, as the round field is not yet set.
        """
        self.prize = test_utils.setup_prize(award_to="individual_team", competition_type="points")

        self.current_round = "Round 1"

        test_utils.set_competition_round()

        test_utils.create_teams(self)

    def testRoundLeader(self):
        """
        Tests that we can retrieve the overall individual points leader for a round prize.
        """
        self.prize.round = RoundSetting.objects.get(name="Round 1")
        self.prize.save()

        # Test one user
        profile = self.users[0].profile
        profile.add_points(10, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(self.prize.leader(team=profile.team), profile,
            "Current prize leader is not the leading user.")

        # Have a user on the same team move ahead in points.
        profile3 = self.users[2].profile
        profile3.add_points(11, datetime.datetime.today(), "test")
        profile3.save()

        self.assertEqual(self.prize.leader(team=profile.team), profile3,
            "User 3 should be the the leader.")

        # Try a user on a different team.
        profile2 = self.users[1].profile
        profile2.add_points(20, datetime.datetime.today(), "test")
        profile2.save()

        self.assertEqual(self.prize.leader(team=profile.team), profile3,
            "User 3 should be the leading profile on user 1's team.")
        self.assertEqual(self.prize.leader(team=profile2.team), profile2,
            "User 2 should be the leading profile on user 2's team.")

    def tearDown(self):
        """
        Deletes the created image file in prizes.
        """
        self.prize.image.delete()
        self.prize.delete()
