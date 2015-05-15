"""Raffle View Test"""
import datetime
import re

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.challenge_mgr.models import RoundSetting
from apps.utils import test_utils

from apps.widgets.raffle.models import RafflePrize


class RafflePrizesTestCase(TransactionTestCase):
    """Raffle Test"""
    fixtures = ["demo_teams.json"]

    def setUp(self):
        """Set up rounds, team, and a user."""
        # Set up rounds.

        test_utils.set_three_rounds()

        # Set up user
        self.user = test_utils.setup_user(username="user", password="changeme")

        challenge_mgr.register_page_widget("win", "raffle")
        self.client.login(username="user", password="changeme")

    def testIndex(self):
        """Check that we can load the index page."""
        raffle_prize = RafflePrize(
            title="Test raffle prize",
            description="A raffle prize for testing",
            round=RoundSetting.objects.get(name="Round 3"),
            value=5,
        )
        raffle_prize.save()

        response = self.client.get(reverse("win_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "Round 2 Raffle",
            msg_prefix="We should be in round 2 of the raffle.")
        print response
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">0</em>,",
            msg_prefix="User should not have any raffle tickets.")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">0</em>,",
            msg_prefix="User should not have any raffle tickets.")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should not have any raffle tickets.")
        deadline = challenge_mgr.get_round_info()["end"]
        date_string = deadline.strftime("%b. %d, %Y, %I:%M ")
        date_string = re.sub(r" \b0", " ", date_string)
        #self.assertContains(response, "Deadline for Round 2 submissions: " + date_string,
        #    msg_prefix="Raffle should have the correct deadline.")

        # Give the user some points and see if their tickets update.
        profile = self.user.profile
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()
        response = self.client.get(reverse("win_index"))
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">1</em>",
            msg_prefix="User should have 1 raffle ticket.")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">0</em>,",
            msg_prefix="User should have 1 raffle ticket.")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">1</em>",
            msg_prefix="User should have 1 raffle ticket.")

    def testAddRemoveTicket(self):
        """Test that we can add and remove a ticket for a prize."""
        raffle_prize = RafflePrize(
            title="Test raffle prize",
            description="A raffle prize for testing",
            round=RoundSetting.objects.get(name="Round 2"),
            value=5,
        )
        raffle_prize.save()

        profile = self.user.profile
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()

        # Test that we can add a ticket.
        response = self.client.get(reverse("win_index"))
        self.assertContains(response, reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should be a url to add a ticket.")

        # Test adding a ticket to a prize.
        response = self.client.post(reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">1</em>",
            msg_prefix="User should have one allocated ticket.")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">1</em>,",
            msg_prefix="User should have one allocated ticket.")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have one allocated ticket.")
        self.assertContains(response, reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should be an url to remove a ticket.")
        self.assertNotContains(response, reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should not be an url to add a ticket.")

        # Test adding another ticket to the prize.
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()
        response = self.client.post(reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            follow=True)
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">2</em>",
            msg_prefix="User should have two allocated tickets.")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">2</em>,",
            msg_prefix="User should have two allocated tickets.")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have two allocated tickets.")

        # Test removing a ticket.
        response = self.client.post(reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            follow=True)
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">2</em>",
            msg_prefix="User should have one allocated ticket and one available.")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">1</em>,",
            msg_prefix="User should have one allocated ticket and one available.")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">1</em>",
            msg_prefix="User should have one allocated ticket and one available.")
        self.assertContains(response, reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should be a url to add a ticket.")
        self.assertContains(response, reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should be an url to remove a ticket.")

    def testAddRemoveWithoutTicket(self):
        """Test that the user cannot remove a ticket from a prize they did not
        allocate tickets in."""
        raffle_prize = RafflePrize(
            title="Test raffle prize",
            description="A raffle prize for testing",
            round=RoundSetting.objects.get(name="Round 1"),
            value=5,
        )
        raffle_prize.save()

        # Test removing a ticket.
        response = self.client.post(reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have no tickets available")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">0</em>,",
            msg_prefix="User should have no tickets available")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have no tickets available")
        self.assertNotContains(response, reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should not be a url to add a ticket.")
        self.assertNotContains(response, reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should not be a url to remove a ticket.")

    def testAddWithoutTicket(self):
        """
        Test that the user cannot add a ticket to a raffle if they don't have any tickets.
        """
        raffle_prize = RafflePrize(
            title="Test raffle prize",
            description="A raffle prize for testing",
            round=RoundSetting.objects.get(name="Round 1"),
            value=5,
        )
        raffle_prize.save()

        # Test adding a ticket.
        response = self.client.post(reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response,
            "Your Total Raffle Tickets: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have no tickets available")
        self.assertContains(response,
            "Allocated:  <em class=\"raffle-ticket-num\">0</em>,",
            msg_prefix="User should have no tickets available")
        self.assertContains(response,
            "Available: <em class=\"raffle-ticket-num\">0</em>",
            msg_prefix="User should have no tickets available")
        self.assertNotContains(response, reverse("raffle_add_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should not be a url to add a ticket.")
        self.assertNotContains(response, reverse("raffle_remove_ticket", args=(raffle_prize.id,)),
            msg_prefix="There should not be a url to remove a ticket.")

    def testPrizeOutsideOfRound(self):
        """
        Test that a raffle prize outside of the round does not appear in the list.
        """

        raffle_prize = RafflePrize(
            title="Test raffle prize",
            description="A raffle prize for testing",
            round=RoundSetting.objects.get(name="Round 1"),
            value=5,
        )
        raffle_prize.save()

        response = self.client.get(reverse("win_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertNotContains(response, "Test raffle prize")
