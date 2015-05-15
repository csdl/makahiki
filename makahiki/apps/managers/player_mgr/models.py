"""Define the model for Player state."""
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from localflavor.us.models import PhoneNumberField
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr.models import Team
from django.db import models


class Profile(models.Model):
    """Profile represents a player's profile info, and his points,
       and other book keeping.
    """
    THEME_CHOICES = ((key, key) for key in settings.INSTALLED_THEMES)

    user = models.OneToOneField(User)

    name = models.CharField('Display Name', unique=True, max_length=50,
                            help_text="The display name of the player")
    team = models.ForeignKey(Team, null=True, blank=True,
                             help_text="The team of the player")
    theme = models.CharField(null=True, blank=True, choices=THEME_CHOICES, max_length=50,
                             help_text="The UI theme for this player.")
    contact_text = PhoneNumberField(null=True, blank=True,
                                    help_text="The contact phone number")
    contact_carrier = models.CharField(max_length=50, null=True, blank=True,
                                       help_text="The phone carrier of the contact number")
    is_ra = models.BooleanField(default=False,
                                help_text="Is RA?")

    # Check first login completion.
    setup_profile = models.BooleanField(default=False, editable=False,
                                        help_text="Has the player's profile setup?")
    setup_complete = models.BooleanField(default=False,
                                         help_text="Has the player completed the first login?")
    completion_date = models.DateTimeField(null=True, blank=True,
                                           help_text="The date of the first login completed")
    # Check visits for daily visitor badge.
    daily_visit_count = models.IntegerField(default=0, editable=False,
                                            help_text="The number of the daily visit")
    last_visit_date = models.DateField(null=True, blank=True,
                                       help_text="The date of the last visit")
    # Check for referrer
    referring_user = models.ForeignKey(User, null=True, blank=True,
                                       related_name='referred_profiles',
                                       help_text="The referring user")
    referrer_awarded = models.BooleanField(default=False, editable=False,
                                           help_text="Has the referral bonus awarded?")
    properties = models.TextField(blank=True,
                                  help_text="Optional properties for the profile.")

    class Meta:
        """Meta sets verbose name and plural."""
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __unicode__(self):
        return self.name

    def user_link(self):
        """return the user first_name."""
        return '<a href="%s/%d/">%s</a>' % ("/admin/auth/user", self.user.pk, self.user.username)

    user_link.allow_tags = True
    user_link.short_description = 'Link to User'

    def current_round_points(self):
        """Returns the total number of points for the user.  Optional parameter for a round."""
        current_round = challenge_mgr.get_round_name()
        return score_mgr.player_points(self, round_name=current_round)

    def points(self):
        """Returns the overall total number of points for the user."""
        return score_mgr.player_points(self, round_name="Overall")

    def last_awarded_submission(self):
        """Returns the last awarded submission date."""
        return score_mgr.player_last_awarded_submission(self)

    def current_round_overall_rank(self):
        """Returns the overall rank of the user for the current round."""
        current_round = challenge_mgr.get_round_name()
        return score_mgr.player_rank(self, round_name=current_round)

    def overall_rank(self):
        """Returns the rank of the user for the round."""
        return score_mgr.player_rank(self)

    def current_round_team_rank(self):
        """Returns the rank of the user for the current round in their own team."""
        current_round = challenge_mgr.get_round_name()
        return score_mgr.player_rank_in_team(self, round_name=current_round)

    def team_rank(self):
        """Returns the rank of the user in their own team."""
        return score_mgr.player_rank_in_team(self)

    def add_points(self, points, transaction_date, message, related_object=None):
        """Adds points based on the point value of the submitted object."""
        score_mgr.player_add_points(self, points, transaction_date, message, related_object)
        self._award_possible_referral_bonus()

    def _award_possible_referral_bonus(self):
        """award possible referral bonus."""

        # check if the referral game mechanics is enabled
        if not challenge_mgr.is_game_enabled("Referral Game Mechanics"):
            return

        has_referral = self.referring_user is not None and not self.referrer_awarded

        if has_referral and self.points() >= score_mgr.active_threshold_points():
            referrer = self.referring_user.profile
            if referrer.setup_profile:
                self.referrer_awarded = True
                self.save()
                score_mgr.award_referral_bonus(self, referrer)

    def remove_points(self, points, transaction_date, message, related_object=None):
        """Removes points from the user."""
        score_mgr.player_remove_points(self, points, transaction_date, message, related_object)

    def remove_related_points(self, related_object):
        """Removes points related to the related_object (action) from the user."""
        score_mgr.player_remove_related_points(self, related_object)


def create_user_profile(user):
    """create a profile related to the user."""
    profile, is_create = Profile.objects.get_or_create(user=user)
    if is_create or profile.name == user.username:
        if user.first_name and user.last_name:
            firstname = user.first_name.capitalize()
            lastname = user.last_name.capitalize()
            profile.name = "%s %s." % (firstname, lastname[:1])

            if Profile.objects.filter(name=profile.name).exclude(user=user).exists():
                profile.name = firstname + " " + lastname
        else:
            profile.name = user.username
        profile.save()


def create_profile(sender, instance=None, **kwargs):
    """ Create a profile automatically when creating a user."""
    _ = sender
    if not kwargs.get('raw', False):
        create_user_profile(instance)

post_save.connect(create_profile, sender=User)

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^localflavor\.us\.models\.PhoneNumberField"])
