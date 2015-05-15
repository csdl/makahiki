"""Handle the rendering of the energy scoreboard widget."""
import datetime

from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.resource_mgr import resource_mgr
from apps.widgets.resource_goal import resource_goal


def supply(request, page_name):
    """Supply the view_objects content."""
    _ = request
    _ = page_name
    return {}


def resource_supply(request, resource, page_name):
    """Supply the view_objects content.
       :return: team, goals_scoreboard, resource_round_ranks"""

    user = request.user
    team = user.profile.team
    round_resource_ranks = {}
    round_group_resource_ranks = {}
    round_resource_goal_ranks = {}

    today = datetime.datetime.today()

    rounds = challenge_mgr.get_all_round_info()["rounds"]
    for key in rounds.keys():
        if rounds[key]["start"] <= today and\
            (rounds[key]["display_scoreboard"] or page_name == "status"):
            round_resource_ranks[key] = resource_mgr.resource_ranks(resource, key)
            round_group_resource_ranks[key] = resource_mgr.group_resource_ranks(resource, key)
            round_resource_goal_ranks[key] = resource_goal.resource_goal_ranks(resource, key)

    """
    round_resource_ranks["Overall"] = resource_mgr.resource_ranks(resource, "Overall")
    round_group_resource_ranks["Overall"] = resource_mgr.group_resource_ranks(resource, "Overall")
    round_resource_goal_ranks["Overall"] = resource_goal.resource_goal_ranks(resource, "Overall")
    """

    resource_setting = resource_mgr.get_resource_setting(resource)
    return {
        "profile": user.profile,
        "team": team,
        "resource": resource_setting,
        "round_resource_goal_ranks": round_resource_goal_ranks,
        "round_resource_ranks": round_resource_ranks,
        "round_group_resource_ranks": round_group_resource_ranks,
        }
