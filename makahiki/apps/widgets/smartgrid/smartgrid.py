"""Implements the Smart Grid Game widget."""

import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import  Count
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.widgets.notifications.models import NoticeTemplate, UserNotification
from apps.widgets.smartgrid import NUM_GOLOW_ACTIONS, SETUP_WIZARD_ACTIVITY, NOSHOW_PENALTY_DAYS
from apps.widgets.smartgrid.models import Action, ActionMember, Level, EmailReminder, \
    TextReminder, ColumnGrid, Grid, Activity, Commitment
from apps.widgets.smartgrid.models import Event
from apps.widgets.smartgrid import  MAX_COMMITMENTS
from apps.managers.predicate_mgr import predicate_mgr


def get_setup_activity():
    """Returns the setup activity object."""
    return get_object_or_404(Action, slug=SETUP_WIZARD_ACTIVITY)


def complete_setup_activity(user):
    """complete the setup activity."""

    # error out if we can't find to the activity.
    activity = get_setup_activity()
    members = ActionMember.objects.filter(user=user, action=activity)
    if not members:
        # if points not awarded, do so.
        member = ActionMember(action=activity, user=user)
        member.approval_status = "approved"
        member.save()


def get_action(slug):
    """returns the action object by slug."""
    action = get_object_or_404(Action, slug=slug)
    if action.type == 'activity':
        action = Activity.objects.get(slug=slug)
    elif action.type == 'commitment':
        action = Commitment.objects.get(slug=slug)
    elif action.type == 'event':
        action = Event.objects.get(slug=slug)
    return action


def annotate_action_details(user, action):
    """retrieve the action details for the user."""
    if action.type == "commitment":
        members = ActionMember.objects.filter(user=user, action=action).order_by("-submission_date")

        # calculate the task duration
        action.duration = action.commitment.commitment_length
    else:
        members = ActionMember.objects.filter(user=user, action=action)

        # calculate the task duration
        if action.type == "activity":
            duration = action.activity.expected_duration
        else:  # is event
            if action.type in ("event", "excursion"):
                duration = action.event.expected_duration
            else:
                duration = 0

        hours = duration / 60
        minutes = duration % 60
        action.duration = ""
        if hours > 1:
            action.duration = "%d hours" % hours
        elif hours > 0:
            action.duration = "%d hour" % hours
        if minutes > 0:
            action.duration += " %d minutes" % minutes

    if members:
        action.member = members[0]
        action.is_unlock = True
        action.completed = True
    else:
        action.member = None
        action.is_unlock = is_unlock(user, action)
        for loc in Grid.objects.filter(action=action):
            action.is_unlock = action.is_unlock and is_level_unlock(user, loc.level)
        action.completed = False

    action.availablity = availablity(action)
    return action


def get_action_members(action):
    """returns the members that had done the action."""
    return ActionMember.objects.filter(action=action)


def get_submitted_actions(user):
    """returns the completed action for the user. It is stored as a dict of action slugs and
    its member status."""
    actions = cache_mgr.get_cache('smartgrid-completed-%s' % user.username)
    if actions is None:
        actions = {}
        for member in ActionMember.objects.filter(
            user=user).select_related("action").order_by("-submission_date"):
            slug = member.action.slug
            if  member.action.type != "commitment":
                actions[slug] = {"approval_status": member.approval_status,
                                 }
            elif slug not in actions:
                actions[slug] = {"days_left": member.days_left(),
                                 "award_date": member.award_date,
                                 }
        cache_mgr.set_cache('smartgrid-completed-%s' % user, actions, 1800)
    return actions


def get_levels(user):
    """Returns the list of annotated levels for the given user."""
    levels = []
    submitted_actions = get_submitted_actions(user)
    for level in Level.objects.all():
        level.is_unlock = predicate_mgr.eval_predicates(level.unlock_condition, user)
        level.is_complete = True
        for row in Grid.objects.filter(level=level):
            action = row.action
            if action.slug not in submitted_actions:
                level.is_complete = False
                break
        levels.append(level)
    return levels


def get_level_actions(user):  # pylint: disable=R0914,R0912,R0915
    """Returns the smart grid as defined in the Smart Grid Designer. The
    grid is a list of lists with the format [<Level>, [<ColumnGrid>*],
    [<Grid>*], [active columns], max_column, max_row]"""
    levels = cache_mgr.get_cache('smartgrid-levels-%s' % user.username)
    if levels is None:
        submitted_actions = get_submitted_actions(user)
        levels = []
        for level in Level.objects.all():
            level.is_unlock = predicate_mgr.eval_predicates(level.unlock_condition, user)
            if level.is_unlock:  # only include unlocked levels
                if level.unlock_condition != "True":
                    contents = "%s is unlocked." % level

                    msg_exists = UserNotification.objects.filter(recipient=user,
                                                                 contents=contents).exists()
                    if not msg_exists:
                        obj, created = UserNotification.objects.\
                            get_or_create(recipient=user,
                                          contents=contents,
                                          level=UserNotification.LEVEL_CHOICES[2][0])
                        if created:  # only show the notification if it is new
                            obj.display_alert = True
                            obj.save()
                level_ret = []
                level.is_complete = True
                level_ret.append(level)
                level_ret.append(ColumnGrid.objects.filter(level=level))
#                level_ret.append(Grid.objects.filter(level=level))

                max_column = len(ColumnGrid.objects.filter(level=level))
                max_row = 0
                just_actions = []
                # update each action
                for row in Grid.objects.filter(level=level):
                    action = Action.objects.get(slug=row.action.slug)
                    action.row = row.row
                    if row.row > max_row:
                        max_row = row.row
                    action.column = row.column
                    if row.column > max_column:
                        max_column = row.column
                    if action.slug in submitted_actions:
                        action.member = submitted_actions[action.slug]
                        action.is_unlock = True
                        action.completed = True
                    else:
                        action.is_unlock = is_unlock(user, action)
                        action.completed = False

                    action.availablity = availablity(action)
                    # if there is one action is not completed, set the level to in-completed
                    if not action.completed:
                        level.is_complete = False
                    just_actions.append(action)
                level_ret.append(just_actions)
                columns = []
                for cat in level_ret[1]:
                    if cat.column not in columns:
                        columns.append(cat.column)
                for act in level_ret[2]:
                    if act.column not in columns:
                        columns.append(act.column)
                level_ret.append(columns)
                level_ret.append(max_column)
                level_ret.append(max_row)
                levels.append(level_ret)
            else:
                level_ret = []
                level_ret.append(level)
                level_ret.append([])
                level_ret.append([])
                level_ret.append([])
                level_ret.append(0)
                level_ret.append(0)
                levels.append(level_ret)

        # Cache the levels for 30 minutes (or until they are invalidated)
        cache_mgr.set_cache('smartgrid-levels-%s' % user, levels, 1800)
    return levels  # pylint: enable=R0914,R0912,R0915


def get_smart_grid():
    """Returns the currently defined smart grid."""
    levels = []
    for level in Level.objects.all():
        columns = []
        col_name = None
        for col_grid in ColumnGrid.objects.filter(level=level):
            col_name = col_grid.name
            col_name.task_list = []
            col = col_grid.column
            for act_grid in Grid.objects.filter(level=level, column=col):
                col_name.task_list.append(act_grid.action)
            columns.append(col_name)
        level.col_list = columns
        levels.append(level)
    return levels


def get_smart_grid_action_slugs():
    """Returns the Actions that are currently in the Smart Grid."""
    action_list = []
    for grid in Grid.objects.all():
        slug = grid.action.slug
        if slug not in action_list:
            action_list.append(slug)
    return action_list


def get_popular_actions(action_type, approval_status, num_results=None):
    """Gets the most popular activities in terms of completions."""
    results = Action.objects.filter(actionmember__approval_status=approval_status,
                                 type=action_type,
        ).annotate(completions=Count("actionmember")).order_by("-completions")

    return results[:num_results] if num_results else results


def get_popular_action_submissions(action_type, num_results=None):
    """Gets the most popular activities in terms of completions."""
    results = Action.objects.filter(type=action_type,
        ).annotate(submissions=Count("actionmember")).order_by("-submissions")

    return results[:num_results] if num_results else results


def get_in_progress_members(user):
    """Get the user's incomplete activity members."""
    return user.actionmember_set.filter(
        award_date=None,
    ).order_by("submission_date").select_related("action")


def get_current_commitment_members(user):
    """Get the user's incomplete commitment members."""
    return user.actionmember_set.filter(
        action__type="commitment",
        award_date=None,
    ).order_by("submission_date").select_related("action")


def get_available_golow_actions(user, related_resource):
    """Retrieves only the golow activities that a user can participate in."""

    golow_actions = cache_mgr.get_cache('golow_actions-%s' % user.username)
    if golow_actions is None:
        actions = Action.objects.exclude(
            actionmember__user=user,
        ).filter(
            Q(expire_date__isnull=True) | Q(expire_date__gte=datetime.date.today()),
            related_resource=related_resource,
            pub_date__lte=datetime.date.today(),
        ).order_by("type", "name")

        # pick one activity per type, until reach NUM_GOLOW_ACTIONS
        action_type = None
        golow_actions = []
        for action in actions:
            if action_type == action.type:
                continue

            unlock = is_unlock(user, action)
            if unlock:
                locs = Grid.objects.filter(action=action)
                if locs:
                    for loc in locs:
                        unlock = unlock and is_level_unlock(user, loc.level)
                else:
                    unlock = False
            if unlock:
                golow_actions.append(action)
                action_type = action.type

                if len(golow_actions) == NUM_GOLOW_ACTIONS:
                    break
        cache_mgr.set_cache('golow_actions-%s' % user.username, golow_actions, 1800)

    return golow_actions


def is_level_unlock(user, level):
    """return True if the level is unlock."""
    return level and predicate_mgr.eval_predicates(level.unlock_condition, user)


def afterPublished(user, action_slug):
    """Return true if the event has been published"""
    _ = user
    try:
        action = Action.objects.get(slug=action_slug)
        return action.pub_date <= datetime.date.today()
    except ObjectDoesNotExist:
        return False


def is_unlock(user, action):
    """Returns the unlock status of the user action."""
    levels = cache_mgr.get_cache('smartgrid-levels-%s' % user.username)
    if levels is None:  # not cached, just check
        return eval_unlock(user, action)

    # cached format of levels is [[<Level>, [<ColumnGrid>*],
    #  [<Grid>*], [active columns], max_column, max_row]+]
    for level in levels:
        for a in level[2]:
            if a.id == action.id:
                return a.is_unlock

    return False


def eval_unlock(user, action):
    """Determine the unlock status of a task by dependency expression"""
    predicates = action.unlock_condition
    if not predicates:
        return False

    # after published is the default unlock rule for action
    # if not afterPublished(user, action.slug):
    #    return False

    return predicate_mgr.eval_predicates(predicates, user)


def can_add_commitment(user):
    """Determines if the user can add additional commitments."""
    return ActionMember.objects.filter(user=user, action__type="commitment",
        award_date__isnull=True).count() < MAX_COMMITMENTS


def can_complete_commitment(user, commitment):
    """Determines if the user can complete commitments, assuming there is a pending commitment"""
    pendings = ActionMember.objects.filter(user=user, action=commitment, award_date=None)

    if pendings:
        return pendings[0].days_left() == 0
    else:
        return False


def get_available_events(user):
    """Retrieves only the events that a user can participate in."""

    events = cache_mgr.get_cache('user_events-%s' % user.username)
    if events is None:
        events = Event.objects.filter(
            Q(expire_date__isnull=True) | Q(expire_date__gte=datetime.date.today()),
            pub_date__lte=datetime.date.today(),
            event_date__gte=datetime.date.today(),
        ).order_by("event_date")

        unlock_events = []
        for event in events:
            unlock = is_unlock(user, event) and not event.is_event_completed()
            if unlock:
                for loc in Grid.objects.filter(action=event):
                    unlock = unlock and is_level_unlock(user, loc.level)
            if unlock:
                unlock_events.append(event)

        events = unlock_events
        # Cache the user_event
        cache_mgr.set_cache('user_events-%s' % user.username, events, 1800)

    return events


def get_next_available_event(user):
    """retrieves the next available event as of current time."""

    events = get_available_events(user)
    for event in events:
        if event.event_date > datetime.datetime.today():
            return [event, ]

    return []


def send_reminders():
    """
    Sends out pending reminders if their send_at time has passed.
    """
    reminders = EmailReminder.objects.filter(
        send_at__lte=datetime.datetime.today(),
        sent=False,
    )
    for reminder in reminders:
        print "Sending reminder to %s for '%s'\n" % (
            reminder.email_address, reminder.action.title)
        reminder.send()

    reminders = TextReminder.objects.filter(
        send_at__lte=datetime.datetime.today(),
        sent=False,
    )
    for reminder in reminders:
        print "Sending reminder to %s for '%s'\n" % (
            reminder.text_number, reminder.action.title)
        reminder.send()


def notify_round_started():
    """Notify the user of a start of a round."""
    if not challenge_mgr.in_competition():
        return

    today = datetime.datetime.today()
    current_round = None
    previous_round = None
    all_round_info = challenge_mgr.get_all_round_info()
    rounds = all_round_info["rounds"]
    for key in rounds.keys():
        # We're looking for a round that ends today and another that starts
        # today (or overall)
        start = rounds[key]["start"]
        end = rounds[key]["end"]
        # Check yesterday's round and check for the current round.
        if start < (today - datetime.timedelta(days=1)) < end:
            previous_round = key

        if start < today < end:
            current_round = key

    print 'Previous Round: %s' % previous_round
    print 'Current Round: %s' % current_round

    if current_round and previous_round and current_round != previous_round:
        # only carry over the scoreboard entry if the round don't need to be reset
        if not rounds[current_round]["round_reset"]:
            print "carry over scoreboard entry to new round."
            score_mgr.copy_scoreboard_entry(previous_round, current_round)

    # if there is a gap, previous_round is null, check if it is not out of round
    if current_round and current_round != previous_round and\
       all_round_info["competition_start"] <= today <= all_round_info["competition_end"]:
        print 'Sending out round transition notices.'
        template = NoticeTemplate.objects.get(notice_type="round-transition")
        message = template.render({"PREVIOUS_ROUND": previous_round,
                                   "CURRENT_ROUND": current_round, })
        for user in User.objects.all():
            UserNotification.create_info_notification(user, message,
                                                      display_alert=True,)


def notify_commitment_end():
    """Notify the user of the end of a commitment period and award their points."""
    members = ActionMember.objects.filter(completion_date=datetime.date.today(),
                                          action__type="commitment",
                                          award_date__isnull=True)

    # try and load the notification template.
    template = None
    try:
        template = NoticeTemplate.objects.get(notice_type="commitment-ready")
    except NoticeTemplate.DoesNotExist:
        pass

    for member in members:
        if template:
            message = template.render({"COMMITMENT": member.action})
        else:
            message = "Your commitment <a href='%s'>%s</a> has ended." % (
                reverse("activity_task",
                        args=(member.action.type, member.action.slug)),
                member.action.title)

            message += "You can click on the link to claim your points."

        UserNotification.create_info_notification(member.user, message,
                                                  display_alert=True,
                                                  content_object=member)
        print "created commitment end notification for %s : %s" % (
            member.user, member.action.slug)


def process_rsvp():
    """Process RSVP notification and penalty"""
    noshow_penalty_points = score_mgr.noshow_penalty_points()
    signup_points = score_mgr.signup_points()

    members = ActionMember.objects.filter(
        Q(action__type="event") | Q(action__type="excursion"),
        approval_status="pending")

    # try and load the notification template.
    template_noshow = None
    try:
        template_noshow = NoticeTemplate.objects.get(
            notice_type="event-noshow-penalty")
    except NoticeTemplate.DoesNotExist:
        pass

    template_reminder = None
    try:
        template_reminder = NoticeTemplate.objects.get(
            notice_type="event-post-reminder")
    except NoticeTemplate.DoesNotExist:
        pass

    for member in members:
        action = member.action
        user = member.user
        profile = user.profile

        diff = datetime.date.today() - action.event.event_date.date()
        if diff.days == NOSHOW_PENALTY_DAYS:
            # send out notification to remind the penalty
            if template_reminder:
                message = template_reminder.render({"ACTIVITY": action})
            else:
                message = "Hi %s, <p/> We just wanted to remind you that the "\
                          "%s <a href='http://%s%s'>%s</a> had ended. Please "\
                          "click on the link to claim your points." % (
                    profile.name,
                    action.type.capitalize(),
                    challenge_mgr.get_challenge().domain,
                    reverse("activity_task", args=(action.type, action.slug,)),
                    action.title)
                message += "<p/>Because you signed up for the "\
                           "event, if you do not enter the "\
                           "confirmation code within %d days after the "\
                           "event, a total of %d points (%d point "\
                           "signup bonus plus %d point no-show penalty) will "\
                           "be deducted from your total points. So please "\
                           "enter your confirmation code early to avoid the "\
                           "penalty." % (
                    NOSHOW_PENALTY_DAYS,
                    noshow_penalty_points + signup_points,
                    noshow_penalty_points,
                    signup_points,
                )
                message += "<p/><p/>Kukui Cup Administrators"
            subject = "[Kukui Cup] Reminder to enter your event confirmation code"
            UserNotification.create_email_notification(user.email, subject,
                                                       message, message)
            print "sent post event email reminder to %s for %s" % (
                profile.name, action.title)
        elif diff.days == (NOSHOW_PENALTY_DAYS + 1):
            # the day after the penalty day, process the penalty reduction
            message = "%s: %s (No Show)" % (action.type.capitalize(), action.title)
            profile.remove_points(noshow_penalty_points + signup_points,
                                  datetime.datetime.today() - datetime.timedelta(minutes=1),
                                  message,
                                  member)
            print "removed noshow penalty points from %s for '%s'" % (profile.name, message)

            if template_noshow:
                message = template_noshow.render({"ACTIVITY": action})
            else:
                message = "%d points had been deducted from you, "\
                          "because you signed up but did not enter the "\
                          "confirmation code %d days after the %s <a "\
                          "href='%s'>%s</a>, " % (
                    noshow_penalty_points + signup_points,
                    NOSHOW_PENALTY_DAYS,
                    action.type.capitalize(),
                    reverse("activity_task", args=(action.type, action.slug,)),
                    action.title)
                message += " If you did attend, please click on the link to "\
                           "claim your points and reverse the deduction."

            UserNotification.create_info_notification(user, message,
                                                      display_alert=True,
                                                      content_object=member)
            print "created no-show penalty notification for %s for %s" % (
                profile.name, action.title)


def check_new_submissions():
    """Check the action submission queue and send out notifications to admin when there is new
    submissions in the queue.
    algorithm for queue processing:
      1. on zero to one transition: send email unless email already sent within N minutes.
    """
    submission_count = ActionMember.objects.filter(
        action__type="activity",
        approval_status="pending").count()

    if submission_count:
        try:
            admin = User.objects.get(username=settings.ADMIN_USER)
            action = Action.objects.get(slug=SETUP_WIZARD_ACTIVITY)
            reminder = EmailReminder.objects.filter(user=admin, action=action)
            if not reminder:
                EmailReminder.objects.create(user=admin,
                                             action=action,
                                             send_at=datetime.datetime.today(),
                                             sent=True)

                challenge = challenge_mgr.get_challenge()
                subject = "[%s] %d New Pending Action Submissions" % (challenge.name,
                                                                      submission_count)
                message = "There are %d new pending action submissions as of %s." % (
                    submission_count, datetime.datetime.today())

                if challenge.email_enabled and challenge.contact_email:
                    print "Sending new submission notification to %s" % challenge.contact_email
                    mail = EmailMultiAlternatives(subject, message, challenge.contact_email,
                        [challenge.contact_email, ])
                    mail.send()
        except ObjectDoesNotExist:
            pass


def check_daily_submissions():
    """Check the action submission queue and send out notifications to admin when there are still
    submission in the queue.
    algorithm for queue processing:
      2. every 24 hours: send email with queue size unless queue size is zero.
    """
    submission_count = ActionMember.objects.filter(
        action__type="activity",
        approval_status="pending").count()

    if submission_count:
        challenge = challenge_mgr.get_challenge()
        subject = "[%s] %d Remaining Pending Action Submissions" % (challenge.name,
                                                                    submission_count)
        message = "There are %d remaining pending action submissions as of %s." % (
            submission_count, datetime.datetime.today())

        if challenge.email_enabled and challenge.contact_email:
            print "Sending new submission notification to %s" % challenge.contact_email
            mail = EmailMultiAlternatives(subject, message, challenge.contact_email,
                [challenge.contact_email, ])
            mail.send()


def availablity(action):
    """Returns -1 if the current date is before pub_date, 0 if action is available,
    and 1 if action is expired."""
    today = datetime.date.today()
    ret_val = 0
    if action.pub_date != None:
        if today < action.pub_date:
            # before pub_date
            ret_val = -1

    if action.expire_date != None:
        if today > action.expire_date and ret_val == 0:
            ret_val = 1
    return ret_val
