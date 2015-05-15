"""Profile page test"""
import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from apps.managers.challenge_mgr import challenge_mgr

from apps.utils import test_utils
from apps.widgets.smartgrid.models import Activity, ActionMember, Commitment, Event
from apps.widgets.quests.models import Quest


class MyAchievementsTestCase(TransactionTestCase):
    """Profile page test"""

    def setUp(self):
        """setup"""
        challenge_mgr.init()
        self.user = test_utils.setup_user(username="user", password="changeme")
        test_utils.set_competition_round()

        test_utils.enable_quest()
        challenge_mgr.register_page_widget("home", "home")
        challenge_mgr.register_page_widget("profile", "my_achievements")
        challenge_mgr.register_page_widget("profile", "my_commitments")

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()

        self.client.login(username="user", password="changeme")

    def testActivityAchievement(self):
        """Check that the user's activity achievements are loaded."""
        activity = Activity(
            title="Test activity",
            description="Testing!",
            expected_duration=10,
            point_value=10,
            slug="test-activity",
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
            type="activity",
        )
        activity.save()

        # Test that profile page has a pending activity.
        member = ActionMember(user=self.user,
                              action=activity,
                              approval_status="approved")
        member.save()

        response = self.client.get(reverse("profile_index"))
        self.assertContains(response,
            reverse("activity_task", args=(activity.type, activity.slug,)))
        self.assertContains(response, "Test activity")

        # Test adding an event to catch a bug.
        event = Event(
            title="Test event",
            slug="test-event",
            description="Testing!",
            expected_duration=10,
            point_value=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            type="event",
            event_date=datetime.datetime.today() + datetime.timedelta(days=3),
        )
        event.save()

        member = ActionMember(user=self.user, action=event, approval_status="pending")
        member.save()
        response = self.client.get(reverse("profile_index"))
        self.assertContains(response,
            reverse("activity_task", args=(activity.type, activity.slug,)))
        self.assertContains(response, "Pending")
        self.assertContains(response, "Activity:")
        self.assertContains(response, "Event:")
        self.assertNotContains(response, "You have nothing in progress or pending.")

    def testCommitmentAchievement(self):
        """Check that the user's commitment achievements are loaded."""
        commitment = Commitment(
            title="Test commitment",
            description="A commitment!",
            point_value=10,
            type="commitment",
            slug="test-commitment",
        )
        commitment.save()

        # Test that profile page has a pending activity.
        member = ActionMember(user=self.user, action=commitment)
        member.save()
        response = self.client.get(reverse("profile_index"))
        self.assertContains(response,
            reverse("activity_task", args=(commitment.type, commitment.slug,)))
        self.assertContains(response, "In Progress")
        self.assertContains(response, "Commitment:")
        self.assertNotContains(response, "You have nothing in progress or pending.")

        # Test that the profile page has a rejected activity
        member.award_date = datetime.datetime.today()
        member.save()
        response = self.client.get(reverse("profile_index"))
        self.assertContains(response,
            reverse("activity_task", args=(commitment.type, commitment.slug,)))
        self.assertNotContains(response, "You have not been awarded anything yet!")
        self.assertNotContains(response, "In Progress")

    def testVariablePointAchievement(self):
        """Test that a variable point activity appears correctly in the my achievements list."""
        activity = Activity(
            title="Test activity",
            slug="test-activity",
            description="Variable points!",
            expected_duration=10,
            point_range_start=5,
            point_range_end=314160,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            confirm_type="text",
            type="activity",
        )
        activity.save()

        points = self.user.profile.points()
        member = ActionMember(
            user=self.user,
            action=activity,
            approval_status="approved",
        )
        member.points_awarded = 314159
        member.save()

        self.assertEqual(self.user.profile.points(), points + 314159,
            "Variable number of points should have been awarded.")

        # Kludge to change point value for the info bar.
        profile = self.user.profile
        profile.add_points(3, datetime.datetime.today(), "test")
        profile.save()

        response = self.client.get(reverse("profile_index"))
        self.assertContains(response,
            reverse("activity_task", args=(activity.type, activity.slug,)))
        # Note, this test may break if something in the page has the value 314159.
        # Try finding another suitable number.
        # print response.content
        self.assertContains(response, "314159", count=5,
            msg_prefix="314159 points should appear for the activity.")

    def testSocialBonusAchievement(self):
        """Check that the social bonus appears in the my achievements list."""
        # Create a second test user.
        user2 = User.objects.create_user("user2", "user2@test.com")
        event = Event.objects.create(
            title="Test event",
            slug="test-event",
            description="Testing!",
            expected_duration=10,
            point_value=10,
            social_bonus=10,
            pub_date=datetime.datetime.today(),
            expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
            type="event",
            event_date=datetime.datetime.today(),
        )

        # Create membership for the two users.
        m = ActionMember(
            user=self.user,
            action=event,
            approval_status="approved",
        )
        m.social_email = "user2@test.com"
        m.save()

        m2 = ActionMember(
            user=user2,
            action=event,
            approval_status="approved",
        )
        m2.social_email = "user@test.com"
        m2.save()

        response = self.client.get(reverse("profile_index"))
        self.assertContains(response, reverse("activity_task", args=(event.type, event.slug,)))
        entry = "Event: Test event (Social Bonus)"
        self.assertContains(response, entry, count=1,
            msg_prefix="Achievements should contain a social bonus entry")

    def testQuestAchievement(self):
        """test quest shown up in achievement"""
        quest = Quest(
            name="Test quest",
            quest_slug="test_quest",
            description="test quest",
            priority=1,
            unlock_conditions="True",
            completion_conditions="True",
        )
        quest.save()

        # Accept the quest, which should be automatically completed.
        response = self.client.post(
            reverse("quests_accept", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )
        response = self.client.get(reverse("profile_index"))
        self.assertContains(response, "Quest: Test quest", count=1,
            msg_prefix="Achievements should contain a quest entry")
