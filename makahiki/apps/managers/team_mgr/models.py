"""Defines the model for teams."""

from django.db import models
from django.contrib.auth.models import User
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.utils.utils import media_file_path


_MEDIA_LOCATION = "team"
"""location for uploaded files."""


class Group(models.Model):
    """Defines the group that a team belongs to."""

    name = models.CharField(max_length=200, help_text="The name of the group.")
    admin_tool_tip = "Groupings of teams. Groups are optional."

    def __unicode__(self):
        return self.name

    def team_points_leaders(self, num_results=None, round_name=None):
        """Returns the top points leaders for the given group."""
        return score_mgr.team_points_leaders_in_group(self, num_results, round_name)


class Team(models.Model):
    """Represents the team that a player belongs to."""

    group = models.ForeignKey(Group, help_text="The group this team belongs to.")
    name = models.CharField(help_text="The team name", max_length=50)
    size = models.IntegerField(null=True, blank=True, default=0,
                               help_text="The size of the team. It is the total number of "
                                         "residents in the team. Non-zero value will be used to "
                                         "normalize the team total score and participation rate.")
    logo = models.ImageField(
        max_length=1024, blank=True, null=True,
        upload_to=media_file_path(_MEDIA_LOCATION),
        help_text="The logo of the team.",)
    admin_tool_tip = "The team a player belongs to. Teams are required."

    def __unicode__(self):
        return self.name

    def current_round_rank(self):
        """Gets the ranking of this team during the current round."""
        current_round = challenge_mgr.get_round_name()
        return score_mgr.team_rank(self, round_name=current_round)

    def rank(self, round_name=None):
        """Returns the rank of the team across all groups."""
        return score_mgr.team_rank(self, round_name=round_name)

    def current_round_points(self):
        """Returns the number of points for the current round."""
        current_round = challenge_mgr.get_round_name()
        return score_mgr.team_points(self, round_name=current_round)

    def points(self, round_name=None):
        """Returns the total number of points for the team.  Optional parameter for a round."""
        return score_mgr.team_points(self, round_name)

    def points_leaders(self, num_results=None, round_name=None):
        """Gets the individual points leaders for the team."""
        entries = score_mgr.player_points_leaders_in_team(self, num_results, round_name)
        if entries:
            return entries
        else:
            return None

    def save(self, *args, **kwargs):
        """Custom save method."""
        super(Team, self).save(*args, **kwargs)

        # also create the resource goal settings
        from apps.widgets.resource_goal.models import EnergyGoalSetting, WaterGoalSetting
        if not EnergyGoalSetting.objects.filter(team=self):
            EnergyGoalSetting(team=self, wattdepot_source_name=self.name).save()
        if not WaterGoalSetting.objects.filter(team=self):
            WaterGoalSetting(team=self).save()

        cache_mgr.clear()

    class Meta:
        """Meta"""
        ordering = ("group", "name")


class Post(models.Model):
    """Represents a wall post on a user's wall."""
    user = models.ForeignKey(User, help_text="The user who submit the post.")
    team = models.ForeignKey(Team, help_text="The team of the submitter.")
    text = models.TextField(help_text="The content of the post.")
    style_class = models.CharField(max_length=50, default="user_post",
                                   help_text="The CSS class to apply to this post.")
    created_at = models.DateTimeField(editable=False, auto_now_add=True,
                                      help_text="The create timestamp")

    def __unicode__(self):
        return "%s (%s): %s" % (self.team, self.user.username, self.text)

    class Meta:
        """meta"""
        verbose_name_plural = "Wall Posts"

    def date_string(self):
        """Formats the created date into a pretty string."""
        return self.created_at.strftime("%m/%d %I:%M %p")
