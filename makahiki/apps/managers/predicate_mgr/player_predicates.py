"""Predicates providing information about the state of the current player."""
import datetime
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.models import Profile
from apps.widgets.badges.models import BadgeAward
from apps.widgets.resource_goal.models import EnergyGoal
from apps.managers.score_mgr.models import ScoreboardEntry


def allocated_raffle_ticket(user):
    """Returns True if the user has any allocated tickets."""
    return user.raffleticket_set.count() > 0


def badge_awarded(user, badge_slug):
    """Returns True if the badge is awarded to the user."""
    for awarded in BadgeAward.objects.filter(profile=user.profile):
        if awarded.badge.slug == badge_slug:
            return True
    return False


def changed_theme(user):
    """returns True if the user change their theme."""
    theme = user.profile.theme
    if not theme:
        return False
    else:
        return theme != challenge_mgr.get_challenge().theme


def daily_energy_goal_count(user, count):
    """Returns True if the number of consecutively meeting daily energy goal equals to count."""
    team = user.profile.team
    if team:
        goals = EnergyGoal.objects.filter(team=team, goal_status='Below the goal').order_by("date")
        if goals:
            date = goals[0].date
            count = 0
            for goal in goals:
                if (goal.date - date) == datetime.timedelta(days=1):
                    count += 1
                else:
                    count = 0

                if count == 2:
                    return True

                date = goal.date

    return False


def daily_visit_count(user, count):
    """Returns True if the number of the user daily visit equals to count."""
    return user.profile.daily_visit_count >= count


def has_points(user, points):
    """Returns True if the user has more than the specified points."""
    return user.profile.points() >= points


def is_admin(user):
    """Returns True if the user is an admin."""
    return user.is_staff or user.is_superuser


def posted_to_wall(user):
    """Returns True if the user posted to their wall and False otherwise."""
    if user.post_set.filter(style_class="user_post").count() > 0:
        return True
    return False


def referring_count(user, count):
    """Returns True if the user have referred at least [count] new players."""
    return Profile.objects.filter(referring_user=user).count() >= count


def set_profile_pic(user):
    """Returns True if the user posted to their wall and False otherwise."""
    if user.avatar_set.filter(primary=True).count() > 0:
        return True
    return False


def team_member_point_percent(user, points, percent):
    """Returns True if the user's team has at least [percent] members got at least [points]."""
    team = user.profile.team
    if team:
        current_round = challenge_mgr.get_round_name()
        point_count = ScoreboardEntry.objects.filter(profile__team=team,
                                                     points__gte=points,
                                                     round_name=current_round,
                                                     ).count()
        return  point_count * 100 / team.profile_set.count() >= percent
    return False
