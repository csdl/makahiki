"""Handle rendering of energy goal widget."""
import datetime
from apps.managers.cache_mgr import cache_mgr

from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.resource_mgr import resource_mgr
from apps.widgets.resource_goal import resource_goal
from apps.widgets.smartgrid import smartgrid
from apps.utils import utils


def supply(request, page_name):
    """Base view supply is not used. The child widget view supply should call resource_supply."""
    _ = request
    _ = page_name
    return {}


def resource_supply(request, page_name):
    """Supply the view_objects content for this widget."""
    user = request.user
    team = user.profile.team
    golow_activities = smartgrid.get_available_golow_actions(user, page_name)
    hourly_goal = None
    daily_goal = None
    goal_settings = None
    if team:
        goal_settings = resource_goal.team_goal_settings(team, page_name)
        if not goal_settings.manual_entry and not "calendar_view" in request.GET:
            hourly_goal = get_hourly_goal_data(team, page_name)
        else:
            daily_goal = get_daily_goal_data(team, page_name)

    resource_setting = resource_mgr.get_resource_setting(page_name)

    return {
        "golow_activities": golow_activities,
        "hourly_goal": hourly_goal,
        "daily_goal": daily_goal,
        "resource": resource_setting,
        "goal_settings": goal_settings,
        }


def get_hourly_goal_data(team, resource):
    """:return: the energy goal data for the user's team."""

    hourly_goal = cache_mgr.get_cache("hgoal-%s-%d" % (resource, team.id))
    if hourly_goal is None:
        date = datetime.datetime.today()
        hourly_goal = {"resource": resource}
        if resource_mgr.is_blackout(date):
            hourly_goal.update({"is_blackout": True})
        else:
            resource_setting = resource_mgr.get_resource_setting(resource)
            unit = resource_setting.unit
            rate = resource_setting.conversion_rate

            usage_data = resource_mgr.team_resource_data(date=date.date(),
                                                         team=team,
                                                         resource=resource)
            if usage_data:
                actual_usage = utils.format_usage(usage_data.usage, rate)

                goal_settings = resource_goal.team_goal_settings(team, resource)
                goal_percent = resource_goal.get_goal_percent(date, team, resource, goal_settings)

                baseline = resource_goal.team_hourly_resource_baseline(
                    resource, team, usage_data.date, usage_data.time)
                goal_usage = utils.format_usage(baseline * (100 - goal_percent) / 100, rate)
                warning_usage = utils.format_usage(baseline * (100 - goal_percent / 2) / 100, rate)
                actual_diff = abs(actual_usage - goal_usage)

                hourly_goal.update({"goal_usage": goal_usage,
                    "warning_usage": warning_usage,
                    "actual_usage": actual_usage,
                    "actual_diff": actual_diff,
                    "updated_at": datetime.datetime.combine(date=usage_data.date,
                                                            time=usage_data.time),
                    "unit": unit,
                   })
            else:
                hourly_goal.update({"no_data": True})

        cache_mgr.set_cache("hgoal-%s-%d" % (resource, team.id), hourly_goal, 600)

    return hourly_goal


def get_daily_goal_data(team, resource):
    """:return: the daily energy goal data."""

    round_info = challenge_mgr.get_round_info()
    if not round_info:
        return None

    today = datetime.date.today()
    start = round_info["start"].date()
    end = round_info["end"].date()
    delta = (end - start).days + 1
    data_table = []
    for day in range(0, delta):
        date = start + datetime.timedelta(days=day)
        goal_info = {"date": date, "resource": resource}

        if day == 0:
            # cal and store the filler_days in the first day goal_info
            goal_info["filler_days"] = range(0, date.weekday())

        if day == (delta - 1):
            # cal and store the filler_days in the last day goal_info
            goal_info["filler_days"] = range(0, 6 - date.weekday())

        if date <= today:
            if date == datetime.date.today():
                goal_info["is_today"] = True

            if resource_mgr.is_blackout(date):
                # the game is disabled for the blackout dates
                goal_info["goal_status"] = "Not available"
                goal_info["verbose_info"] = "Game disabled for today"
            else:
                _set_goal_info(goal_info, resource, team, date)

        data_table.append(goal_info)

    return data_table


def _set_goal_info(goal_info, resource, team, date):
    """set the goal info."""
    resource_setting = resource_mgr.get_resource_setting(resource)
    unit = resource_setting.unit
    rate = resource_setting.conversion_rate
    goal_settings = resource_goal.team_goal_settings(team, resource)
    goal = resource_goal.team_goal(date, team, resource)
    goal_percent = resource_goal.get_goal_percent(date, team, resource, goal_settings)

    if goal:
        goal_info["goal_status"] = goal.goal_status
        if goal.actual_usage:
            goal_info["goal_info"] = "usage:<br/>%d %s" % (
                utils.format_usage(goal.actual_usage, rate), unit)
        elif goal.goal_usage:
            goal_info["goal_info"] = "goal:%d %s<br/>(reduce %d%%)" % (
                utils.format_usage(goal.goal_usage, rate), unit, goal_percent)
    else:
        goal_info["goal_status"] = "Unknown"

    if goal_info["goal_status"] == "Not available":
        goal_info["verbose_info"] = "Game disabled for today because baseline data " \
                                    "not available."
    elif goal_info["goal_status"] == "Unknown":
        if date == datetime.date.today():
            # if there is baseline, display the expected goal,
            # otherwise, display disabled with no baseline, as unavailable
            baseline = resource_goal.team_daily_resource_baseline(
                date, team, resource)
            if baseline:
                goal_usage = baseline * (100 - goal_percent) / 100
                goal_info["goal_status"] = None
                goal_info["goal_info"] = "goal:%d %s<br/>(reduce %d%%)" % (
                    utils.format_usage(goal_usage, rate), unit, goal_percent)
            else:
                goal_info["goal_status"] = "Not available"
                goal_info["verbose_info"] = "Game disabled for today because " \
                                            "baseline data not available."
        else:
            goal_info["goal_status"] = "Not available"
            goal_info["verbose_info"] = "Game disabled for today because usage data " \
                                    "not available."
    else:
        goal_info["verbose_info"] = "%d %s used within the last 24 hours (ends at %s). " \
        "<br/>The goal is %d %s (reduce %d%%)." % (
                utils.format_usage(goal.actual_usage, rate),
                unit,
                goal_settings.manual_entry_time if goal_settings.manual_entry else "midnight",
                utils.format_usage(goal.goal_usage, rate),
                unit,
                goal_percent
            )
