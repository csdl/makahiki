"""Prepares the views for participation widget."""
import datetime
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.participation import participation


def supply(request, page_name):
    """Supply the view_objects content for this widget, which is participation data."""

    _ = request
    _ = page_name

    round_participation_ranks = {}

    today = datetime.datetime.today()
    rounds = challenge_mgr.get_all_round_info()["rounds"]
    for key in rounds.keys():
        if rounds[key]["start"] <= today and\
            (rounds[key]["display_scoreboard"] or page_name == "status"):
            round_participation_ranks[key] = participation.participation_ranks(key)

    """
    round_participation_ranks["Overall"] = participation.participation_ranks("Overall")
    """

    return {
        "round_participation_ranks": round_participation_ranks,
    }


def remote_supply(request, page_name):
    """Supplies data to remote views."""
    return supply(request, page_name)
