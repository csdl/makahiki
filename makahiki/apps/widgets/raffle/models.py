"""Provides the model for the raffle widget."""

from django.db import models
from django.contrib.auth.models import User
from apps.managers.cache_mgr import cache_mgr
from apps.utils.utils import media_file_path
from apps.managers.challenge_mgr.models import RoundSetting

POINTS_PER_TICKET = 25
"""Number of points required to earn a raffle ticket"""

_MEDIA_LOCATION = "prizes"
"""location for uploaded files."""


class RafflePrize(models.Model):
    """RafflePrize model"""
    round = models.ForeignKey(RoundSetting, null=True, blank=True,
                              help_text="The round of the raffle prize.")

    title = models.CharField(max_length=50, help_text="The title of the raffle prize.")
    value = models.IntegerField(help_text="The value of the raffle prize")
    description = models.TextField(
        help_text="Description of the raffle prize.  Uses " \
                  "<a href='http://daringfireball.net/projects/markdown/syntax'>Markdown</a> " \
                  "formatting."
    )
    image = models.ImageField(
        max_length=1024,
        upload_to=media_file_path(_MEDIA_LOCATION),
        blank=True,
        help_text="A picture of the raffle prize."
    )
    winner = models.ForeignKey(User, null=True, blank=True,
                               help_text="The winner of the raffle prize. Normally, this is "
                                         "randomly picked by the system at the end of the round.")
    admin_tool_tip = ""

    def __unicode__(self):
        if self.round == None:
            return "%s: %s" % (self.round, self.title)
        else:
            return "%s: %s" % (self.round.name, self.title)

    def add_ticket(self, user):
        """Adds a ticket from the user if they have one.
          Throws an exception if they cannot add a ticket."""
        ticket = RaffleTicket(raffle_prize=self, user=user)
        ticket.save()
        cache_mgr.delete('get_quests-%s' % user.username)

    def remove_ticket(self, user):
        """Removes an allocated ticket."""
        # Get the first ticket that matches the query.
        ticket = RaffleTicket.objects.filter(raffle_prize=self, user=user)[0]
        ticket.delete()

    def allocated_tickets(self, user=None):
        """Returns the number of tickets allocated to this prize.
           Takes an optional argument to return the number of tickets allocated by the user."""
        query = self.raffleticket_set
        if user:
            query = query.filter(user=user)

        return query.count()


class RaffleTicket(models.Model):
    """Raffle ticket model"""
    user = models.ForeignKey(User)
    raffle_prize = models.ForeignKey(RafflePrize)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return ""

    @staticmethod
    def available_tickets(user):
        """Returns the number of raffle tickets the user has available."""
        profile = user.profile
        total_tickets = profile.points() / POINTS_PER_TICKET
        allocated_tickets = user.raffleticket_set.count()

        return total_tickets - allocated_tickets

    @staticmethod
    def total_tickets(user):
        """Return the total tickets available for this user."""
        return user.profile.points() / POINTS_PER_TICKET
