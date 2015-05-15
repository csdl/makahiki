"""Implements the Daily Energy (or Water) Goal Game."""

import datetime
from django.db.models.aggregates import Count, Avg
from django.template.defaultfilters import slugify
import requests
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.resource_mgr import resource_mgr
from apps.managers.resource_mgr.egauge import EGauge
from apps.managers.resource_mgr.wattdepot import Wattdepot
from apps.managers.team_mgr.models import Team
from apps.widgets.resource_goal.models import EnergyGoal, WaterGoal, WaterGoalSetting, \
    EnergyGoalSetting, EnergyBaselineDaily, WaterBaselineDaily, EnergyBaselineHourly, \
    WaterBaselineHourly


def team_goal_settings(team, resource):
    """Returns the goal settings for the given team and resource."""
    if resource == "energy":
        goalsetting = EnergyGoalSetting
    elif resource == "water":
        goalsetting = WaterGoalSetting

    cache_key = "goal_setting-%s-%s" % (resource, slugify(team.name))
    goalsettings = cache_mgr.get_cache(cache_key)
    if goalsettings is None:
        goalsettings = goalsetting.objects.filter(team=team)
        if goalsettings:
            goalsettings = goalsettings[0]
            cache_mgr.set_cache(cache_key, goalsettings, 2592000)
    return goalsettings


def is_manual_entry(team, resource):
    """Returns true if the game uses manual entry for the given team and resource."""
    gs = team_goal_settings(team, resource)
    return gs.manual_entry if gs else None


def get_resource_goal(resource):
    """Return the resource goal object."""
    if resource == "energy":
        return EnergyGoal
    elif resource == "water":
        return WaterGoal
    else:
        return None


def get_resource_storage(name):
    """Returns the resource data storage service by name."""
    if name == "Wattdepot":
        return Wattdepot()
    elif name == "eGauge":
        return EGauge()
    else:
        return None


def team_goal(date, team, resource):
    """Returns the team's goal status for the given resource."""
    goal = get_resource_goal(resource)
    goals = goal.objects.filter(date=date, team=team)
    if goals:
        return goals[0]
    else:
        return None


def _get_baseline_date(date, depth=0):
    """Returns a non-blackout date that is one weeks prior. only look back maximum 3 weeks.
    otherwise, return None."""
    if depth == 3:
        return None

    baseline_date = date - datetime.timedelta(days=7)
    if resource_mgr.is_blackout(baseline_date):
        depth += 1
        return _get_baseline_date(baseline_date, depth)
    else:
        return baseline_date


def _get_resource_baselinedaily(resource):
    """returns the specific resource baselinedaily object."""
    if resource == "energy":
        return EnergyBaselineDaily
    elif resource == "water":
        return WaterBaselineDaily
    else:
        return None


def _get_resource_baselinehourly(resource):
    """returns the specific resource baselinehourly object."""
    if resource == "energy":
        return EnergyBaselineHourly
    elif resource == "water":
        return WaterBaselineHourly
    else:
        return None


def team_daily_resource_baseline(date, team, resource):
    """Returns the baseline usage for the date and resource."""

    daily_baseline = _get_resource_baselinedaily(resource)

    day = date.weekday()
    baselines = daily_baseline.objects.filter(team=team, day=day)
    if baselines:
        return baselines[0].usage
    else:
        return 0


def team_hourly_resource_baseline(resource, team, date, time):
    """Returns the baseline usage for the date and resource."""
    hourly_baseline = _get_resource_baselinehourly(resource)

    day = date.weekday()
    hour = time.hour
    baseline_start = hourly_baseline.objects.filter(team=team, day=day, hour=hour)
    if baseline_start:
        baseline_start = baseline_start[0].usage
    else:
        baseline_start = 0

    hour = hour + 1
    baseline_end = hourly_baseline.objects.filter(team=team, day=day, hour=hour)
    if baseline_end:
        baseline_end = baseline_end[0].usage
    else:
        baseline_end = 0

    # calculate baseline_usage proportionally to the time within the hour
    minute = time.minute if time.minute else 1
    return baseline_start + (baseline_end - baseline_start) * minute / 60


def update_resource_baseline(resource, date, weeks):
    """calculate all team's resource baseline for the specified date and week period.
    if dynamic, always update the baseline,
    if fixed, only update if the baseline does not exist
    """
    session = requests.session()
    for team in Team.objects.all():
        update_team_resource_baseline(resource, session, team, date, weeks)


def update_team_resource_baseline(resource, session, team, date, weeks):
    """calculate the resource baseline from the specified end_date and week period."""

    goal_settings = team_goal_settings(team, resource)

    # daily
    daily_baseline = _get_resource_baselinedaily(resource)
    baseline, is_create = daily_baseline.objects.get_or_create(team=team, day=date.weekday())
    if is_create or (goal_settings and goal_settings.baseline_method == "Dynamic"):
        # if dynamic, always update the baseline,
        # if fixed, only update if the baseline does not exist
        usage = get_resource_baseline_usage(resource, session, team, date, weeks, None)
        baseline.usage = usage
        baseline.save()

    # hourly, only update for real time resource
    if goal_settings and not goal_settings.manual_entry:
        hourly_baseline = _get_resource_baselinehourly(resource)
        for hour in range(1, 25):
            baseline, is_create = hourly_baseline.objects.get_or_create(team=team,
                                                                     day=date.weekday(),
                                                                     hour=hour)
            if is_create or goal_settings.baseline_method == "Dynamic":
                usage = get_resource_baseline_usage(resource, session, team, date, weeks, hour)
                baseline.usage = usage
                baseline.save()


def get_resource_baseline_usage(resource, session, team, end_date, weeks, hour):
    """Returns the daily or hourly energy baseline usage from the history data."""
    total_usage = 0
    count = 0
    for week in range(0, weeks):
        date = end_date - datetime.timedelta(days=(week * 7))
        date = _get_baseline_date(date)
        if date:
            usage = get_history_resource_usage(resource, session, team, date, hour)
        else:
            # can not find a good baseline date
            usage = 0

        if not hour:
            print "=== %s:%d %s baseline prior: %d" % (
                date, hour if hour else 0, team.name, usage)

        if usage:
            total_usage += usage
            count += 1

    if count:
        baseline = total_usage / count
    else:
        baseline = 0

    if not hour:
        print "=== %s:%d %s baseline final: %d" % (
           end_date, hour if hour else 0, team.name, baseline)

    return baseline


def get_history_resource_usage(resource, session, team, date, hour):
    """returns the team's resource usage based on team's goal settings."""
    goal_settings = team_goal_settings(team, resource)

    usage = 0
    if not hour:
        # for daily data, try to get it from resource usage table
        # if not found, get if from ResourceStorage
        usage = resource_mgr.team_resource_usage(date, team, resource)

    if not usage and goal_settings and not goal_settings.manual_entry:
        storage = get_resource_storage(goal_settings.data_storage)
        if goal_settings.wattdepot_source_name:
            team_resource_name = goal_settings.wattdepot_source_name
        else:
            team_resource_name = team.name
        usage = resource_mgr.get_history_resource_data(session, team_resource_name, date, hour,
                                                       storage)

    return usage


def get_goal_percent(date, team, resource, goal_settings):
    """return the current goal percent from the goal settings or previous calculated
    dynamic goal."""

    if goal_settings.baseline_method == "Dynamic":
        # get previous week's goal result and the goal percent
        previous_goal_result = team_goal(date - datetime.timedelta(days=7), team, resource)
        if previous_goal_result and previous_goal_result.current_goal_percent_reduction:
            return previous_goal_result.current_goal_percent_reduction

    # otherwise, use the default
    return goal_settings.goal_percent_reduction


def update_resource_usage(resource, date):
    """Update the latest resource usage from Storage server."""

    session = requests.session()

    for team in Team.objects.all():
        goal_settings = team_goal_settings(team, resource)
        if not goal_settings.manual_entry:
            storage = get_resource_storage(goal_settings.data_storage)
            if goal_settings.wattdepot_source_name:
                team_resource_name = goal_settings.wattdepot_source_name
            else:
                team_resource_name = team.name
            resource_mgr.update_team_resource_usage(resource, session, date, team,
                                                    team_resource_name,
                                                    storage)

    # clear the cache for energy ranking, and RIB where it displays
    round_name = challenge_mgr.get_round_name(date)
    cache_mgr.delete("%s_ranks-%s" % (resource, slugify(round_name)))


def check_resource_goals(resource, date):
    """Check the previous day's resource goal for all teams."""

    # check the previous day's data and goal
    date = date - datetime.timedelta(days=1)
    date = datetime.datetime(date.year, date.month, date.day,
                                   hour=23, minute=59, second=59)

    # do nothing if out of round
    if not challenge_mgr.in_competition(date):
        return 0

    update_resource_usage(resource, date)

    is_awarded = False
    for team in Team.objects.all():
        count = check_team_resource_goal(resource, team, date)
        if count:
            print '%s users in %s are awarded %s points each.' % (
                count,
                team,
                team_goal_settings(team, resource).goal_points)
            is_awarded = True

    if not is_awarded:
        print 'No user are awarded daily goal points.'


def check_team_resource_goal(resource, team, date):
    """Check the daily goal, award points to the team members if the goal is met.
    Returns the number of players in the team that got the award."""
    count = 0
    goal = get_resource_goal(resource)
    goal, _ = goal.objects.get_or_create(team=team, date=date)

    if goal.actual_usage:
        # if there is already actual_usage in the goal, do nothing
        print "=== %s %s goal already checked." % (date, team.name)
        return 0

    goal_settings = team_goal_settings(team, resource)
    goal.current_goal_percent_reduction = get_goal_percent(date, team, resource, goal_settings)

    goal.baseline_usage = team_daily_resource_baseline(date, team, resource)
    goal.goal_usage = goal.baseline_usage * (100 - goal.current_goal_percent_reduction) / 100

    resource_data = resource_mgr.team_resource_data(date, team, resource)
    # check if the manual entry time is within the target time,
    # otherwise can not determine the actual usage
    if resource_data and (not goal_settings.manual_entry or
        goal_settings.manual_entry_time.hour == resource_data.time.hour):
        goal.actual_usage = resource_data.usage
    else:
        goal.actual_usage = 0

    if not goal.actual_usage:
        # if can not determine the actual usage, set the status to unknown
        goal.goal_status = "Unknown"
    elif not goal.baseline_usage:
        # if no baseline, set the status to not available
        goal.goal_status = "Not available"
    else:
        # there are actual and goal usage
        if goal.actual_usage <= goal.goal_usage:
            # if already awarded, do nothing
            if goal.goal_status != "Below the goal":
                goal.goal_status = "Below the goal"

                # record the reduction percentage
                goal.percent_reduction = (goal.goal_usage -
                                          goal.actual_usage) * 100 / goal.goal_usage

                #adjust the dynamimc goal percent.
                #the current goal percent is 1 percent less from the previous day's goal percent
                # unless the previous goal percent is already 1.
                if goal.current_goal_percent_reduction > 1:
                    goal.current_goal_percent_reduction -= 1

                count = _award_goal_points(team, resource, goal_settings.goal_points, goal, date)
        else:
            goal.goal_status = "Over the goal"

    print "=== %s %s actual: %d, goal_usage: %d, reduction: %d, goal: %d" % (
        date, team.name, goal.actual_usage, goal.goal_usage,
        goal.percent_reduction, goal.current_goal_percent_reduction
    )

    goal.save()

    return count


def _award_goal_points(team, resource, goal_points, goal, date):
    """award goal points to team member. It is always award for the end of the day"""

    count = 0
    # Award points to the members of the team.
    for profile in team.profile_set.all():
        if profile.setup_complete:
            award_date = datetime.datetime(date.year, date.month, date.day,
                                           hour=23, minute=59, second=59)
            profile.add_points(goal_points, award_date,
                               "Team %s Goal for %s" % (resource, award_date.date()), goal)
            count += 1

    return count


def resource_goal_ranks(resource, round_name=None):
    """Generate the scoreboard for resource goals."""
    if not challenge_mgr.is_game_enabled("%s Game" % resource.capitalize()):
        return None

    cache_key = "%s_goal_ranks-%s" % (resource, slugify(round_name))
    goal_ranks = cache_mgr.get_cache(cache_key)
    if goal_ranks is None:
        goal_ranks = []
        goal = get_resource_goal(resource)

        start_end = challenge_mgr.get_round_start_end(round_name)
        if start_end is not None:
            start, end = start_end
        else:
            return None

        ranks = goal.objects.filter(
            goal_status="Below the goal",
            date__gte=start,
            date__lte=end).values("team__name").annotate(
                completions=Count("team"),
                average_reduction=Avg("percent_reduction")).order_by(
                    "-completions", "-average_reduction")

        for rank in ranks:
            goal_ranks.append(rank)

        total_count = Team.objects.count()
        if len(goal_ranks) != total_count:
            for t in Team.objects.all():
                # find the team in the goal_ranks
                count = 0
                for goal_rank in goal_ranks:
                    if t.name == goal_rank["team__name"]:
                        break
                    else:
                        count += 1
                if count == len(goal_ranks):
                    # not found
                    rank = {"team__name": t.name,
                            "completions": 0,
                            "average_reduction": 0}
                    goal_ranks.append(rank)

                    if len(goal_ranks) == total_count:
                        break

        cache_mgr.set_cache(cache_key, goal_ranks, 3600 * 24)
    return goal_ranks


def resource_goal_leader(name, round_name=None, place=1):
    """Returns the leader (team name) of the resource use."""
    ranks = resource_goal_ranks(name, round_name)
    if len(ranks) >= place:
        return ranks[place - 1]["team__name"]
    else:
        return None


def resource_goal_rank_info(team, resource):
    """Get the overall rank for the team. Return a dict of the rank number and usage."""
    if team:
        info = {}
        ranks = resource_goal_ranks(resource)
        if ranks:
            for idx, rank in enumerate(ranks):
                if rank["team__name"] == team.name:
                    info["rank"] = idx + 1
                    break

        ranks = resource_mgr.resource_ranks(resource)
        if ranks:
            for idx, rank in enumerate(ranks):
                if rank["team__name"] == team.name:
                    info["usage"] = rank["total"]
                    info["unit"] = resource_mgr.get_resource_setting(resource).unit
                    break
        return info
    else:
        return None
