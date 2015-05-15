"""
test score_mgr
"""

import datetime
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr.models import Group, Team
from apps.managers.score_mgr.models import ScoreboardEntry, PointsTransaction
from apps.utils import test_utils


class ScoreboardEntryUnitTests(TransactionTestCase):
    """scoreboard test"""

    def setUp(self):
        """Generate test. Set the competition settings to the current date for testing."""
        self.user = User(username="test_user", password="changeme")
        self.user.save()

        self.current_round = "Round 1"
        test_utils.set_competition_round()

        self.user.profile.add_points(10, datetime.datetime.today(), "test")

    def testUserOverallRoundRankWithPoints(self):
        """Tests that the overall rank calculation for a user in a round is
        correct based on points."""
        top_entry = ScoreboardEntry.objects.filter(
            round_name=self.current_round).order_by("-points")[0]
        entry, _ = ScoreboardEntry.objects.get_or_create(
            profile=self.user.profile,
            round_name=self.current_round,
            )
        entry.points = top_entry.points + 1
        entry.last_awarded_submission = datetime.datetime.today()
        entry.save()

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         1,
                         "Check user is ranked #1 for the current round.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        entry2, _ = ScoreboardEntry.objects.get_or_create(
            profile=profile2,
            round_name=self.current_round,
            )
        entry2.points = entry.points + 1
        entry2.last_awarded_submission = entry.last_awarded_submission
        entry2.save()

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         2,
                         "Check user is now second.")

    def testUserOverallRoundRankWithSubmissionDate(self):
        """Tests that the overall rank calculation for a user in a round is
        correct based on submission date."""
        top_entry = ScoreboardEntry.objects.filter(
            round_name=self.current_round).order_by("-points")[0]
        entry, _ = ScoreboardEntry.objects.get_or_create(
            profile=self.user.profile,
            round_name=self.current_round,
            )
        entry.points = top_entry.points + 1
        entry.last_awarded_submission = datetime.datetime.today() - datetime.timedelta(days=3)
        entry.save()

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         1,
                         "Check user is ranked #1 for the current round.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        entry2, _ = ScoreboardEntry.objects.get_or_create(
            profile=profile2,
            round_name=self.current_round,
            )
        entry2.points = entry.points
        entry2.last_awarded_submission = datetime.datetime.today()
        entry2.save()

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         2,
                         "Check user is now second.")

    def testUserTeamRoundRankWithPoints(self):
        """Tests that the team rank calculation for a round is correct based
        on points."""
        # Setup dorm
        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        profile = self.user.profile
        profile.team = team
        profile.save()

        # Set up entry
        top_entry = ScoreboardEntry.objects.filter(
            round_name=self.current_round).order_by("-points")[0]
        entry, _ = ScoreboardEntry.objects.get_or_create(
            profile=self.user.profile,
            round_name=self.current_round,
            )
        entry.points = top_entry.points + 1
        entry.last_awarded_submission = datetime.datetime.today()
        entry.save()

        self.assertEqual(score_mgr.player_rank_in_team(self.user.profile,
                                                        self.current_round),
                         1,
                         "Check user is ranked #1 for the current round.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()
        profile2 = user2.profile
        profile2.team = team
        profile2.save()

        entry2, _ = ScoreboardEntry.objects.get_or_create(
            profile=profile2,
            round_name=self.current_round,
            )
        entry2.points = entry.points + 1
        entry2.last_awarded_submission = entry.last_awarded_submission
        entry2.save()

        self.assertEqual(score_mgr.player_rank_in_team(self.user.profile,
                                                        self.current_round),
                         2,
                         "Check user is now second.")

    def testUserTeamRoundRankWithSubmissionDate(self):
        """Tests that the team rank calculation for a round is correct based
        on points."""
        # Set up dorm
        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        # Create the entry for the test user
        profile = self.user.profile
        profile.team = team
        profile.save()
        top_entry = ScoreboardEntry.objects.filter(
            round_name=self.current_round).order_by("-points")[0]
        entry, _ = ScoreboardEntry.objects.get_or_create(
            profile=self.user.profile,
            round_name=self.current_round,
            )
        entry.points = top_entry.points + 1
        entry.last_awarded_submission = datetime.datetime.today() - \
                                        datetime.timedelta(days=3)
        entry.save()

        # Create another test user
        user2 = User(username="test_user2", password="changeme")
        user2.save()
        profile2 = user2.profile
        profile2.team = team
        profile2.save()

        entry2, _ = ScoreboardEntry.objects.get_or_create(
            profile=profile2,
            round_name=self.current_round,
            )
        entry2.points = entry.points
        entry2.last_awarded_submission = datetime.datetime.today()
        entry2.save()

        self.assertEqual(score_mgr.player_rank_in_team(self.user.profile,
                                                        self.current_round),
                         2,
                         "Check user is now second.")

    def testRoundRankWithoutEntry(self):
        """Tests that the overall rank calculation is correct even if a user
        has not done anything yet."""
        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        # Rank will be the number of users who have points plus one.
        overall_rank = 1
        team_rank = 1

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         overall_rank,
                         "Check user is last overall for the current round.")
        self.assertEqual(score_mgr.player_rank_in_team(self.user.profile,
                                                        self.current_round),
                         team_rank,
                         "Check user is last in their team for the current "
                         "round.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(10, datetime.datetime.today(), "test")

        self.assertEqual(score_mgr.player_rank(self.user.profile,
                                                           self.current_round),
                         overall_rank + 1,
                         "Check that the user's overall rank has moved down.")
        self.assertEqual(score_mgr.player_rank_in_team(self.user.profile,
                                                        self.current_round),
                         team_rank + 1,
                         "Check that the user's team rank has moved down.")


class PointsLogTest(TransactionTestCase):
    """test points log"""
    def setUp(self):
        self.user = User.objects.create_user("test", "test@test.com")

        test_utils.set_competition_round()

    def testAddPoints(self):
        """
        Test that adding points creates a new entry in the points log.
        """
        log_count = PointsTransaction.objects.count()
        profile = self.user.profile
        profile.add_points(10, datetime.datetime.today(), "Hello world", None)
        profile.save()

        self.assertEqual(PointsTransaction.objects.count(), log_count + 1,
                         "A new log should have been created.")
        log = profile.user.pointstransaction_set.all()[0]
        self.assertEqual(log.points, 10, "Points should have been awarded.")
        self.assertEqual(log.message, "Hello world",
                         "Message should have been added.")
