"""raffle model test"""
import os
import datetime

from django.test import TransactionTestCase
from django.conf import settings
from django.core.files.images import ImageFile
from django.contrib.auth.models import User
from apps.utils import test_utils

from apps.widgets.raffle.models import RafflePrize, RaffleTicket
from apps.managers.challenge_mgr.models import RoundSetting


class RafflePrizeTests(TransactionTestCase):
    """
    Tests the RafflePrize model.
    """

    def setUp(self):
        """
        Sets up a test individual prize for the rest of the tests.
        This prize is not saved, as the round field is not yet set.
        """

        test_utils.set_competition_round()

        # Create a test user
        self.user = User.objects.create_user("user", "user@test.com", password="changeme")

        image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
        image = ImageFile(open(image_path, "r"))
        self.prize = RafflePrize(
            title="Super prize!",
            description="A test prize",
            image=image,
            round=RoundSetting.objects.get(name="Round 1"),
            value=5,
        )

    def testTicketAllocation(self):
        """
        Tests that a user can allocate a ticket.
        """
        self.prize.round = RoundSetting.objects.get(name="Round 1")
        self.prize.save()

        profile = self.user.profile
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()

        # Add a ticket to the prize
        self.assertEqual(RaffleTicket.available_tickets(self.user), 1,
                         "User should have one raffle ticket.")
        self.prize.add_ticket(self.user)
        self.assertEqual(RaffleTicket.available_tickets(self.user), 0,
                         "User should not have any raffle tickets.")
        self.assertEqual(self.prize.allocated_tickets(), 1,
            "1 ticket should be allocated to this prize.")
        self.assertEqual(self.prize.allocated_tickets(self.user), 1,
            "1 ticket should be allocated by this user to this prize.")

        # Have another user add a ticket to the prize.
        user2 = User.objects.create_user("user2", "user2@test.com", password="changeme")

        profile = user2.profile
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()

        # Add a ticket to the prize
        self.prize.add_ticket(user2)
        self.assertEqual(self.prize.allocated_tickets(), 2,
            "2 tickets should be allocated to this prize.")
        self.assertEqual(self.prize.allocated_tickets(user2), 1,
            "1 ticket should be allocated by this user to this prize.")

        # Add another ticket to the prize.
        profile.add_points(25, datetime.datetime.today(), "test")
        profile.save()

        self.prize.add_ticket(user2)
        self.assertEqual(self.prize.allocated_tickets(), 3,
            "3 tickets should be allocated to this prize.")
        self.assertEqual(self.prize.allocated_tickets(user2), 2,
            "2 tickets should be allocated by this user to this prize.")

        # Remove a ticket from the prize.
        self.prize.remove_ticket(self.user)
        self.assertEqual(self.prize.allocated_tickets(), 2,
            "2 tickets should be allocated to this prize.")
        self.assertEqual(self.prize.allocated_tickets(self.user), 0,
            "No tickets should be allocated by this user to this prize.")

        self.prize.remove_ticket(user2)
        self.assertEqual(self.prize.allocated_tickets(), 1,
            "1 ticket should be allocated to this prize.")
        self.assertEqual(self.prize.allocated_tickets(user2), 1,
            "1 ticket should be allocated by this user to this prize.")

    def tearDown(self):
        """
        Deletes the created image file in prizes.
        """
        self.prize.image.delete()
        self.prize.delete()
