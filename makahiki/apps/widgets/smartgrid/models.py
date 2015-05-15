"""Smart Grid Game model definition."""

import datetime
import random
from django.core.exceptions import ObjectDoesNotExist

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string
from localflavor.us.models import PhoneNumberField
import os
from apps.managers.challenge_mgr import challenge_mgr

from apps.managers.score_mgr import score_mgr
from apps.managers.score_mgr.models import PointsTransaction
from apps.managers.team_mgr.models import Post
from apps.utils.utils import media_file_path
from apps.widgets.badges import badges
from apps.widgets.notifications.models import UserNotification
from apps.managers.cache_mgr import cache_mgr
from apps.widgets.smartgrid import NOSHOW_PENALTY_DAYS, SETUP_WIZARD_ACTIVITY
from django.core.validators import MaxValueValidator

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


class TextPromptQuestion(models.Model):
    """Represents questions that can be asked of users in order to verify participation
    in activities."""

    action = models.ForeignKey("Action")
    question = models.TextField(help_text="The question text.")
    answer = models.CharField(max_length=255,
                              help_text="The answer of question (max 255 characters).",
                              null=True, blank=True)

    def __unicode__(self):
        return "Question: '%s' Answer: '%s'" % (self.question, self.answer)


class QuestionChoice(models.Model):
    """Represents questions's multiple choice"""

    question = models.ForeignKey("TextPromptQuestion")
    action = models.ForeignKey("Action")
    choice = models.CharField(max_length=255,
                              help_text="The choice of question (max 255 characters).")

    def __unicode__(self):
        return self.choice


class Level(models.Model):
    """Associates the actions to different levels."""
    name = models.CharField(max_length=50,
                            help_text="The name of the level.")
    slug = models.SlugField(help_text="Automatically generated if left blank.",
                            null=True)
    priority = models.IntegerField(
        default=1,
        help_text="Levels with lower values (higher priority) will be listed first."
    )
    unlock_condition = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="if the condition is True, the level will be unlocked. " +
                   settings.PREDICATE_DOC_TEXT)
    unlock_condition_text = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="The description of the unlock condition.")
    admin_tool_tip = "Smart Grid Level"

    def __unicode__(self):
        return self.name

    class Meta:
        """Meta"""
        ordering = ("priority",)

    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        super(Level, self).save(args, kwargs)
        cache_mgr.clear()


class ColumnName(models.Model):
    """ColumnNames are used to group actions in the Smart Grid."""
    name = models.CharField(max_length=255,
                            help_text="The name of the column (max 255 characters).")
    slug = models.SlugField(help_text="Automatically generated if left blank.",
                            null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        super(ColumnName, self).save(args, kwargs)
        cache_mgr.clear()


class Action(models.Model):
    """Activity Base class."""
    TYPE_CHOICES = (
        ('activity', 'Activity'),
        ('commitment', 'Commitment'),
        ('event', 'Event'),
        ('filler', 'Filler'),
        )
    RESOURCE_CHOICES = (
        ('energy', 'Energy'),
        ('water', 'Water'),
        ('waste', 'Waste'),
    )

    VIDEO_SOURCE_CHOICES = (
        ('youtube', 'youtube'),
    )

    users = models.ManyToManyField(User, through="ActionMember")

    name = models.CharField(
        max_length=20,
        help_text="The name of the action.")
    slug = models.SlugField(
        help_text="A unique identifier of the action. Automatically generated if left blank.",
        unique=True,
        )
    title = models.CharField(
        max_length=200,
        help_text="The title of the action.")
    image = models.ImageField(
        max_length=255, blank=True, null=True,
        upload_to=media_file_path(_MEDIA_LOCATION_ACTION),
        help_text="Uploaded image for the activity. This will appear under the title when "
                  "the action content is displayed.")
    video_id = models.CharField(
        null=True, blank=True,
        max_length=200,
        help_text="The id of the video (optional). Currently only YouTube video is supported. "
                  "This is the unique id of the video as identified by the YouTube video url.")
    video_source = models.CharField(
        null=True, blank=True,
        max_length=20,
        choices=VIDEO_SOURCE_CHOICES,
        help_text="The source of the video."
    )
    embedded_widget = models.CharField(
        null=True, blank=True,
        max_length=50,
        help_text="The name of the embedded widget (optional)."
    )
    description = models.TextField(
        help_text="The discription of the action. " + settings.MARKDOWN_TEXT
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="The type of the actions."
    )
    pub_date = models.DateField(
        default=datetime.date.today(),
        verbose_name="Publication date",
        help_text="Date from which the action will be available for users."
    )
    expire_date = models.DateField(
        null=True, blank=True,
        verbose_name="Expiration date",
        help_text="Date after which the action will be marked as expired."
    )
    unlock_condition = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="if the condition is True, the action will be unlocked. " +
                  settings.PREDICATE_DOC_TEXT)
    unlock_condition_text = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="The description of the unlock condition. It will be displayed to players when "
                  "the lock icon is clicked.")
    related_resource = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=RESOURCE_CHOICES,
        help_text="The resource type this action related.")
    social_bonus = models.IntegerField(
        default=0,
        help_text="Social bonus point value.")
    point_value = models.IntegerField(
        default=0,
        help_text="The point value to be awarded."
    )

    def get_classname(self):
        """Returns the classname."""
        return self._meta.module_name

    def __unicode__(self):
        return "%s: %s" % (self.type.capitalize(), self.title)

    def get_action(self, action_type):
        """Returns the concrete action object by type."""
        return action_type.objects.get(action_ptr=self.pk)

    def admin_link(self):
        """returns the hardcoded link to edit the action."""
        return "<a href='/challenge_setting_admin/smartgrid/%s/%s/'>%s</a>" % \
            (self.type, self.pk, self.name)


class Activity(Action):
    """Activities involve verifiable actions that users commit to.  These actions can be
   verified by asking questions or posting an image attachment that verifies the user did
   the activity."""

    CONFIRM_CHOICES = (
        ('text', 'Question and Answer'),
        ('image', 'Image Upload'),
        ('free', 'Free Response'),
        ('free_image', 'Free Response and Image Upload'),
        )

    expected_duration = models.IntegerField(
        verbose_name="Expected activity duration",
        help_text="Time (in minutes) that the activity is expected to take."
    )
    point_range_start = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum number of points possible for a variable point activity."
    )
    point_range_end = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of points possible for a variable point activity."
    )
    confirm_type = models.CharField(
        max_length=20,
        choices=CONFIRM_CHOICES,
        default="text",
        help_text="If the type is 'Question and Answer', please provide the "
                  "'Text prompt questions' section below.",
        verbose_name="Confirmation Type"
    )
    confirm_prompt = models.TextField(
        blank=True,
        verbose_name="Confirmation prompt",
        help_text=settings.MARKDOWN_TEXT
    )
    admin_note = models.TextField(
        null=True, blank=True,
        help_text="Notes for admins when approving this activity. " + settings.MARKDOWN_TEXT)

    def is_active(self):
        """Determines if the activity is available for users to participate."""
        return self.is_active_for_date(datetime.date.today())

    def is_active_for_date(self, date):
        """Determines if the activity is available for user participation at the given date."""
        pub_result = date - self.pub_date
        expire_result = self.expire_date - date
        if pub_result.days < 0 or expire_result.days < 0:
            return False
        return True

    def pick_question(self, user_id):
        """Choose a random question to present to a user."""
        if self.confirm_type != "text":
            return None

        questions = TextPromptQuestion.objects.filter(action=self)
        if questions:
            return questions[user_id % len(questions)]
        else:
            return None

    class Meta:
        """meta"""
        verbose_name_plural = "Activities"


class Commitment(Action):
    """Commitments involve non-verifiable actions that a user can commit to.
    Typically, they will be worth fewer points than activities."""
    commitment_length = models.IntegerField(
        default=5,
        help_text="Duration of commitment, in days."
    )


class Event(Action):
    """Events will be verified by confirmation code. It includes events and excursions."""

    expected_duration = models.IntegerField(
        verbose_name="Expected activity duration",
        help_text="Time (in minutes) that the activity is expected to take."
    )
    event_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date and time of the event",
        help_text="Required for events."
    )
    event_location = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name="Event Location",
        help_text="Location of the event"
    )
    event_max_seat = models.IntegerField(
        default=1000,
        help_text="Specify the max number of seats available to the event."
    )

    def is_event_completed(self):
        """Determines if the event is completed."""
        if self.event_date:
            result = datetime.datetime.today() - self.event_date
            if result.days >= 0 and result.seconds >= 0:
                return True
        return False


class Filler(Action):
    """Filler action. It is always locked"""
    pass


class ColumnGrid(models.Model):
    """Defines the ColumnName positions in the Smart Grid."""
    level = models.ForeignKey(Level,
        help_text="The level of the action."
    )
    column = models.IntegerField(
        default=1,
        help_text="The column of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    name = models.ForeignKey(ColumnName,
                             help_text="The ColumnName in this location.")


class Grid(models.Model):
    """Defines the Smart Grid, holds the level, column, row, and Action."""
    level = models.ForeignKey(Level,
        help_text="The level of the action."
    )
    column = models.IntegerField(
        default=1,
        help_text="The column of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    row = models.IntegerField(
        default=1,
        help_text="The row of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    action = models.ForeignKey(Action,
                               help_text="The Action in this location.")

    class Meta:
        """Meta"""
        ordering = ("level", "column", "row")

    def __unicode__(self):
        return "%s: [%s, x=%s, y=%s]" % (self.action, self.level, self.column, self.row)


class ActionMember(models.Model):
    """Represents the join between commitments and users.  Has fields for
    commenting on a commitment and whether or not the commitment is currently
    active."""

    STATUS_TYPES = (
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        )

    user = models.ForeignKey(User)
    action = models.ForeignKey(Action)
    question = models.ForeignKey(TextPromptQuestion, null=True, blank=True)
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
            super(ActionMember, self).save(args, kwargs)
            return

        if self.approval_status == u"rejected":
            self.award_date = None
            super(ActionMember, self).save(args, kwargs)

            self._handle_activity_notification(self.approval_status)
        else:
            if self.approval_status == u"pending":
                # Mark pending items as submitted.

                self.submission_date = datetime.datetime.today()

                if self.action.type == "commitment" and not self.completion_date:
                    self.completion_date = self.submission_date + \
                        datetime.timedelta(days=self.action.commitment.commitment_length)

                super(ActionMember, self).save(args, kwargs)

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
                        super(ActionMember, self).save(args, kwargs)
                        self._award_possible_reverse_penalty_points()
                else:
                    # always make sure the submission_date is set
                    self.submission_date = self.award_date

                # must save before awarding point due to the generic foreign key relation
                super(ActionMember, self).save(args, kwargs)
                self._award_points()

                self.social_bonus_awarded = self._award_possible_social_bonus()
                if self.social_bonus_awarded:
                    super(ActionMember, self).save(args, kwargs)

                self._handle_activity_notification(self.approval_status)

        self.post_to_wall()
        self.invalidate_cache()
        badges.award_possible_badges(self.user.profile, "smartgrid")

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
            ref_members = ActionMember.objects.filter(action=self.action,
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
            ref_members = ActionMember.objects.filter(user__email=self.social_email,
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
        """if NOSHOW_PENALTY_DAYS past and has submission_date (signed up),
        return true as noshow penalty."""
        event = self.action.event
        diff = datetime.date.today() - event.event_date.date()
        if diff.days > NOSHOW_PENALTY_DAYS and self.submission_date:
            return True
        else:
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
            challenge = challenge_mgr.get_challenge()
            message += " You can still get points by clicking on the link and trying again."
            UserNotification.create_error_notification(self.user, message, display_alert=True,
                                                       content_object=self)

            # only send out email notification for rejected action
            subject = "[%s] Your response to '%s' was %s" % (
                challenge.name, self.action.title, status_nicely)

            message = render_to_string("email/rejected_activity.txt", {
                "object": self,
                "COMPETITION_NAME": challenge.name,
                "domain": challenge.domain,
                "status_nicely": status_nicely,
                })
            html_message = render_to_string("email/rejected_activity.html", {
                "object": self,
                "COMPETITION_NAME": challenge.name,
                "domain": challenge.domain,
                "status_nicely": status_nicely,
                })

            UserNotification.create_email_notification(
                self.user.email, subject, message, html_message)
        else:
            points = self.points_awarded if self.points_awarded else self.action.point_value
            message += " You earned %d points!" % points

            UserNotification.create_success_notification(self.user, message, display_alert=True,
                                                         content_object=self)

            # if admin approve an activity (action_type==activity),
            # check to the submission queue is empty,
            # if so, remove the admin reminder object.
            if self.action.type == "activity":
                submission_count = ActionMember.objects.filter(
                    action__type="activity",
                    approval_status="pending").count()
                if not submission_count:
                    try:
                        admin = User.objects.get(username=settings.ADMIN_USER)
                        action = Action.objects.get(slug=SETUP_WIZARD_ACTIVITY)
                        EmailReminder.objects.filter(user=admin, action=action).delete()
                    except ObjectDoesNotExist:
                        pass

    def post_to_wall(self):
        """post to team wall as system post."""
        team = self.user.profile.team
        if team:
            if self.approval_status == "approved":
                # User completed the commitment
                message = "has completed the %s \"%s\"." % (self.action.type,
                                                            self.action.title,)
            else:
                # User is adding the commitment.
                message = "is participating in the %s \"%s\"." % (self.action.type,
                                                                  self.action.title,)

            post = Post(user=self.user,
                        team=team,
                        text=message,
                        style_class="system_post")
            post.save()

    def invalidate_cache(self):
        """Invalidate the categories cache."""
        username = self.user.username
        cache_mgr.delete('smartgrid-levels-%s' % username)
        cache_mgr.delete('smartgrid-completed-%s' % username)
        cache_mgr.delete('user_events-%s' % username)
        cache_mgr.delete('get_quests-%s' % username)
        cache_mgr.delete('golow_actions-%s' % username)

        team = self.user.profile.team
        if team:
            cache_mgr.invalidate_template_cache("team_avatar", self.action.id, team.id)
        cache_mgr.invalidate_template_cache("my_commitments", username)
        cache_mgr.invalidate_template_cache("my_achievements", username)
        cache_mgr.invalidate_template_cache("smartgrid", username)

    def delete(self, using=None):
        """Custom delete method to remove the points for completed action."""
        profile = self.user.profile

        if self.approval_status == "approved":
            # remove all related point transaction
            profile.remove_related_points(self)
        else:
            # drop any possible signup transaction
            self._drop_signup_points()

        if profile.team:
            message = "is no longer participating in the %s \"%s\"." % (
                self.action.type, self.action.title,)
            post = Post(user=self.user,
                        team=profile.team,
                        text=message,
                        style_class="system_post")
            post.save()

        self.invalidate_cache()

        super(ActionMember, self).delete()


class Reminder(models.Model):
    """
    Sends a reminder for an activity to a user.  Reminders are queued up and sent later.
    """
    REMINDER_CHOICES = (
        ("email", "Email"),
        ("text", "Text"),
        )

    user = models.ForeignKey(User, editable=False)
    action = models.ForeignKey(Action, editable=False)

    send_at = models.DateTimeField(
        help_text="The send time of the reminder."
    )
    sent = models.BooleanField(
        default=False, editable=False,
        help_text="Is reminder sent?")

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True, null=True)

    class Meta:
        """meta"""
        abstract = True
        unique_together = ("user", "action")

    def send(self):
        """send methods that subclass all required to implement."""
        raise NotImplementedError("Reminder subclasses need to implement send.")


class EmailReminder(Reminder):
    """Email Reminder Class"""
    email_address = models.EmailField(
        help_text="The email address."
    )

    def send(self):
        """
        Sends a reminder email to the user.
        """
        if not self.sent:
            challenge = challenge_mgr.get_challenge()
            subject = "[%s] Reminder for %s" % (challenge.name,
                                                self.action.title)
            message = render_to_string("email/activity_reminder.txt", {
                "action": self.action,
                "user": self.user,
                "COMPETITION_NAME": challenge.name,
                "domain": challenge.domain,
                })
            html_message = render_to_string("email/activity_reminder.html", {
                "action": self.action,
                "user": self.user,
                "COMPETITION_NAME": challenge.name,
                "domain": challenge.domain,
                })

            UserNotification.create_email_notification(self.email_address, subject, message,
                html_message)
            self.sent = True
            self.save()


class TextReminder(Reminder):
    """Text Reminder Class"""
    TEXT_CARRIERS = (
        ('att', 'AT&T'),
        ('sprint', 'Sprint'),
        ('tmobile', 'T-Mobile'),
        ('verizon', 'Verizon'),
        ('mobi', 'Mobi PCS'),
        ('virgin', 'Virgin Mobile'),
        ('alltel', "AllTel"),
        )
    TEXT_EMAILS = {
        "att": "txt.att.net",
        "verizon": "vtext.com",
        "tmobile": "tmomail.net",
        "sprint": "messaging.sprintpcs.com",
        "mobi": "mobipcs.net",
        "virgin": "vmobl.com",
        "alltel": "message.alltel.com",
        }
    text_number = PhoneNumberField(
        help_text="The phone number."
    )
    text_carrier = models.CharField(
        max_length=50, choices=TEXT_CARRIERS, null=True, blank=True,
        help_text="The phone carrier.")

    def send(self):
        """
        Sends a reminder text to the user via an email.
        """
        number = self.text_number.replace("-", "")
        email = number + "@" + self.TEXT_EMAILS[self.text_carrier]
        if not self.sent:
            message = render_to_string("email/activity_text_reminder.txt", {
                "activity": self.action,
                "user": self.user,
                })

            UserNotification.create_email_notification(email, "", message)
            self.sent = True
            self.save()


class ConfirmationCode(models.Model):
    """Represents confirmation codes for activities."""
    action = models.ForeignKey(Action)
    code = models.CharField(max_length=50, unique=True, db_index=True,
                            help_text="The confirmation code.")
    is_active = models.BooleanField(default=True, editable=False,
                                    help_text="Is the confirmation code still active?")
    user = models.ForeignKey(User, null=True, blank=True,
                             help_text="The user who claimed the code.")
    create_date = models.DateTimeField(default=datetime.datetime.now(),
                                   verbose_name="Date created",
                                   help_text="Date the code was created.")
    printed_or_distributed = models.BooleanField(default=False, editable=True,
                                help_text="Has the code been printed or distributed.")

    @staticmethod
    def generate_codes_for_activity(event, num_codes):
        """Generates a set of random codes for the activity."""
        values = 'abcdefghijkmnpqrstuvwxyz234789'

        # Use the first non-dash component of the slug.
        components = event.slug.split('-')
        header = components[0]
        # Need to see if there are other codes with this header.
        index = 1
        while ConfirmationCode.objects.filter(code__istartswith=header).exclude(
            action=event).count() > 0 and index < len(components):
            header += components[index]
            index += 1

        header += "-"
        for _ in range(0, num_codes):
            code = ConfirmationCode(action=event, code=header)
            valid = False
            while not valid:
                for value in random.sample(values, 5):
                    code.code += value
                try:
                    # print code.code
                    # Throws exception if the code is a duplicate.
                    code.save()
                    valid = True
                except IntegrityError:
                    # Try again.
                    code.code = header
