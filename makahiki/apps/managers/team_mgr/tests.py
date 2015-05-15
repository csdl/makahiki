"""Tests for team_manager."""


import datetime

from django.test import TransactionTestCase
from django.contrib.auth.models import User
from apps.managers.team_mgr import team_mgr

from apps.managers.team_mgr.models import Group, Team
from apps.utils import test_utils


class DormUnitTestCase(TransactionTestCase):
    """dorm test"""

    def setUp(self):
        self.groups = [Group(name="Test Group %d" % i) for i in range(0, 2)]
        _ = [d.save() for d in self.groups]

        self.teams = [Team(name=str(i), group=self.groups[i % 2]) for i in
                       range(0, 4)]
        _ = [f.save() for f in self.teams]

        self.users = [User.objects.create_user("test%d" % i, "test@test.com")
                      for i in range(0, 4)]

        # Assign users to teams.
        for index, user in enumerate(self.users):
            user.profile.team = self.teams[index % 4]
            user.profile.save()

        self.current_round = "Round 1"
        test_utils.set_competition_round()

    def testTeamPointsInRound(self):
        """Tests calculating the team points leaders in a round."""
        profile = self.users[0].profile
        profile.add_points(10,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
        profile.save()

        self.assertEqual(self.groups[0].team_points_leaders(round_name=self.current_round)[0],
                         profile.team,
                         "The user's team is not leading in the prize.")

        # Test that a user in a different team but same dorm changes the
        # leader for the original user.
        profile2 = self.users[2].profile
        profile2.add_points(profile.points() + 1,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
        profile2.save()

        self.assertEqual(self.groups[0].team_points_leaders(round_name=self.current_round)[0],
                         profile2.team,
                         "The user's team should have changed.")

        # Test that adding points to a user in a different dorm does not
        # change affect these standings.
        profile1 = self.users[1].profile
        profile1.add_points(profile.points() + 1,
                            datetime.datetime.today() -\
                            datetime.timedelta(minutes=1),
                            "test")
        profile1.save()

        self.assertEqual(self.groups[0].team_points_leaders(round_name=self.current_round)[0],
                         profile2.team,
                         "The leader of the team should not change.")
        self.assertEqual(self.groups[1].team_points_leaders(round_name=self.current_round)[0],
                         profile1.team,
                         "The leader in the second dorm should be profile1's "
                         "team.")

        # Test that a tie is handled properly.
        profile.add_points(1, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(self.groups[0].team_points_leaders(round_name=self.current_round)[0],
                         profile.team,
                         "The leader of the team should have changed back.")

    def testTeamPointsOverall(self):
        """Tests calculating the team points leaders in a round."""
        profile = self.users[0].profile
        profile.add_points(10,
                           datetime.datetime.today() -\
                           datetime.timedelta(minutes=1),
                           "test")
        profile.save()

        self.assertEqual(self.groups[0].team_points_leaders()[0],
                         profile.team,
                         "The user's team is not leading in the prize.")

        # Test that a user in a different team but same dorm changes the
        # leader for the original user.
        profile2 = self.users[2].profile
        profile2.add_points(profile.points() + 1,
                            datetime.datetime.today() -\
                            datetime.timedelta(minutes=1),
                            "test")
        profile2.save()

        self.assertEqual(self.groups[0].team_points_leaders()[0],
                         profile2.team,
                         "The user's team should have changed.")

        # Test that a tie between two different teams is handled properly.
        profile.add_points(1, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(profile.points(), profile2.points(),
            "The two profiles should have identical points.")
        self.assertEqual(self.groups[0].team_points_leaders()[0],
                         profile.team,
                         "The leader of the team should have changed back.")

        # Test that adding points to a user in a different dorm does not
        # change affect these standings.
        profile1 = self.users[1].profile
        profile1.add_points(profile.points() + 1,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile1.save()

        self.assertEqual(self.groups[0].team_points_leaders()[0],
                         profile.team,
                         "The leader of the team should not change.")
        self.assertEqual(self.groups[1].team_points_leaders()[0],
                         profile1.team,
                         "The leader in the second dorm should be profile1's "
                         "team.")


class TeamLeadersTestCase(TransactionTestCase):
    """test team leader"""
    def setUp(self):
        self.group = Group(name="Test Group")
        self.group.save()

        self.teams = [Team(name=str(i), group=self.group) for i in
                       range(0, 2)]
        _ = [f.save() for f in self.teams]

        self.users = [User.objects.create_user("test%d" % i, "test@test.com")
                      for i in range(0, 4)]

        # Assign users to teams.
        for index, user in enumerate(self.users):
            user.profile.team = self.teams[index % 2]
            user.profile.save()

        self.current_round = "Round 1"
        test_utils.set_competition_round()

    def testTeamPointsInRound(self):
        """Tests calculating the team points leaders in a round."""
        profile = self.users[0].profile
        profile.add_points(10,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "test")
        profile.save()

        self.assertEqual(team_mgr.team_points_leader(round_name=self.current_round),
                         profile.team,
                         "The user's team is not leading in the prize.")

        # Test that a user in a different team but same dorm changes the
        # leader for the original user.
        profile2 = self.users[2].profile
        profile2.add_points(profile.points() + 1,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile2.save()

        self.assertEqual(team_mgr.team_points_leader(round_name=self.current_round),
                         profile2.team,
                         "The user's team should have changed.")

        # Test that a tie is handled properly.
        profile.add_points(1, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(team_mgr.team_points_leader(round_name=self.current_round),
                         profile.team,
                         "The leader of the team should have changed back.")

    def testIndividualPointsInRound(self):
        """Tests calculating the individual points leaders in a round."""
        profile = self.users[0].profile
        profile.add_points(10,
                           datetime.datetime.today() -
                           datetime.timedelta(minutes=1),
                           "test")
        profile.save()

        self.assertEqual(profile.team.points_leaders(round_name=self.current_round)[0],
                         profile,
                         "The user should be in the lead in his own team.")

        # Test that a user in a different team but same dorm does not change
        # the leader for the original team.
        profile1 = self.users[1].profile
        profile1.add_points(15,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile1.save()

        self.assertEqual(profile.team.points_leaders(round_name=self.current_round)[0],
                         profile,
                         "The leader for the user's team should not have"
                         " changed.")
        self.assertEqual(profile1.team.points_leaders(round_name=self.current_round)[0],
                         profile1,
                         "User 1 should be leading in their own team.")

        # Test another user going ahead in the user's team.
        profile2 = self.users[2].profile
        profile2.add_points(15,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile2.save()

        self.assertEqual(profile.team.points_leaders(round_name=self.current_round)[0],
                         profile2,
                         "User 2 should be in the lead in the user's team.")

        # Test that a tie is handled properly.
        profile.add_points(5, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(profile.team.points_leaders(round_name=self.current_round)[0],
                         profile,
                         "The leader of the team should have changed back.")

    def testTeamPointsOverall(self):
        """Tests calculating the team points leaders in a round."""
        profile = self.users[0].profile
        profile.add_points(10,
                           datetime.datetime.today() -
                           datetime.timedelta(minutes=1),
                           "test")
        profile.save()

        self.assertEqual(profile.team.points_leaders()[0],
                         profile,
                         "The user should be in the lead in his own team.")

        # Test that a user in a different team but same dorm does not change
        # the leader for the original team.
        profile1 = self.users[1].profile
        profile1.add_points(15,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile1.save()

        self.assertEqual(profile.team.points_leaders()[0],
                         profile,
                         "The leader for the user's team should not have "
                         "changed.")
        self.assertEqual(profile1.team.points_leaders()[0],
                         profile1,
                         "User 1 should be leading in their own team.")

        # Test another user going ahead in the user's team.
        profile2 = self.users[2].profile
        profile2.add_points(15,
                            datetime.datetime.today() -
                            datetime.timedelta(minutes=1),
                            "test")
        profile2.save()

        self.assertEqual(profile.team.points_leaders()[0],
                         profile2,
                         "User 2 should be in the lead in the user's team.")

        # Test that a tie is handled properly.
        profile.add_points(5, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(profile.team.points_leaders()[0],
                         profile,
                         "The leader of the team should have changed back.")


class TeamsUnitTestCase(TransactionTestCase):
    """team tests"""
    def setUp(self):
        self.group = Group(name="Test group")
        self.group.save()
        self.test_team = Team(name="A", group=self.group)
        self.test_team.save()

    def testOverallPoints(self):
        """Check that retrieving the points for the team is correct."""
        # Create a test user.
        user = User(username="test_user", password="test_password")
        user.save()
        user_points = 10
        user.profile.team = self.test_team

        self.assertEqual(self.test_team.points(),
                         0,
                         "Check that the team does not have any points yet.")

        user.profile.add_points(user_points, datetime.datetime.today(),
            "test")
        user.profile.save()

        self.assertEqual(self.test_team.points(),
                         user_points,
                         "Check that the number of points are equal for "
                         "one user.")

        # Create another test user and check again.
        user = User(username="test_user1", password="test_password")
        user.save()
        user.profile.team = self.test_team
        user.profile.add_points(user_points,
                                      datetime.datetime.today(),
                                      "test")
        user.profile.save()

        self.assertEqual(self.test_team.points(), 2 * user_points,
            "Check that the number of points are equal for two users.")

    def testPointsInRound(self):
        """Tests that we can accurately compute the amount of points in a
        round."""
        test_utils.set_competition_round()

        user = User(username="test_user", password="test_password")
        user.save()
        profile = user.profile
        profile.team = self.test_team
        profile.save()

        self.assertEqual(self.test_team.current_round_points(),
                         0,
                         "Check that the team does not have any points yet.")

        profile.add_points(10, datetime.datetime.today(), "test")
        profile.save()

        self.assertEqual(self.test_team.current_round_points(),
                         10,
                         "Check that the number of points are correct in "
                         "this round.")

    def testOverallRankWithPoints(self):
        """Check that calculating the rank is correct based on point value."""
        # Create a test user.
        user = User(username="test_user", password="test_password")
        user.save()
        user_points = 10
        user.profile.team = self.test_team

        # Test the team is ranked last if they haven't done anything yet.
        team_rank = 1
        self.assertEqual(self.test_team.rank(), team_rank,
            "Check the team is ranked last.")

        user.profile.add_points(user_points,
                                      datetime.datetime.today(),
                                      "test")
        user.profile.save()

        self.assertEqual(self.test_team.rank(),
                         1,
                         "Check the team is now ranked number 1.")

        # Create a test user on a different team.
        test_team2 = Team(name="B", group=self.group)
        test_team2.save()

        user2 = User(username="test_user1", password="test_password")
        user2.save()
        user2.profile.team = test_team2
        user2.profile.add_points(user_points + 1,
                                       datetime.datetime.today(),
                                       "test")
        user2.profile.save()

        self.assertEqual(self.test_team.rank(),
                         2,
                         "Check that the team is now ranked number 2.")

    def testRoundRank(self):
        """Check that the rank calculation is correct for the current round."""
        # Save the round information and set up a test round.
        test_utils.set_competition_round()

        # Create a test user.
        user = User(username="test_user", password="test_password")
        user.save()
        user_points = 10
        user.profile.team = self.test_team
        user.profile.save()

        self.assertEqual(self.test_team.current_round_rank(),
                         1,
                         "Check the calculation works even if there's "
                         "no submission.")

        user.profile.add_points(user_points,
                                      datetime.datetime.today(),
                                      "test")
        user.profile.save()
        self.assertEqual(self.test_team.current_round_rank(),
                         1,
                         "Check the team is now ranked number 1.")

        test_team2 = Team(name="B", group=self.group)
        test_team2.save()

        user2 = User(username="test_user1", password="test_password")
        user2.save()
        user2.profile.team = test_team2
        user2.profile.add_points(user_points + 1,
                                       datetime.datetime.today(),
                                       "test")
        user2.profile.save()

        self.assertEqual(self.test_team.current_round_rank(),
                         2,
                         "Check the team is now ranked number 2.")

    def testOverallRankWithSubmissionDate(self):
        """Check that rank calculation is correct in the case of ties."""
        # Create a test user.
        user = User(username="test_user", password="test_password")
        user.save()
        user_points = 10
        user.profile.team = self.test_team
        user.profile.add_points(user_points,
                                      datetime.datetime.today(),
                                      "test")
        user.profile.save()

        # Create a test user on a different team.
        test_team2 = Team(name="B", group=self.group)
        test_team2.save()

        user = User(username="test_user1", password="test_password")
        user.save()
        user.profile.team = test_team2
        user.profile.add_points(user_points,
                                      datetime.datetime.today() + datetime.timedelta(days=1),
                                      "test")
        user.profile.save()

        self.assertEqual(self.test_team.rank(),
                         2,
                         "Check that the team is ranked second.")
