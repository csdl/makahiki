"""Test for possible quest conditions."""

import datetime
# import os

from django.test import TransactionTestCase
from django.contrib.auth.models import User
# from django.conf import settings
# from django.core.files.images import ImageFile
# from django.db.models import signals
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.predicates import badge_awarded, has_points, \
    posted_to_wall
from apps.managers.team_mgr.models import Group, Team, Post
from apps.utils import test_utils
from apps.widgets.badges import badges

from apps.widgets.quests.quests import possibly_completed_quests, get_quests
from apps.widgets.smartgrid.models import Activity, ActionMember, Commitment, ColumnName, Level, \
    ColumnGrid, Grid
# from apps.lib.avatar import create_default_thumbnails
# from apps.lib.avatar.models import Avatar, avatar_file_path
from apps.widgets.raffle.models import RafflePrize, RaffleTicket
from apps.widgets.smartgrid.predicates import submitted_action, \
    approved_action, approved_some_of_type, approved_some, submitted_some_of_type
from apps.managers.challenge_mgr.models import RoundSetting


class QuestConditionsTest(TransactionTestCase):
    """
    Tests for the possible quest conditions.
    """
    fixtures = ["base_badges.json"]

    def setUp(self):
        challenge_mgr.init()
        self.user = User(username="testuser", password="password")
        self.user.save()

        self.quest = test_utils.create_quest(completion_conditions=False)
        test_utils.set_competition_round()

    def testAllocatedTicket(self):
        """
        Test that allocated_ticket works.
        """
        # Create a raffle prize.
        r = RoundSetting.objects.get(name="Round 1")
        prize = RafflePrize(
            title="Super prize!",
            description="A test prize",
            round=r,
            value=5,
        )
        prize.save()

        # Test within context of a quest
        self.quest.unlock_conditions = "allocated_raffle_ticket()"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests["available_quests"],
            "User should not be able to participate in this quest.")

        self.quest.unlock_conditions = "not allocated_raffle_ticket()"
        self.quest.completion_conditions = "allocated_raffle_ticket()"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")
        self.quest.accept(self.user)

        # Add a raffle ticket and test that the user completed the quest.
        ticket = RaffleTicket(raffle_prize=prize, user=self.user)
        ticket.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")

    def testNumTasksCompleted(self):
        """Test that completing an activity works with approved_some_of and has_action."""
        # put the grid together. First the ColumnName
        level = Level(name="Test level", slug="test-level")
        level.save()
        column = ColumnName(name="Test column", slug="test-column")
        column.save()
        c_grid = ColumnGrid(level=level, column=1, name=column)
        c_grid.save()
        # Then the activity
        activity = Activity(
            type="activity",
            name="Test",
            slug="test",
            title="Test activity",
            description="Variable points!",
            expected_duration=10,
            point_value=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
        )
        activity.save()
        grid = Grid(level=level, column=1, row=1, action=activity)
        grid.save()

        # Test activities
        member = ActionMember(user=self.user, action=activity, approval_status="pending")
        member.save()
        self.assertFalse(approved_some_of_type(self.user, action_type='activity', count=1),
            "User with pending activity should not have completed a task.")
        self.assertFalse(approved_some(self.user, count=1),
            "User with pending activity should not have completed a task.")

        # Test within context of a quest
        self.quest.unlock_conditions = "approved_some_of_type(action_type='activity', count=1)"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests,
            "User should not be able to participate in this quest.")

        self.quest.unlock_conditions = "approved_some(count=1)"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests,
            "User should not be able to participate in this quest.")

        # Check that the user can now add the quest.
        member.approval_status = "approved"
        member.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.unlock_conditions = "approved_some_of_type(action_type='activity', count=1)"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should not be able to participate in this quest.")

        # Test as a completion condition.
        self.quest.accept(self.user)
        self.quest.completion_conditions = "approved_some_of_type(action_type='activity', count=2)"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "approved_some(count=2)"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "approved_some_of_type(action_type='activity', count=1)"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")

    def testNumTasksCompletedWithType(self):
        """test task completed."""
        activity = Activity(
            type="activity",
            name="Test",
            slug="test",
            title="Test activity",
            description="Variable points!",
            expected_duration=10,
            point_value=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
        )
        activity.save()

        # Test activities
        member = ActionMember(user=self.user, action=activity, approval_status="pending")
        member.save()
        self.assertFalse(approved_some_of_type(self.user, action_type="activity", count=1),
            "User with pending activity should not have completed a task.")

        # Test within context of a quest
        self.quest.unlock_conditions = "approved_some_of_type(action_type='activity', count=1)"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests,
            "User should not be able to participate in this quest.")

        # Check that the user can now add the quest.
        member.approval_status = "approved"
        member.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        # Test as a completion condition.
        self.quest.accept(self.user)
        self.quest.completion_conditions = "approved_some_of_type(action_type='activity', count=2)"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "approved_some_of_type(action_type='activity', count=1)"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")

    def testHasActivity(self):
        """Test that completing an activity works with has_action."""
        activity = Activity(
            type="activity",
            name="Test",
            slug="test-activity",
            title="Test activity",
            description="Variable points!",
            expected_duration=10,
            point_value=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
        )
        activity.save()

        # Test within context of a quest
        self.quest.unlock_conditions = "submitted_action(action_slug='test-activity')"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests,
            "User should not be able to participate in this quest.")

        member = ActionMember(user=self.user, action=activity, approval_status="pending")
        member.save()
        self.assertTrue(submitted_action(self.user, action_slug="test-activity"),
            "User should have a pending task.")
        self.assertTrue(submitted_some_of_type(self.user, action_type="activity"),
            "User should have a pending task.")

        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.unlock_conditions = "submitted_some_of_type(action_type='activity')"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        member.approval_status = "approved"
        member.save()
        self.assertTrue(submitted_action(self.user, action_slug='test-activity'),
            "User should have a completed task.")
        self.assertTrue(submitted_some_of_type(self.user, action_type="activity"),
            "User should have a completed task.")

        # Test as a completion condition.
        self.quest.accept(self.user)
        self.quest.completion_conditions = "not submitted_action(action_slug='test-activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "not submitted_some_of_type(action_type='activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "submitted_action(action_slug='test-activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")

    def testCompletedActivity(self):
        """Tests that approved_action works when a task is completed."""
        activity = Activity(
            type="activity",
            name="Test",
            title="Test activity",
            slug="test-activity",
            description="Variable points!",
            expected_duration=10,
            point_value=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
        )
        activity.save()

        # Test within context of a quest
        self.quest.unlock_conditions = "approved_action(action_slug='test-activity')"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest not in quests,
            "User should not be able to participate in this quest.")

        member = ActionMember(user=self.user, action=activity, approval_status="approved")
        member.save()
        self.assertTrue(approved_action(self.user, action_slug="test-activity"),
            "User should have completed 'Test'.")
        self.assertTrue(approved_some_of_type(self.user, action_type="activity"),
            "User should have completed an activity")

        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.unlock_conditions = "approved_some_of_type(action_type='activity')"
        self.quest.save()
        quests = get_quests(self.user)
        self.assertTrue(self.quest in quests["available_quests"],
            "User should be able to participate in this quest.")

        # Test as a completion condition.
        self.quest.accept(self.user)
        self.quest.completion_conditions = "not approved_action(action_slug='test-activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "not approved_some_of_type(action_type='activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest not in completed_quests,
            "User should not be able to complete the quest.")

        self.quest.completion_conditions = "approved_action(action_slug='test-activity')"
        self.quest.save()
        completed_quests = possibly_completed_quests(self.user)
        self.assertTrue(self.quest in completed_quests, "User should have completed the quest.")

    def testCommitmentsNumCompleted(self):
        """Tests that approved_some_of works for a completed commitment."""
        commitment = Commitment(
            title="Test commitment",
            type="commitment",
            slug="test",
            name="Test",
            description="A commitment!",
            point_value=10,
        )
        commitment.save()

        member = ActionMember(user=self.user, action=commitment)
        member.save()
        self.assertFalse(approved_some(self.user, count=1),
            "User with commitment in progress should not have completed a task.")

        # Test as an unlock condition
        self.quest.unlock_conditions = "approved_some(count=1)"
        self.quest.save()
        self.assertTrue(self.quest not in get_quests(self.user),
            "User should not be able to participate in this quest.")

        member.award_date = datetime.datetime.today()
        member.approval_status = "approved"
        member.save()
        self.assertTrue(approved_some(self.user, count=1),
            "User that has a completed commitment did not complete a task.")
        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")

        # Test as a completion condition
        self.quest.accept(self.user)
        self.quest.completion_conditions = "approved_some(count=2)"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        self.quest.completion_conditions = "approved_some(count=1)"
        self.quest.save()
        self.assertTrue(self.quest in possibly_completed_quests(self.user),
            "User should be able to complete this quest.")

    def testHasCommitment(self):
        """Tests that has_action works for a commitment in progress."""
        commitment = Commitment(
            title="Test commitment",
            type="commitment",
            name="Test",
            slug="test-commitment",
            description="A commitment!",
            point_value=10,
        )
        commitment.save()

        # Test as an unlock condition.
        self.quest.unlock_conditions = "submitted_action(action_slug='test-commitment')"
        self.quest.save()
        self.assertTrue(self.quest not in get_quests(self.user),
            "User should not be able to participate in this quest.")

        member = ActionMember(user=self.user, action=commitment)
        member.save()
        self.assertTrue(submitted_action(self.user, action_slug='test-commitment'),
            "User should have a commitment in progress.")
        self.assertTrue(submitted_some_of_type(self.user, action_type="commitment"),
            "User should have a commitment in progress.")

        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")
        self.quest.unlock_conditions = "submitted_some_of_type(action_type='commitment')"
        self.quest.save()
        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")

        member.award_date = datetime.datetime.today()
        member.save()
        self.assertTrue(submitted_action(self.user, action_slug='test-commitment'),
            "User should have a completed commitment.")
        self.assertTrue(submitted_some_of_type(self.user, action_type="commitment"),
            "User should have a completed commitment.")

        # Test as a completion condition
        self.quest.accept(self.user)
        self.quest.completion_conditions = "not submitted_action(action_slug='test-commitment')"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        self.quest.completion_conditions = "not submitted_some_of_type(action_type='commitment')"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        self.quest.completion_conditions = "submitted_action(action_slug='test-commitment')"
        self.quest.save()
        self.assertTrue(self.quest in possibly_completed_quests(self.user),
            "User should be able to complete this quest.")

    def testBadgeAwarded(self):
        """Tests that badge awarded works for a user."""
        profile = self.user.profile
        self.assertFalse(badge_awarded(self.user, "daily-visitor"),
            "New user should not be awarded the daily visitor badge.")

        # Test as a quest unlock condition.
        self.quest.unlock_conditions = "badge_awarded('daily-visitor')"
        self.quest.save()
        self.assertTrue(self.quest not in get_quests(self.user),
            "User should not be able to participate in this quest.")

        self.quest.unlock_conditions = "not badge_awarded('three-peater')"
        self.quest.save()
        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.accept(self.user)
        self.quest.completion_conditions = "badge_awarded('three-peater')"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        profile.daily_visit_count = 3
        profile.save()
        badge = badges.get_badge("three-peater")
        badges.award_badge(profile=profile, badge=badge)
        self.assertTrue(badge_awarded(self.user, "three-peater"),
            "User should have been awarded the three-peater badge.")
        self.assertTrue(self.quest in possibly_completed_quests(self.user),
            "User should have completed this quest.")

    def testHasPointsOverall(self):
        """Tests that has_points works for a user."""
        profile = self.user.profile
        test_points = 10
        self.assertFalse(has_points(self.user, test_points), "User should not have any points")
        profile.add_points(test_points, datetime.datetime.today(), "test quest")
        self.assertTrue(has_points(self.user, test_points), "User should have enough points.")

        # Test within context of a quest.
        profile.remove_points(test_points, datetime.datetime.today(), "test quest")
        self.quest.unlock_conditions = "has_points(10)"
        self.quest.save()
        self.assertTrue(self.quest not in get_quests(self.user),
            "User should not be able to participate in this quest.")

        self.quest.unlock_conditions = "not has_points(10)"
        self.quest.save()
        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.accept(self.user)
        self.quest.completion_conditions = "has_points(10)"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        profile.add_points(test_points, datetime.datetime.today(), "test quest")
        self.assertTrue(self.quest in possibly_completed_quests(self.user),
            "User should have completed this quest.")

    def testPostedToWall(self):
        """
        Tests that this predicate is completed when the user posts something to their wall.
        """
        group = Group.objects.create(name="test")
        team = Team.objects.create(name="a", group=group)
        profile = self.user.profile
        profile.team = team
        profile.save()

        self.assertFalse(posted_to_wall(self.user), "User should not have posted to their wall.")
        post = Post.objects.create(user=self.user, team=team, text="text")
        self.assertTrue(posted_to_wall(self.user), "User should have posted to their own wall.")

        # Test within context of a quest.
        post.delete()
        self.quest.unlock_conditions = "posted_to_wall()"
        self.quest.save()
        self.assertTrue(self.quest not in get_quests(self.user),
            "User should not be able to participate in this quest.")

        self.quest.unlock_conditions = "not posted_to_wall()"
        self.quest.save()
        self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
            "User should be able to participate in this quest.")

        self.quest.accept(self.user)
        self.quest.completion_conditions = "posted_to_wall()"
        self.quest.save()
        self.assertTrue(self.quest not in possibly_completed_quests(self.user),
            "User should not be able to complete this quest.")

        post = Post.objects.create(user=self.user, team=team, text="text")
        self.assertTrue(self.quest in possibly_completed_quests(self.user),
            "User should have completed this quest.")

#     def testSetProfilePic(self):
#         """
#         Tests that this predicate is completed when the user sets a profile pic.
#         """
#         # Need to disconnect create thumbnail signal temporarily for test so that additional image
#         # files don't get created.
#         signals.post_save.disconnect(create_default_thumbnails, Avatar)
#
#         self.assertFalse(set_profile_pic(self.user), "User should not have their "
#profile pic set.")
#         image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
#         image = ImageFile(open(image_path, "r"))
#         path = avatar_file_path(user=self.user, filename="test.jpg")
#         avatar = Avatar(user=self.user, avatar=path, primary=True)
#         avatar.avatar.storage.save(path, image)
#         avatar.save()
#         self.assertTrue(set_profile_pic(self.user), "User should have their profile pic set.")
#
#         # Test within context of a quest.
#         avatar.delete()
#         self.quest.unlock_conditions = "set_profile_pic()"
#         self.quest.save()
#         self.assertTrue(self.quest not in get_quests(self.user),
#             "User should not be able to participate in this quest.")
#
#         self.quest.unlock_conditions = "not set_profile_pic()"
#         self.quest.save()
#         self.assertTrue(self.quest in get_quests(self.user)["available_quests"],
#             "User should be able to participate in this quest.")
#
#         self.quest.accept(self.user)
#         self.quest.completion_conditions = "set_profile_pic()"
#         self.quest.save()
#         self.assertTrue(self.quest not in possibly_completed_quests(self.user),
#             "User should not be able to complete this quest.")
#
#         avatar = Avatar(user=self.user, avatar=path, primary=True)
#         avatar.save()
#         self.assertTrue(self.quest in possibly_completed_quests(self.user),
#             "User should have completed this quest.")
#
#         # Be sure to clean up test files and reconnect post_save signal.
#         signals.post_save.connect(create_default_thumbnails, sender=Avatar)
#         for avatar in self.user.avatar_set.all():
#             avatar.avatar.delete()
#             avatar.delete()
