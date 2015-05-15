"""analysis module."""
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
from apps.managers.log_mgr.models import MakahikiLog
from apps.managers.player_mgr import player_mgr
from apps.managers.player_mgr.models import Profile
from apps.managers.score_mgr.models import PointsTransaction
from apps.managers.team_mgr.models import Team
from apps.widgets.resource_goal.models import EnergyGoal
from apps.widgets.smartgrid.models import ActionMember, Action
from apps.managers.challenge_mgr.models import RoundSetting


MIN_SESSION = 60  # Assume user spends 60 seconds on a single page.


def _output(msg, outfile=None):
    """output the msg to outfile if outfile is specified, otherwise, return the msg."""
    if outfile:
        outfile.write(msg)
        return ""
    else:
        return msg


def energy_goal_timestamps(date_start, date_end, outfile=None):
    """display the timestamps for user points."""
    output = _output('=== energy goal timestamps from %s to %s ===\n' % (
        date_start, date_end), outfile)

    if not date_start:
        output += _output("must specify date_start parameter.", outfile)
        return output

    date_end, date_start = _get_start_end_date(date_end, date_start)

    output += _output("%s,%s,%s\n" % ("timestamp", "team", "energy-goals"
    ), outfile)

    days = (date_end - date_start).days

    for day in range(days):
        for team in Team.objects.all():
            timestamp = date_start + datetime.timedelta(days=day)
            count = EnergyGoal.objects.filter(
                goal_status="Below the goal",
                team=team,
                date__gte=date_start,
                date__lte=timestamp).count()
            output += _output("%s,%s,%d\n" % (timestamp, team, count), outfile)

    return output


def user_point_timestamps(date_start, date_end, outfile=None):
    """display the timestamps for user points."""
    output = _output('=== point timestamps from %s to %s ===\n' % (
        date_start, date_end), outfile)

    if not date_start:
        output += _output("must specify date_start parameter.", outfile)
        return output

    date_end, date_start = _get_start_end_date(date_end, date_start)

    output += _output("%s,%s,%s\n" % ("timestamp", "user", "points"
    ), outfile)

    users = PointsTransaction.objects.filter(
        transaction_date__gte=date_start,
        transaction_date__lt=date_end).values_list("user", flat=True).order_by("user").distinct()

    print "total %d users" % len(users)

    count = 0

    for user_id in users:
        user = User.objects.get(id=user_id)
        if user.is_superuser or user.is_staff:
            continue

        timestamp = date_start
        while timestamp <= date_end:
            points = PointsTransaction.objects.filter(
                user=user,
                transaction_date__gte=date_start,
                transaction_date__lt=timestamp).aggregate(Sum('points'))["points__sum"]
            output += _output("%s,%s,%d\n" % (timestamp, user, points if points else 0), outfile)
            timestamp += datetime.timedelta(hours=1)

        count += 1
        if count % 10 == 0:
            print "process user #%d" % count

    print "process user #%d" % count
    return output


def _get_start_end_date(date_end, date_start):
    """return the start and end date in date object."""

    date_start = datetime.datetime.strptime(date_start, "%Y-%m-%d")
    if not date_end:
        date_end = datetime.datetime.today()
    else:
        date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    return date_end, date_start


def _process_post(log, outfile, output, p):
    """process the post content."""
    partner = None
    if "referrer_email" in log.post_content:
        partner = _get_post_content_value(log.post_content, "referrer_email")
    if "social_email" in log.post_content:
        partner = _get_post_content_value(log.post_content, "social_email")
    if partner:
        user = player_mgr.get_user_by_email(partner)
        if user and user != p.user:
            partner_p = user.profile
            if partner_p.team:
                output += _output(",%s,%s,%s" % (
                    user, partner_p.team.group, _get_profile_room(partner_p)), outfile)
    return output


def user_timestamps(team, date_start, date_end, outfile=None):
    """display the timestamps for user interaction with the site and other players."""
    output = _output('=== user timestamps in team %s from %s to %s ===\n' % (
        team, date_start, date_end), outfile)

    if team:
        try:
            team = Team.objects.get(name=team)
        except ObjectDoesNotExist:
            output += _output("team does not exist.", outfile)
            return output

    if not date_start:
        output += _output("must specify date_start parameter.", outfile)
        return output

    date_end, date_start = _get_start_end_date(date_end, date_start)

    output += _output("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % ("timestamp", "user", "last_name",
                                                           "group", "room",
                                                           "action", "action-url",
                                                           "partner", "partner-group",
                                                           "partner-room"), outfile)

    logs = MakahikiLog.objects.filter(request_time__gte=date_start,
                                      request_time__lt=date_end).order_by("request_time")
    count = 0
    for log in logs:
        if log.remote_user in ("not-login", "AnonymousUser", "admin") or \
                        log.remote_user.find("*") != -1:
            continue

        try:
            p = Profile.objects.get(user__username=log.remote_user)
        except ObjectDoesNotExist:
            continue

        if not p.team or (team and p.team != team):
            continue

        output += _output("%s,%s,%s,%s,%s,%s,%s" % (log.request_time, p.user, p.user.last_name,
                                                    p.team.group, _get_profile_room(p),
                                                    _get_action_type(log.request_url),
                                                    _get_action(log.request_url)), outfile)

        if log.post_content:
            output = _process_post(log, outfile, output, p)
        output += _output("\n", outfile)
        count += 1
        if count % 1000 == 0:
            print _output("process log entry #%d" % count)

    print _output("process log entry #%d" % count)
    return output


def _get_profile_room(profile):
    """get the profile's room from properties."""
    if profile.properties:
        props = profile.properties.split(";")
        room_prop = props[0].split("=")
        if len(room_prop) >= 1:
            return room_prop[1]
    else:
        return None


def _get_post_content_value(post_content, key):
    """get the referral email from the post content."""

    key = "'" + key + "': [u'"
    pos_start = post_content.find(key)
    if pos_start == -1:
        return None
    pos_start += len(key)
    pos_end = post_content.find("']", pos_start)
    return post_content[pos_start:pos_end]


def _get_action(url):
    """return the action short url."""
    return url.split("?")[0]


def _get_action_type(url):
    """return the action type."""
    url = _get_action(url)
    if url.endswith("/login/"):
        return "Login"
    elif url.endswith("/referral/"):
        return "Referral"
    elif url.endswith("/setup/complete/"):
        return "Setup"
    elif url.endswith("/add/"):
        return "Submission"
    elif url.find("/video-") != -1:
        return "Watch video"
    else:
        return "View"


def calculate_action_stats():
    """action stats"""
    output = '=== Action Stats ===\n'

    output += 'action_type,total_actions\n'

    actions = Action.objects.all()  # was only actions in the grid. need to address?

    output += "%s,%d\n" % (
        "activity", actions.filter(type="activity").count()
    )

    output += "%s,%d\n" % (
        "event", actions.filter(type="event").count()
        )
    output += "%s,%d\n" % (
        "excursion", actions.filter(type="excursion").count()
        )

    output += "%s,%d\n" % (
        "commitment", actions.filter(type="commitment").count()
        )

    return output


def calculate_summary_stats():
    """calculate the summary."""
    output = '=== Summary Stats ===\n'

    output += "%s,%d\n" % (
        "Total number of social submission",
        ActionMember.objects.filter(social_email__isnull=True).count()
    )
    output += "%s,%d\n" % (
        "Total number of referrals",
        Profile.objects.filter(referring_user__isnull=False).count()
    )
    return output


def calculate_user_stats():
    """Calculate the user stats."""
    output = '=== User Stats ===\n'

    users = User.objects.filter(is_superuser=False)
    output += 'user id,total seconds spent,total hours spent,total submissions,total points\n'

    for user in users:
        logs = MakahikiLog.objects.filter(remote_user=user.username).order_by(
            'request_time')
        total_time = _user_time_spent(logs)

        total_submission = _user_submissions(user)

        total_point = _user_points(user)

        output += '%d,%d,%.2f,%d,%d\n' % (
            user.id, total_time, total_time / 3600.0,
            total_submission, total_point)
    return output


def calculate_user_summary(user_list):
    """Calculate the user summary."""
    output = '=== Summary for users in list: "%s" ===\n' % user_list

    user_list = user_list.split(",")
    profiles = Profile.objects.filter(name__in=user_list)
    rounds = RoundSetting.objects.all()
    point_types = (
        "Activity", "Commitment", "Event", "Excursion", "Referred", "Super Referred",
        "Mega Referred", "Badge",
        "Set up profile", "Bonus Points", "Team 50% participation",
        "Team 75% participation", "Team energy Goal")
    sub_point_types = ("Provide feedback", "Social Bonus", "Sign up", "No Show")
    output += 'name, email, round, total points, '
    for t in point_types:
        output += "%s, " % t
    for t in sub_point_types:
        output += "%s, " % t
    output += "\n"

    for p in profiles:
        for rd in rounds:

            user = p.user

            # get user points and submissions from_action for each round and action type
            output += "%s, %s, %s, " % (user.first_name + " " + user.last_name,
                                        user.username, rd.name)

            query = PointsTransaction.objects.filter(
                transaction_date__lte=rd.end,
                transaction_date__gte=rd.start,
                user=user)
            total_points = query.aggregate(Sum("points"))["points__sum"]
            total_points = total_points if total_points else 0
            output += '%d, ' % (total_points if total_points else 0)
            all_points = 0
            for t in point_types:
                type_points = query.filter(
                    Q(message__startswith=t) | Q(message__startswith=" " + t)).aggregate(
                        Sum("points"))["points__sum"]
                type_points = type_points if type_points else 0
                all_points += type_points
                output += '%d, ' % (type_points)
            for t in sub_point_types:
                sub_type_points = query.filter(
                    message__contains=t).aggregate(Sum("points"))["points__sum"]
                output += '%d, ' % (sub_type_points if sub_type_points else 0)
            output += "\n"
            # the total_points should be equals to all_points
            if total_points != all_points:
                output += "all points (%d) not added to total points.\n" % all_points

    return output


def _user_submissions(user):
    """
    user submissions.
    """
    return ActionMember.objects.filter(user=user).count()


def _user_points(user):
    """user points."""
    return user.profile.points()


def _user_time_spent(logs, start_date=None):
    """ Iterate over the logs and track previous time and time spent."""
    query = logs
    if start_date:
        query = query.filter(request_time__gt=start_date)

    if query.count() > 0:
        prev = query[0].request_time
        cur_session = total = 0
        for log in query[1:]:
            current = log.request_time
            diff = current - prev
            # Start a new interval if 30 minutes have passed.
            if diff.total_seconds() > (60 * 30):
                if cur_session == 0:
                    total += MIN_SESSION
                else:
                    total += cur_session
                cur_session = 0
            else:
                cur_session += diff.total_seconds()

            prev = current

        # Append any session that was in progress.
        total += cur_session
        return total

    return 0
