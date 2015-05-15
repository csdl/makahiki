"""Quests Test"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.utils import test_utils
from apps.widgets.quests.quests import get_quests


class QuestFunctionalTestCase(TransactionTestCase):
    """Quests Tests"""
    def setUp(self):
        """setup"""
        self.user = User.objects.create_user("user", "user@test.com", password="changeme")
        profile = self.user.profile
        profile.setup_profile = True
        profile.setup_complete = True
        profile.save()

        test_utils.enable_quest()
        challenge_mgr.register_page_widget("home", "home")

        self.client.login(username="user", password="changeme")

#    def testNoQuests(self):
#        """Test that the appropriate text is displayed when there are no quests."""
#        cache_mgr.clear()
#        response = self.client.get(reverse("home_index"))
#        self.assertContains(response,
#            "There are no quests available at this time.  Please check back later!")

    def testGetQuests(self):
        """Test that quests show up in the interface."""
        quest = test_utils.create_quest(completion_conditions=False)
        quest.unlock_conditions = "False"
        quest.save()
        cache_mgr.clear()

        response = self.client.get(reverse("home_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertNotContains(response, "Test quest",
            msg_prefix="Test quest should not be available to the user.")

        quest.unlock_conditions = "True"
        quest.save()
        cache_mgr.clear()
        response = self.client.get(reverse("home_index"))
        self.assertContains(response, "Test quest",
            msg_prefix="Test quest should be available to the user.")

    def testAcceptQuest(self):
        """Test that a user can accept a quest using a url."""
        quest = test_utils.create_quest(completion_conditions=False)
        cache_mgr.clear()

        response = self.client.get(reverse("home_index"))
        self.assertContains(response, "Test quest",
            msg_prefix="Test quest should be available to the user.")
        response = self.client.post(
            reverse("quests_accept", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )
        self.assertRedirects(response, reverse("home_index"))
        quests = get_quests(self.user)
        self.assertEqual(len(quests["user_quests"]), 1, "User should have one quest.")

    def testOptOutOfQuest(self):
        """Test that a user can opt out of the quest."""
        quest = test_utils.create_quest(completion_conditions=False)
        cache_mgr.clear()

        response = self.client.get(reverse("home_index"))
        self.assertContains(response, "Test quest",
            msg_prefix="Test quest should be available to the user.")
        response = self.client.post(
            reverse("quests_opt_out", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )
        self.assertRedirects(response, reverse("home_index"))
        self.assertNotContains(response, "Test quest", msg_prefix="Test quest should not be shown.")
        self.assertFalse("completed" in response.context["DEFAULT_VIEW_OBJECTS"]["quests"],
            "There should not be any completed quests.")

    def testCancelQuest(self):
        """Test that a user can cancel their participation in a quest."""
        quest = test_utils.create_quest(completion_conditions=False)
        cache_mgr.clear()

        response = self.client.post(
            reverse("quests_accept", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )
        self.assertTrue(quest in response.context["DEFAULT_VIEW_OBJECTS"]["quests"]["user_quests"],
            "User should be participating in the test quest.")
        response = self.client.post(
            reverse("quests_cancel", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )
        self.assertRedirects(response, reverse("home_index"))
        self.assertTrue(
            quest not in response.context["DEFAULT_VIEW_OBJECTS"]["quests"]["user_quests"],
            "Test quest should not be in user's quests.")
        self.assertTrue(
            quest in response.context["DEFAULT_VIEW_OBJECTS"]["quests"]["available_quests"],
            "Test quest should be in available quests.")

    def testQuestCompletion(self):
        """Test that a user gets a dialog box when they complete a quest."""
        quest = test_utils.create_quest(completion_conditions=True)
        cache_mgr.clear()

        response = self.client.get(reverse("home_index"))

        self.assertEqual(len(response.context["DEFAULT_VIEW_OBJECTS"]["notifications"]["alerts"]),
            0, "User should not have any completed quests.")

        response = self.client.post(
            reverse("quests_accept", args=(quest.quest_slug,)),
            follow=True,
            HTTP_REFERER=reverse("home_index"),
        )

        self.assertRedirects(response, reverse("home_index"))

        response = self.client.get(reverse("home_index"))

        self.assertFalse(quest in response.context["DEFAULT_VIEW_OBJECTS"]["quests"]["user_quests"],
            "Quest should not be loaded as a user quest.")
        message = "Congratulations! You completed the '%s' quest." % quest.name
        self.assertContains(response, message,
            msg_prefix="Quest completion message should be shown.")
        self.assertContains(response, "notification-dialog",
            msg_prefix="Notification dialog should be shown.")
