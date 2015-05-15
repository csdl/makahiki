'''Models for the Smart Grid Play Tester.
Created on Jun 23, 2013

@author: Cam Moore
'''
from django.db import models
from django.contrib.auth.models import User
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerTextPromptQuestion, Draft
from django.contrib.contenttypes import generic
from apps.widgets.notifications.models import UserNotification
from apps.managers.score_mgr.models import PointsTransaction
import os
from django.conf import settings
import datetime
from apps.managers.score_mgr import score_mgr
from apps.widgets.smartgrid import SETUP_WIZARD_ACTIVITY
from django.core.urlresolvers import reverse


_MEDIA_LOCATION_ACTION = os.path.join("smartgrid", "actions")
"""location for the uploaded files for actions."""

_MEDIA_LOCATION_MEMBER = os.path.join("smartgrid", "members")
"""location for the uploaded files for actionmembers."""


def activity_image_file_path(instance=None, filename=None, user=None):
    """Returns the file path used to save an activity confirmation image."""
    if instance:
        user = user or instance.user
    return os.path.join(settings.MAKAHIKI_MEDIA_PREFIX, _MEDIA_LOCATION_MEMBER,
                        user.username, filename)


class TesterActionSubmittion(models.Model):
    """Represents the join between commitments and users.  Has fields for
    commenting on a commitment and whether or not the commitment is currently
    active."""

    STATUS_TYPES = (
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        )

    user = models.ForeignKey(User)
    action = models.ForeignKey(DesignerAction)
    draft = models.ForeignKey(Draft)
    question = models.ForeignKey(DesignerTextPromptQuestion, null=True, blank=True)
    notifications = generic.GenericRelation(UserNotification, editable=False)
    pointstransactions = generic.GenericRelation(PointsTransaction, editable=False)

    submission_date = models.DateTimeField(
        editable=False,
        help_text="The submission date.")
    completion_date = models.DateField(
        null=True, blank=True,
        help_text="The completion date."
    )
    award_date = models.DateTimeField(
        null=True, blank=True, editable=False,
        help_text="The award date.")
    approval_status = models.CharField(
        max_length=20, choices=STATUS_TYPES, default="pending",
        help_text="The approval status.")
    social_bonus_awarded = models.BooleanField(default=False,
        help_text="Is the social bonus awarded?")
    comment = models.TextField(
        blank=True,
        help_text="The comment from user submission.")
    social_email = models.TextField(
        blank=True, null=True,
        help_text="Email address of the person the user went with.")
    response = models.TextField(
        blank=True,
        help_text="The response of the submission.")
    admin_comment = models.TextField(
        blank=True,
        help_text="Reason for approval/rejection")
    image = models.ImageField(
        max_length=1024, blank=True,
        upload_to=activity_image_file_path,
        help_text="Uploaded image for verification.")
    points_awarded = models.IntegerField(
        blank=True, null=True,
        help_text="Number of points to award for activities with variable point values.")
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)
    admin_link = models.CharField(max_length=100, blank=True, null=True)
    admin_tool_tip = "Player submission for Actions"

    class Meta:
        """meta"""
        unique_together = ('user', 'action', 'submission_date')
        verbose_name_plural = "Action Submissions"

    def __unicode__(self):
        return "%s : %s" % (self.action.title, self.user.username)

    def active(self):
        """return active member"""
        return self.approval_status == "approved"

    def user_link(self):
        """return the user first_name."""
        return '<a href="%s/%d/">%s</a>' % ("/admin/player_mgr/profile",
                                            self.user.profile.pk,
                                            self.user.username)
    user_link.allow_tags = True
    user_link.short_description = 'Link to profile'

    def days_left(self):
        """
        Returns how many days are left before the user can submit the activity.
        """
        diff = self.completion_date - datetime.date.today()
        if diff.days < 0:
            return 0

        return diff.days

    def check_admin_link(self):
        """Sets admin_link if not already set."""
        if not self.admin_link:
            link = "/admin/smartgrid/" + self.action.type + "/" + str(self.action.id)
            self.admin_link = link

    def save(self, *args, **kwargs):
        """custom save method."""

        self.check_admin_link()

        if self.social_bonus_awarded:
            # only awarding social bonus
            super(TesterActionSubmittion, self).save(args, kwargs)
            return

        if self.approval_status == u"rejected":
            self.award_date = None
            super(TesterActionSubmittion, self).save(args, kwargs)

            self._handle_activity_notification(self.approval_status)
        else:
            if self.approval_status == u"pending":
                # Mark pending items as submitted.

                self.submission_date = datetime.datetime.today()

                if self.action.type == "commitment" and not self.completion_date:
                    self.completion_date = self.submission_date + \
                        datetime.timedelta(days=self.action.commitment_length)

                super(TesterActionSubmittion, self).save(args, kwargs)

                self._award_signup_points()

            else:    # is approved
                if not self.points_awarded:
                    self.points_awarded = self.action.point_value

                # Record dates.
                self.award_date = datetime.datetime.today()

                if self.submission_date:
                    if self.action.type in ("event", "excursion"):
                        # this is an event with signup
                        # must save before awarding point due to the generic foreign key relation
                        super(TesterActionSubmittion, self).save(args, kwargs)
                        self._award_possible_reverse_penalty_points()
                else:
                    # always make sure the submission_date is set
                    self.submission_date = self.award_date

                # must save before awarding point due to the generic foreign key relation
                super(TesterActionSubmittion, self).save(args, kwargs)
                self._award_points()

                self.social_bonus_awarded = self._award_possible_social_bonus()
                if self.social_bonus_awarded:
                    super(TesterActionSubmittion, self).save(args, kwargs)

                self._handle_activity_notification(self.approval_status)

    def _award_points(self):
        """Custom save method to award points."""
        profile = self.user.profile

        points = self.points_awarded
        if not points:
            points = self.action.point_value

        if self.action.type == "activity":
            transaction_date = self.submission_date
        elif self.action.type == "commitment":
            transaction_date = self.award_date
        else:  # is Event
            transaction_date = self.award_date

        profile.add_points(points, transaction_date, self.action, self)

    def _award_possible_social_bonus(self):
        """award possible social bonus."""

        profile = self.user.profile
        social_message = "%s (Social Bonus)" % self.action

        # award social bonus to others who referenced my email and successfully completed
        # the activity
        if self.user.email:
            ref_members = TesterActionSubmittion.objects.filter(action=self.action,
                                                      approval_status="approved",
                                                      social_email=self.user.email)
            for m in ref_members:
                if not m.social_bonus_awarded:
                    ref_profile = m.user.profile
                    ref_profile.add_points(m.action.social_bonus,
                                           m.award_date,
                                           social_message, self)
                    m.social_bonus_awarded = True
                    m.save()

        ## award social bonus to myself if the ref user had successfully completed the activity
        if self.social_email and not self.social_bonus_awarded:
            ref_members = TesterActionSubmittion.objects.filter(user__email=self.social_email,
                                                      approval_status="approved",
                                                      action=self.action)
            if ref_members:
                profile.add_points(self.action.social_bonus,
                                   self.award_date,
                                   social_message, self)
                return True

        return False

    def _award_signup_points(self):
        """award the sign up point for commitment and event."""

        if self.action.type != "activity":
            #increase the point from signup
            message = "%s (Sign up)" % self.action
            self.user.profile.add_points(score_mgr.signup_points(),
                                               self.submission_date,
                                               message,
                                               self)

    def _drop_signup_points(self):
        """award the sign up point for commitment and event."""

        if self.action.type != "activity":
            #increase the point from signup
            message = "%s (Drop Sign up)" % self.action
            self.user.profile.remove_points(score_mgr.signup_points(),
                                               self.submission_date,
                                               message,
                                               self)

    def _award_possible_reverse_penalty_points(self):
        """ reverse event noshow penalty."""
        if self._has_noshow_penalty():
            message = "%s (Reverse No Show Penalty)" % self.action
            self.user.profile.add_points(
                score_mgr.noshow_penalty_points() + score_mgr.signup_points(),
                self.award_date,
                message,
                self)

    def _has_noshow_penalty(self):
        """Returns False"""
        return False

    def _handle_activity_notification(self, status):
        """Creates a notification for rejected or approved tasks.
        This also creates an email message if it is configured.
        """
        # don't create notification if the action is the SETUP_WIZARD_ACTIVITY
        # that is used in the setup wizard.
        if self.action.slug == SETUP_WIZARD_ACTIVITY:
            return

        # Construct the message to be sent.
        status_nicely = 'not approved' if status != 'approved' else status
        message = 'Your response to <a href="%s#action-details">"%s"</a> %s was %s.' % (
            reverse("activity_task", args=(self.action.type, self.action.slug,)),
            self.action.title,
            # The below is to tell the javascript to convert into a pretty date.
            # See the prettyDate function in media/js/makahiki.js
            '<span class="rejection-date" title="%s"></span>' % self.submission_date.isoformat(),
            status_nicely,
            )

        if status != 'approved':
            message += " You can still get points by clicking on the link and trying again."
            UserNotification.create_error_notification(self.user, message, display_alert=True,
                                                       content_object=self)
        else:
            points = self.points_awarded if self.points_awarded else self.action.point_value
            message += " You earned %d points!" % points

            UserNotification.create_success_notification(self.user, message, display_alert=True,
                                                         content_object=self)

    def post_to_wall(self):
        """post to team wall as system post."""
        pass

    def invalidate_cache(self):
        """Invalidate the categories cache."""
#         username = self.user.username
#         cache_mgr.delete('smartgrid-levels-%s' % username)
#         cache_mgr.delete('smartgrid-completed-%s' % username)
#         cache_mgr.delete('user_events-%s' % username)
#         cache_mgr.delete('get_quests-%s' % username)
#         cache_mgr.delete('golow_actions-%s' % username)
#         team = self.user.profile.team
#         if team:
#             cache_mgr.invalidate_template_cache("team_avatar", self.action.id, team.id)
#         cache_mgr.invalidate_template_cache("my_commitments", username)
#         cache_mgr.invalidate_template_cache("my_achievements", username)
#         cache_mgr.invalidate_template_cache("smartgrid", username)
        pass

    def delete(self, using=None):
        """Custom delete method to remove the points for completed action."""
        profile = self.user.profile

        if self.approval_status == "approved":
            # remove all related point transaction
            profile.remove_related_points(self)
        else:
            # drop any possible signup transaction
            self._drop_signup_points()
        self.invalidate_cache()

        super(TesterActionSubmittion, self).delete()
