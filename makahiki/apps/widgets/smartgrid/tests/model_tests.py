"""Test"""
import datetime
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.core import mail
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.utils import test_utils

from apps.widgets.smartgrid.models import  EmailReminder, TextReminder, \
                                           ActionMember, Commitment
from apps.widgets.notifications.models import UserNotification
from apps.widgets.smartgrid import smartgrid


class ActivitiesTest(TransactionTestCase):
    """Test Activity"""
    def setUp(self):
        """Generate test user and activity. Set the competition settings to the
        current date for testing."""
        challenge_mgr.init()
        self.user = User.objects.create_user('user', 'user@test.com')
        self.user.save()
        self.activity = test_utils.create_activity()
        self.event = test_utils.create_event()

        self.current_round = "Round 1"

        test_utils.set_competition_round()

    def testActivityLog(self):
        """
        Test that regular activities create the appropriate log.
        """
        member = ActionMember(user=self.user, action=self.activity, approval_status='approved')
        member.save()

        # Check the points log for this user.
        log = self.user.pointstransaction_set.all()[0]
        self.assertTrue(log.message.startswith(self.activity.type.capitalize()))

    def testPopularActivities(self):
        """Check which activity is the most popular."""
        activity_member = ActionMember(user=self.user, action=self.activity)
        activity_member.approval_status = "approved"
        activity_member.save()

        activities = smartgrid.get_popular_actions("activity", "approved")
        self.assertEqual(activities[0].title, self.activity.title)

    def testGetEvents(self):
        """Verify that get_available_events does retrieve events."""
        events = smartgrid.get_available_events(self.user)

        if self.event.id != events[0].id:
            self.fail("Event is not listed in the events list.")

    def testApproveAddsPoints(self):
        """Test for verifying that approving a user awards them points."""
        points = self.user.profile.points()

        # Setup to check round points.
        (entry, _) = self.user.profile.scoreboardentry_set.get_or_create(
            round_name=self.current_round)
        round_points = entry.points
        round_last_awarded = entry.last_awarded_submission

        activity_points = self.activity.point_value

        activity_member = ActionMember(user=self.user, action=self.activity)
        activity_member.save()

        # Verify that nothing has changed.
        self.assertEqual(points, self.user.profile.points())
        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        self.assertEqual(round_points, entry.points)
        self.assertEqual(round_last_awarded, entry.last_awarded_submission)

        activity_member.approval_status = "approved"
        activity_member.save()

        # Verify overall score changed.
        new_points = self.user.profile.points()
        self.assertEqual(new_points - points, activity_points)

        # Verify round score changed.
        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        self.assertEqual(round_points + activity_points, entry.points)
        self.assertTrue(abs(
            activity_member.submission_date - entry.last_awarded_submission) < datetime.timedelta(
            minutes=1))

    def testRejectThenApprove(self):
        """Test that Reject then approve a user removes their points."""
        points = self.user.profile.points()

        activity_member = ActionMember(user=self.user, action=self.activity,
            submission_date=datetime.datetime.today())

        activity_member.approval_status = "rejected"
        activity_member.save()
        self.assertEqual(len(mail.outbox), 1, "Check that the rejection sent an email.")
        self.assertTrue(activity_member.award_date is None)
        self.assertTrue(self.user.profile.last_awarded_submission() is None)

        activity_member.approval_status = "approved"
        activity_member.save()
        new_points = self.user.profile.points()

        self.assertEqual(points + activity_member.points_awarded, new_points)

    def testDeleteRemovesPoints(self):
        """Test that deleting an approved ActionMember removes their points."""

        points = self.user.profile.points()

        # Setup to check round points.
        (entry, _) = self.user.profile.scoreboardentry_set.get_or_create(
            round_name=self.current_round)
        round_points = entry.points

        activity_member = ActionMember(user=self.user, action=self.activity)
        activity_member.approval_status = "approved"
        activity_member.save()
        award_date = activity_member.award_date

        activity_member.delete()
        new_points = self.user.profile.points()

        self.assertEqual(points, new_points)
        self.assertTrue(self.user.profile.last_awarded_submission() is None)

        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        self.assertEqual(round_points, entry.points)
        self.assertTrue(
            entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)

    def testRejectionNotifications(self):
        """
        Test that notifications are created by rejections and
        are marked as read when the member changes back to pending.
        """
        notifications = UserNotification.objects.count()
        activity_member = ActionMember(user=self.user, action=self.activity,
            submission_date=datetime.datetime.today())
        activity_member.approval_status = "rejected"
        activity_member.submission_date = datetime.datetime.today()
        activity_member.save()

        self.assertEqual(UserNotification.objects.count(), notifications + 1,
            "New notification should have been created.")
        notice = activity_member.notifications.all()[0]
        self.assertTrue(notice.unread, "Notification should be unread.")


class CommitmentsUnitTestCase(TransactionTestCase):
    """Commitment Test."""
    def setUp(self):
        """Create test user and commitment. Set the competition settings to the current
        date for testing."""
        self.user = User(username="test_user", password="changeme")
        self.user.save()
        self.commitment = Commitment(
            title="Test commitment",
            name="Test",
            slug="test",
            description="A commitment!",
            point_value=10,
            type="commitment",
        )
        self.commitment.save()

        self.current_round = "Round 1"
        test_utils.set_competition_round()

    def testPopularCommitments(self):
        """Tests that we can retrieve the most popular commitments."""
        commitment_member = ActionMember(user=self.user, action=self.commitment)
        commitment_member.award_date = datetime.datetime.today()
        commitment_member.approval_status = "approved"
        commitment_member.save()

        commitments = smartgrid.get_popular_actions("commitment", "approved")
        self.assertEqual(commitments[0].title, self.commitment.title)
        self.assertEqual(commitments[0].completions, 1,
            "Most popular commitment should have one completion.")

    def testCompletionAddsPoints(self):
        """Tests that completing a task adds points."""
        points = self.user.profile.points()

        # Setup to check round points.
        (entry, _) = self.user.profile.scoreboardentry_set.get_or_create(
            round_name=self.current_round)
        round_points = entry.points

        commitment_member = ActionMember(user=self.user, action=self.commitment,
            completion_date=datetime.datetime.today())
        commitment_member.save()

        # Check that the user's signup point.
        self.assertEqual(points + score_mgr.signup_points(), self.user.profile.points())

        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        self.assertEqual(round_points + score_mgr.signup_points(), entry.points)

        commitment_member.award_date = datetime.datetime.today()
        commitment_member.approval_status = "approved"
        commitment_member.save()
        points += commitment_member.action.commitment.point_value
        self.assertEqual(points + score_mgr.signup_points(), self.user.profile.points())
        self.assertEqual(self.user.profile.last_awarded_submission(),
            commitment_member.award_date)

        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        round_points += commitment_member.action.commitment.point_value
        self.assertEqual(round_points + score_mgr.signup_points(), entry.points)
        self.assertTrue(
            abs(entry.last_awarded_submission - commitment_member.award_date) < datetime.timedelta(
                minutes=1))

    def testDeleteRemovesPoints(self):
        """Test that deleting a commitment member after it is completed removes the user's
        points."""
        points = self.user.profile.points()

        # Setup to check round points.
        (entry, _) = self.user.profile.scoreboardentry_set.get_or_create(
            round_name=self.current_round)
        round_points = entry.points

        commitment_member = ActionMember(user=self.user, action=self.commitment,
            completion_date=datetime.datetime.today())
        commitment_member.save()

        commitment_member.award_date = datetime.datetime.today()
        commitment_member.approval_status = "approved"
        commitment_member.save()
        award_date = commitment_member.award_date
        commitment_member.delete()

        # Verify nothing has changed.
        profile = self.user.profile
        self.assertTrue(
            profile.last_awarded_submission() is None or
            profile.last_awarded_submission() < award_date)
        self.assertEqual(points, profile.points())

        entry = self.user.profile.scoreboardentry_set.get(round_name=self.current_round)
        self.assertEqual(round_points, entry.points)
        self.assertTrue(
            entry.last_awarded_submission is None or entry.last_awarded_submission < award_date)


class RemindersUnitTest(TransactionTestCase):
    """Reminder test."""
    def setUp(self):
        """
        Create a test event and a test user.
        """
        self.event = test_utils.create_event()

        self.user = User.objects.create_user("testuser", "test@test.com")

    def testSendEmailReminder(self):
        """Test that we can send an email reminder."""
        reminder = EmailReminder.objects.create(
            user=self.user,
            action=self.event,
            email_address="test@tester.com",
            send_at=datetime.datetime.today(),
        )

        reminder.send()
        sent_mail = mail.outbox[0]
        self.assertTrue("test@tester.com" in sent_mail.to,
            "Email address should be in the recipient list.")
        reminder = self.user.emailreminder_set.get(action=self.event)
        self.assertTrue(reminder.sent, "Reminder should be marked as sent.")

        # Try to send the reminder again.
        mail_count = len(mail.outbox)
        reminder.send()
        self.assertEqual(len(mail.outbox), mail_count, "A duplicate email should not be sent.")

    def testSendAttTextReminder(self):
        """
        Test that we construct the appropriate email address for AT&T customers.
        """
        reminder = TextReminder.objects.create(
            user=self.user,
            action=self.event,
            text_number="808-555-1234",
            text_carrier="att",
            send_at=datetime.datetime.today(),
        )

        reminder.send()
        sent_mail = mail.outbox[0]
        att_email = "8085551234@txt.att.net"
        self.assertTrue(att_email in sent_mail.to,
            "AT&T email address should be in the recipient list.")

        mail_count = len(mail.outbox)
        reminder.send()
        self.assertEqual(len(mail.outbox), mail_count, "A duplicate email should not be sent.")

    def testSendTmobileTextReminder(self):
        """
        Test that we construct the appropriate email address for T-Mobile customers.
        """
        reminder = TextReminder.objects.create(
            user=self.user,
            action=self.event,
            text_number="808-555-1234",
            text_carrier="tmobile",
            send_at=datetime.datetime.today(),
        )

        reminder.send()
        sent_mail = mail.outbox[0]
        tmobile_mail = "8085551234@tmomail.net"
        self.assertTrue(tmobile_mail in sent_mail.to,
            "T-Mobile email address should be in the recipient list.")

    def testSendSprintTextReminder(self):
        """
        Test that we construct the appropriate email address for Sprint customers.
        """
        reminder = TextReminder.objects.create(
            user=self.user,
            action=self.event,
            text_number="808-555-1234",
            text_carrier="sprint",
            send_at=datetime.datetime.today(),
        )

        reminder.send()
        sent_mail = mail.outbox[0]
        sprint_mail = "8085551234@messaging.sprintpcs.com"
        self.assertTrue(sprint_mail in sent_mail.to,
            "Sprint email address should be in the recipient list.")

    def testSendVerizonTextReminder(self):
        """
        Test that we construct the appropriate email address for Verizon customers.
        """
        reminder = TextReminder.objects.create(
            user=self.user,
            action=self.event,
            text_number="808-555-1234",
            text_carrier="verizon",
            send_at=datetime.datetime.today(),
        )

        reminder.send()
        sent_mail = mail.outbox[0]
        tmobile_mail = "8085551234@vtext.com"
        self.assertTrue(tmobile_mail in sent_mail.to,
            "Verizon email address should be in the recipient list.")
