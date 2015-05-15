"""
profile tests
"""

import datetime

from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from apps.managers.player_mgr import player_mgr

from apps.managers.team_mgr.models import Group, Team
from apps.managers.player_mgr.models import Profile
from apps.utils import test_utils


class ProfileLeadersTests(TransactionTestCase):
    """profile leader tests"""
    def setUp(self):
        """
        test case setup
        """
        self.users = [User.objects.create_user("test%d" % i, "test@test.com")
                      for i in range(0, 3)]

        self.current_round = "Round 1"
        test_utils.set_competition_round()

    def testLeadersInRound(self):
        """
        Test that we can retrieve the leaders in a given round.
        """
        # Test one user
        profile = self.users[0].profile
        profile.add_points(10,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
        profile.save()

        self.assertEqual(
            player_mgr.points_leader(round_name=self.current_round), profile,
            "Current leader is not the leading user.")

        # Have another user move ahead in points
        profile2 = self.users[1].profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.save()

        self.assertEqual(
            player_mgr.points_leader(round_name=self.current_round), profile2,
            "User 2 should be the leading profile.")

        # Have this user get the same amount of points,
        # but an earlier award date.
        profile3 = self.users[2].profile
        profile3.add_points(profile2.points(),
            datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
        profile3.save()

        self.assertEqual(
            player_mgr.points_leader(round_name=self.current_round), profile2,
            "User 2 should still be the leading profile.")

    def testLeadersOverall(self):
        """
        Test that we can retrieve the leaders in a given round.
        """
        # Test one user
        profile = self.users[0].profile
        profile.add_points(10,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
        profile.save()

        self.assertEqual(player_mgr.points_leader(), profile,
            "Current leader is not the leading user.")

        # Have another user move ahead in points
        profile2 = self.users[1].profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.save()

        self.assertEqual(player_mgr.points_leader(), profile2,
            "User 2 should be the leading profile.")

        # Have this user get the same amount of points,
        # but an earlier award date.
        profile3 = self.users[2].profile
        profile3.add_points(profile2.points(),
            datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
        profile3.save()

        self.assertEqual(player_mgr.points_leader(), profile2,
            "User 2 should still be the leading profile.")


class ProfileUnitTests(TransactionTestCase):
    """profile unit test"""
    def setUp(self):
        """
        test case setup
        """
        test_utils.set_competition_round()

    def testDisplayNameUnique(self):
        """
        test displayname uniqueness.
        """
        user1 = User(username="test_user", password="changeme")
        user1.save()
        user2 = User(username="test_user1", password="changeme")
        user2.save()

        profile1 = user1.profile
        profile1.name = "Test User"
        profile1.save()

        profile2 = user2.profile
        profile2.name = "Test User"
        self.assertRaises(IntegrityError, profile2.save)

    def testReferralBonus(self):
        """
        Test that the referral bonus is awarded once the referred user
        reaches 30 points.
        """
        user1 = User.objects.create_user("test_user", 'user@test.com',
            password="changeme")
        user1.save()
        user2 = User.objects.create_user('test_user2', 'user2@test.com',
            password="changeme")
        user2.save()

        test_utils.enable_game("Referral Game Mechanics")

        profile1 = user1.profile
        profile1.setup_profile = True
        profile1.setup_complete = True
        points1 = profile1.points()
        profile1.save()

        profile2 = user2.profile
        profile2.setup_profile = True
        profile2.setup_complete = True
        profile2.referring_user = user1
        profile2.add_points(10, datetime.datetime.today(), 'test 1')
        profile2.save()

        self.assertEqual(points1, Profile.objects.get(user=user1).points(),
            'User 1 should not have received any points.')

        points2 = profile2.points()
        profile2.add_points(40, datetime.datetime.today(),
            'Trigger referral bonus.')
        profile2.save()

        self.assertEqual(points1 + 10, Profile.objects.get(user=user1).points(),
            'User 1 should have the referral bonus')
        self.assertEqual(points2 + 50, Profile.objects.get(user=user2).points(),
            'User 2 should have the referral bonus')
        self.assertTrue(Profile.objects.get(user=user2).referrer_awarded,
            'User 2 should have the referral awarded.')

        profile2.add_points(20, datetime.datetime.today(), 'Post test')
        profile2.save()

        self.assertEqual(points1 + 10, Profile.objects.get(user=user1).points(),
            'User 1 should not be given the referral bonus again.')

    def testReferralLoop(self):
        """test referral loop"""
        user1 = User.objects.create_user("test_user", 'user@test.com',
            password="changeme")
        user1.save()
        user2 = User.objects.create_user('test_user2', 'user2@test.com',
            password="changeme")
        user2.save()

        test_utils.enable_game("Referral Game Mechanics")

        profile1 = user1.profile
        profile1.setup_profile = True
        profile1.setup_complete = True
        profile1.referring_user = user2
        profile1.add_points(45, datetime.datetime.today(), 'test 1')
        profile1.save()

        profile2 = user2.profile
        profile2.setup_profile = True
        profile2.setup_complete = True
        profile2.referring_user = user1
        profile2.add_points(45, datetime.datetime.today(), 'test 1')
        profile2.save()

        profile1.add_points(10, datetime.datetime.today(), 'test 1')
        profile1.save()

        #for log in user2.pointstransaction_set.all():
        #    print "%d %s" % (log.points, log.message)

        self.assertEqual(Profile.objects.get(user=user1).points(), 65)
        self.assertEqual(Profile.objects.get(user=user2).points(), 55)

    def testTeamRankWithPoints(self):
        """Tests that the team_rank method accurately computes the rank based
         on points."""
        user = User(username="test_user", password="changeme")
        user.save()
        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        profile = user.profile
        profile.team = team

        # Check that the user is ranked last if they haven't done anything.
        rank = 1
        self.assertEqual(profile.team_rank(), rank,
            "Check that the user is ranked last.")

        # Make the user number 1 overall.
        top_user = Profile.objects.all()[0]
        profile.add_points(top_user.points() + 1, datetime.datetime.today(),
            "Test")
        profile.save()

        self.assertEqual(profile.team_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.save()

        self.assertEqual(profile.team_rank(), 1,
                         "Check that the user is still number 1 if the new "
                         "profile is not on the same team.")

        profile2.team = team
        profile2.save()

        self.assertEqual(profile.team_rank(), 2,
            "Check that the user is now rank 2.")

    def testTeamRankWithSubmissionDate(self):
        """Tests that the team_rank method accurately computes the rank when
        users have the same number of points,"""
        user = User(username="test_user", password="changeme")
        user.save()
        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        profile = user.profile
        profile.team = team
        top_user = player_mgr.points_leader()
        profile.add_points(top_user.points() + 1,
            datetime.datetime.today() - datetime.timedelta(minutes=1), "Test")
        profile.save()

        self.assertEqual(profile.team_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points(), datetime.datetime.today(), "Test")
        profile2.save()

        profile2.team = team
        profile2.save()

        self.assertEqual(profile.team_rank(), 2,
            "Check that the user is now rank 2.")

    def testOverallRankWithPoints(self):
        """Tests that the rank method accurately computes the rank with
        points."""
        user = User(username="test_user", password="changeme")
        user.save()
        profile = user.profile

        # Check if the rank works if the user has done nothing.
        rank = 1
        self.assertEqual(profile.overall_rank(), rank,
            "Check that the user is at least tied for last.")

        # Make the user ranked 1st.
        top_user = Profile.objects.all()[0]
        profile.add_points(top_user.points() + 1, datetime.datetime.today(),
            "Test")
        profile.save()

        self.assertEqual(profile.overall_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.save()

        self.assertEqual(profile.overall_rank(), 2,
            "Check that the user is now rank 2.")

    def testOverallRankWithSubmissionDate(self):
        """Tests that the overall_rank method accurately computes the rank
        when two users have the same number of points."""
        user = User(username="test_user", password="changeme")
        user.save()

        profile = user.profile
        top_user = Profile.objects.all()[0]
        profile.add_points(top_user.points() + 1,
            datetime.datetime.today() - datetime.timedelta(days=1), "Test")
        profile.save()

        self.assertEqual(profile.overall_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points(), datetime.datetime.today(), "Test")
        profile2.save()

        self.assertEqual(profile.overall_rank(), 2,
            "Check that the user is now rank 2.")

    def testOverallRankForCurrentRound(self):
        """Test that we can retrieve the rank for the user in the current
        round."""
        test_utils.set_competition_round()

        user = User(username="test_user", password="changeme")
        user.save()

        profile = user.profile
        top_user = player_mgr.points_leader()
        profile.add_points(top_user.points() + 1, datetime.datetime.today(),
            "Test")
        profile.save()

        self.assertEqual(profile.current_round_overall_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.save()

        self.assertEqual(profile.current_round_overall_rank(), 2,
            "Check that the user is now number 2.")

    def testTeamRankForCurrentRound(self):
        """Test that we can retrieve the rank for the user in the current
        round."""
        test_utils.set_competition_round()

        group = Group(name="Test group")
        group.save()
        team = Team(name="A", group=group)
        team.save()

        user = User(username="test_user", password="changeme")
        user.save()

        profile = user.profile
        top_user = Profile.objects.all()[0]
        profile.add_points(top_user.points() + 1, datetime.datetime.today(),
            "Test")
        profile.team = team
        profile.save()

        self.assertEqual(profile.current_round_team_rank(), 1,
            "Check that the user is number 1.")

        user2 = User(username="test_user2", password="changeme")
        user2.save()

        profile2 = user2.profile
        profile2.add_points(profile.points() + 1, datetime.datetime.today(),
            "Test")
        profile2.team = team
        profile2.save()

        self.assertEqual(profile.current_round_team_rank(), 2,
            "Check that the user is now number 2.")

    def testCurrentRoundPoints(self):
        """Tests that we can retrieve the points for the user in the current
        round."""
        test_utils.set_competition_round()

        user = User(username="test_user", password="changeme")
        user.save()

        profile = user.profile
        points = profile.points()
        profile.add_points(10, datetime.datetime.today(), "Test")
        profile.save()

        self.assertEqual(profile.current_round_points(), points + 10,
            "Check that the user has 10 more points in the current round.")
