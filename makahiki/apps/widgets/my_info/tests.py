"""Profile page test"""

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from apps.managers.challenge_mgr import challenge_mgr

from apps.utils import test_utils


class ProfileFunctionalTestCase(TransactionTestCase):
    """Profile page test"""

    def setUp(self):
        """setup"""
        self.user = test_utils.setup_user(username="user", password="changeme")
        test_utils.set_competition_round()
        challenge_mgr.register_page_widget("profile", "my_info")

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()

        self.client.login(username="user", password="changeme")

    def testIndex(self):
        """Check that we can load the index page."""
        response = self.client.get(reverse("profile_index"))
        self.failUnlessEqual(response.status_code, 200)

    def testProfileUpdate(self):
        """Tests updating the user's profile."""
        # Construct a valid form
        user_form = {
            "display_name": "Test User",
            "about": "I rock",
            "theme": "theme-forest",
            "contact_email": "user@test.com",
            "contact_text": "8088675309",
            "contact_carrier": "tmobile",
            }
        # Test posting a valid form.
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "Your changes have been saved",
            msg_prefix="Successful form update should have a success message.")

        # Try getting the form again to see if info sticked.
        response = self.client.get(reverse("profile_index"))
        self.assertContains(response, "user@test.com", count=1,
            msg_prefix="Contact email should be saved.")
        self.assertContains(response, "808-867-5309", count=1,
            msg_prefix="Phone number should be saved.")
        self.assertContains(response, '<option value="tmobile" selected="selected">',
            msg_prefix="Carrier should be saved.")

        # Try posting the form again.
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "Your changes have been saved",
            msg_prefix="Second form update should have a success message.")

        # Test posting without a name
        user_form.update({"display_name": ""})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "This field is required",
            msg_prefix="User should not have a valid display name.")

        # Test posting with whitespace as a name
        user_form.update({"display_name": "    "})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "This field is required",
            msg_prefix="User should not have a valid display name.")

        # Test posting a name that is too long.
        letters = "abcdefghijklmnopqrstuvwxyz"
        user_form.update({"display_name": letters})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertNotContains(response, "Your changes have been saved",
            msg_prefix="Profile with long name should not be valid.")

        # Test posting without a valid email
        user_form.update({"display_name": "Test User", "contact_email": "foo"})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "Enter a valid email address",
            msg_prefix="User should not have a valid email address")

        # Test posting without a valid phone number
        user_form.update({"contact_email": "user@test.com", "contact_text": "foo"})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "Phone numbers must be in XXX-XXX-XXXX format.",
            msg_prefix="User should not have a valid contact number.")

    def testProfileWithDupName(self):
        """test profile without dupliate name"""
        user = User.objects.create_user("user2", "user2@test.com")
        profile = user.profile
        profile.name = "Test U."
        profile.save()

        user_form = {
            "display_name": "Test U.",
            "about": "I rock",
            "stay_logged_in": True,
            "theme": "theme-forest",
            "contact_email": "user@test.com",
            "contact_text": "8088675309",
            "contact_carrier": "tmobile",
            }
        # Test posting form with dup name.
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name should raise an error.")

        user_form.update({"display_name": "  Test U.     "})
        # Test posting a form with a dup name with a lot of whitespace.
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        # print response.content
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name with whitespace should raise an error.")
        self.assertContains(response, "Test U.", count=1,
            msg_prefix="This should only be in the form and in the error message.")

        user_form.update({"display_name": "Test   U."})
        response = self.client.post(reverse("profile_save"), user_form, follow=True)
        # print response.content
        self.assertContains(response, "Please use another name.",
            msg_prefix="Duplicate name with internal whitespace should raise an error.")
