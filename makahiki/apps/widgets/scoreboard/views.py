"""Prepares the views for point scoreboard widget."""
import datetime
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr import player_mgr
from apps.managers.team_mgr import team_mgr


def supply(request, page_name):
    """Supply the view_objects content for this widget, which is all the scoreboard data."""

    user = request.user

    team = user.profile.team
    num_results = 10 if page_name != "status" else None
    round_standings = {}

    current_round = challenge_mgr.get_round_name()
    today = datetime.datetime.today()
    rounds = challenge_mgr.get_all_round_info()["rounds"]
    for key in rounds.keys():
        # 1. always display current round
        # 2. if not future round
        #    a. display the round with the "display_scoreboard" flag
        #    b. display in the status page
        if rounds[key]["start"] <= today and \
            (rounds[key]["display_scoreboard"] or page_name == "status"):
            round_standings[key] = {
                #"group_standings": team_mgr.group_points_leaders(num_results, key),
                "team_standings": team_mgr.team_points_leaders(num_results, key),
                "profile_standings": player_mgr.points_leaders(num_results, key),
                #"group_participation": team_mgr.group_active_participation(num_results, key) if \
                #    page_name == "status" else None,
                "team_participation": team_mgr.team_active_participation(num_results, key) if \
                                      page_name == "status" else None,
                "user_team_standings": team.points_leaders(num_results, key) if \
                                       team and page_name != "status" else None,
            }
    """
    # add an overall scoreboard
    round_standings["Overall"] = {
        #"group_standings": team_mgr.group_points_leaders(num_results, "Overall"),
        "team_standings": team_mgr.team_points_leaders(num_results, "Overall"),
        "profile_standings": player_mgr.points_leaders(num_results, "Overall"),
        #"group_participation": team_mgr.group_active_participation(num_results, "Overall") if\
        #    page_name == "status" else None,
        "team_participation": team_mgr.team_active_participation(num_results, "Overall") if \
            page_name == "status" else None,
    }
    """
    count = len(rounds)

    return {
        "profile": user.profile,
        "team": team,
        "current_round": current_round,
        "round_standings": round_standings,
        "no_carousel": page_name == "status",
        "range": count,
        "user": user,
    }


def remote_supply(request, page_name):
    """Supplies data to remote views."""
    return supply(request, page_name)
