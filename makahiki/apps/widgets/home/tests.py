"""
home page tests
"""

import json
import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.challenge_mgr.models import RoundSetting

from apps.managers.player_mgr.models import Profile
from apps.utils import test_utils
from apps.widgets.help.models import HelpTopic
from apps.widgets.smartgrid import SETUP_WIZARD_ACTIVITY
from apps.widgets.smartgrid.models import Activity


class HomeFunctionalTestCase(TransactionTestCase):
    """Home Test Case."""

    def testIndex(self):
        """Check that we can load the index."""
        test_utils.set_competition_round()
        User.objects.create_user("user", "user@test.com", password="changeme")
        self.client.login(username="user", password="changeme")

        challenge_mgr.register_page_widget("home", "home")

        response = self.client.get(reverse("home_index"))
        self.failUnlessEqual(response.status_code, 200)


class CompetitionMiddlewareTestCase(TransactionTestCase):
    """competition middleware test."""

    def setUp(self):
        User.objects.create_user("user", "user@test.com", password="changeme")
        self.client.login(username="user", password="changeme")

    def testBeforeCompetition(self):
        """
        Check that the user is redirected before the competition starts.
        """
        start = datetime.datetime.today() + datetime.timedelta(days=1)
        end = start + datetime.timedelta(days=7)
        RoundSetting.objects.create(name="Round 1", start=start, end=end)

        response = self.client.get(reverse("home_index"), follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                "widgets/home/templates/restricted.html")
        self.assertContains(response, "The competition starts at")

    def testAfterCompetition(self):
        """
        Check that the user is redirected after the competition ends.
        """
        start = datetime.datetime.today() - datetime.timedelta(days=8)
        end = start - datetime.timedelta(days=7)
        RoundSetting.objects.create(name="Round 1", start=start, end=end)

        response = self.client.get(reverse("home_index"), follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                "widgets/home/templates/restricted.html")
        self.assertContains(response, "The Kukui Cup is now over")


class SetupWizardFunctionalTestCase(TransactionTestCase):
    """setup widzard test cases."""

    def setUp(self):
        """setup."""
        test_utils.set_competition_round()
        self.user = User.objects.create_user("user", "user@test.com", password="changeme")

        # create the term help-topic
        HelpTopic.objects.create(title="", slug="terms-and-conditions", category="faq", contents="")

        # create the setup activity
        Activity.objects.create(slug=SETUP_WIZARD_ACTIVITY, name="", title="", expected_duration=5)

        challenge_mgr.register_page_widget("home", "home")
        self.client.login(username="user", password="changeme")

    def testDisplaySetupWizard(self):
        """Check that the setup wizard is shown for new users."""
        response = self.client.get(reverse("home_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to the Kukui Cup")

    def testSetupTerms(self):
        """Check that we can access the terms page of the setup wizard."""
        response = self.client.get(reverse("setup_terms"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/terms.html")
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

    def testReferralStep(self):
        """
        Test that we can record referral emails from the setup page.
        """
        user2 = User.objects.create_user("user2", "user2@test.com")

        # Test we can get the referral page.
        response = self.client.get(reverse('setup_referral'), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

        # Test referring using their own email
        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': self.user.email,
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/referral.html")
        self.assertEqual(len(response.context['form'].errors), 1,
            "Using their own email as referrer should raise an error.")

        # Test referring using the email of a user who is not in the system.
        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': 'user@foo.com',
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/referral.html")
        self.assertEqual(len(response.context['form'].errors), 1,
            'Using external email as referrer should raise an error.')

        # Test bad email.
        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': 'foo',
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].errors), 1,
            'Using a bad email should insert an error.')
        self.assertTemplateUsed(response, "first-login/referral.html")

        # Staff user should not be able to be referred.
        user2.is_staff = True
        user2.save()

        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': user2.email,
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].errors), 1,
            'Using an admin as a referrer should raise an error.')
        self.assertTemplateUsed(response, "first-login/referral.html")

        user2.is_staff = False
        user2.save()

        # Test no referrer.
        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': '',
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")

        # Test successful referrer
        response = self.client.post(reverse('setup_referral'), {
            'referrer_email': user2.email,
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.referring_user,
                         user2,
                         'User 1 should be referred by user 2.')

        # Test getting the referral page now has user2's email.
        response = self.client.get(reverse('setup_referral'), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
                            user2.email,
                            msg_prefix="Going back to referral page should " \
                                       "have second user's email.")

    def testSetupProfile(self):
        """Check that we can access the profile page of the setup wizard."""
        profile = self.user.profile
        profile.name = "Test User"
        profile.save()
        response = self.client.get(reverse("setup_profile"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/profile.html")
        self.assertContains(response, profile.name)
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

    def testSetupProfileUpdate(self):
        """Check that we can update the profile of the user in the setup
        wizard."""
        profile = self.user.profile
        points = profile.points()
        response = self.client.post(reverse("setup_profile"), {
            "display_name": "Test User",
            }, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/activity.html")

        user = User.objects.get(username="user")
        self.assertEqual(points + 5, user.profile.points(),
            "Check that the user has been awarded points.")
        self.assertTrue(user.profile.setup_profile,
            "Check that the user has now set up their profile.")

        # Check that updating again does not award more points.
        response = self.client.post(reverse("setup_profile"), {
            "display_name": "Test User",
            }, follow=True)
        user = User.objects.get(username="user")
        self.assertEqual(points + 5, user.profile.points(),
            "Check that the user was not awarded any more points.")
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/activity.html")

    def testSetupProfileWithoutName(self):
        """Test that there is an error when the user does not supply a
        username."""
        _ = self.user.profile
        response = self.client.post(reverse("setup_profile"), {
            "display_name": "",
            })
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")

    def testSetupProfileWithDupName(self):
        """Test that there is an error when the user uses a duplicate display
         name."""
        _ = self.user.profile

        user2 = User.objects.create_user("user2", "user2@test.com")
        profile2 = user2.profile
        profile2.name = "Test U."
        profile2.save()

        response = self.client.post(reverse("setup_profile"), {
            "display_name": "Test U.",
            }, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name should raise an error.")

        response = self.client.post(reverse("setup_profile"), {
            "display_name": "   Test U.    ",
            }, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name with whitespace should raise an error.")

        response = self.client.post(reverse("setup_profile"), {
            "display_name": "Test   U.",
            }, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "first-login/profile.html")
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name with whitespace should raise an error.")

    def testSetupActivity(self):
        """Check that we can access the activity page of the setup wizard."""
        response = self.client.get(reverse("setup_activity"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/activity.html")
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

    def testSetupQuestion(self):
        """Check that we can access the question page of the setup wizard."""
        response = self.client.get(reverse("setup_question"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/question.html")
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

    def testSetupComplete(self):
        """
        Check that we can access the complete page of the setup wizard.
        """
        # Test a normal GET request (answer was incorrect).
        response = self.client.get(reverse("setup_complete"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/complete.html")
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

        user = User.objects.get(username="user")
        self.assertTrue(user.profile.setup_complete,
            "Check that the user has completed the profile setup.")

        # Test a normal POST request (answer was correct).
        profile = user.profile
        profile.setup_complete = False
        profile.save()

        response = self.client.post(reverse("setup_complete"), {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(response, "first-login/complete.html")
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Response JSON could not be decoded.")

        user = User.objects.get(username="user")
        self.assertTrue(user.profile.setup_complete,
            "Check that the user has completed the profile setup.")
