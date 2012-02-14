import datetime
import simplejson as json

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Max

from managers.base_mgr import get_team_label
from managers.player_mgr.models import Profile, ScoreboardEntry
from managers.team_mgr.models import Team

# Default number of individuals to retrieve standings for when tracking across all dorms.
MAX_INDIVIDUAL_STANDINGS = 10

class StandingsException(Exception):
    def __init__(self, value):
        self.value = value
        super(StandingsException, self).__init__(value)

    def __str__(self):
        return repr(self.value)


def _compare_rounds(a, b):
    """Used to sort the competition rounds."""
    a_start = datetime.datetime.strptime(settings.COMPETITION_ROUNDS[a]["start"]
        , "%Y-%m-%d")
    b_start = datetime.datetime.strptime(settings.COMPETITION_ROUNDS[b]["start"]
        , "%Y-%m-%d")

    return cmp(a_start, b_start)


def get_all_standings(dorm=None, grouping="team",
                      count=MAX_INDIVIDUAL_STANDINGS):
    """Retrieves standings across all teams for all rounds. Can be grouped by team or by individual."""

    standings = []
    keys = settings.COMPETITION_ROUNDS.keys()
    keys.sort(_compare_rounds)

    for round_name in keys:
        if grouping == "team":
            standings.append(
                get_team_standings(dorm=dorm, round_name=round_name, ))
        else:
            standings.append(
                get_individual_standings(dorm=dorm, round_name=round_name,
                    count=count))

    # Append overall standings.
    if grouping == "team":
        standings.append(get_team_standings(dorm=dorm, ))
    else:
        standings.append(get_individual_standings(dorm=dorm, count=count))

    return standings


def get_individual_standings(dorm=None, round_name=None,
                             count=MAX_INDIVIDUAL_STANDINGS):
    """Retrieves standings across all teams for individual users."""

    team_label = get_team_label()
    title = team_label.capitalize() + " vs. " + team_label.capitalize() + ": "

    # Build up the query set.
    profiles = Profile.objects
    if dorm:
        profiles = profiles.filter(team__dorm=dorm)
        title = "%s: " % dorm.name

    if round_name:
        profiles = profiles.filter(scoreboardentry__round_name=round_name).annotate(
            total_points=Sum("scoreboardentry__points"),
            last_awarded=Max("scoreboardentry__last_awarded_submission")
        ).order_by("-total_points", "-last_awarded")[:count]
        title += round_name
    else:
        profiles = profiles.annotate(
            total_points=Sum("points"),
            last_awarded=Max("last_awarded_submission")
        ).order_by("-total_points", "-last_awarded")[:count]
        title += "Overall"

    # Construct the standings info dictionary.
    info = []
    for i, profile in enumerate(profiles):
        if profile.first_name and profile.last_name:
            initials = profile.first_name[0] + profile.last_name[0]
        else:
            initials = profile.name[0]

        label = ""
        if profile.team:
            label = "%s: %s %s (%s)" % (
                profile.team.dorm.name,
                team_label,
                profile.team.number,
                initials,
                )

        info.append({
            "points": profile.total_points,
            "rank": i + 1,
            "label": label,
            })

    return json.dumps({
        "title": title,
        "info": info,
        })


def get_team_standings(dorm=None, round_name=None):
    """Retrieves standings across all teams grouped by team."""

    team_label = get_team_label()

    title = team_label.capitalize() + " vs. " + team_label.capitalize() + ": "

    # Build up the query set.
    teams = Team.objects
    if dorm:
        teams = teams.filter(dorm=dorm)
        title = "%s: " % dorm.name

    if round_name:
        teams = teams.filter(
            profile__scoreboardentry__round_name=round_name).annotate(
            points=Sum("profile__scoreboardentry__points"),
            last_awarded_submission=Max(
                "profile__scoreboardentry__last_awarded_submission")
        ).order_by("-points", "-last_awarded_submission")
        title += round_name
    else:
        teams = teams.annotate(
            points=Sum("profile__points"),
            last_awarded_submission=Max("profile__last_awarded_submission")
        ).order_by("-points", "-last_awarded_submission")
        title += "Overall"

    # Construct the standings info dictionary.
    info = []
    for i, team in enumerate(teams):
        if dorm:
            # We don't need to put the dorm name if it's standings for a dorm.
            label = team.number
        else:
            label = "%s: %s %s" % (team.dorm.name, team_label, team.number)
        info.append({
            "points": team.points,
            "rank": i + 1,
            "label": label,
            })

    return json.dumps({
        "title": title,
        "info": info,
        })


def get_all_standings_for_user(user, is_me=True, group="team"):
    """Uses get_standings_for_user to generate standings for each round and the overall
standings for users in the user's team.  Returns an array of the different standings."""

    standings = []

    keys = settings.COMPETITION_ROUNDS.keys()
    keys.sort(_compare_rounds)

    for round_name in keys:
        standings.append(
            get_standings_for_user(user, group=group, round_name=round_name,
                is_me=is_me))

    # Append overall standings.
    standings.append(get_standings_for_user(user, group=group, is_me=is_me))

    return standings


def get_standings_for_user(user, group="team", round_name=None, is_me=True):
    """Generates standings for a user to be used in the standings widget.
Generates either team-wide standings or standings based on all users.
Returns a json structure for insertion into the javascript code."""

    _ = is_me
    standings_type = "individual"

    # Check for valid standings parameter.
    if group != "team" and group != "all":
        raise StandingsException(
            "Unknown standings type %s. Valid types are 'all' and 'team'." % standings_type)

    user_profile = Profile.objects.get(user=user)

    if not user_profile.team:
        # Nothing we can do.
        raise StandingsException("User has no team for standings.")

    title = user_entry = entries = None
    if round_name:
        # Calculate standings for round.
        user_entry, _ = user_profile.scoreboardentry_set.get_or_create(
            round_name=round_name)

        if not settings.COMPETITION_ROUNDS or not settings.COMPETITION_ROUNDS.has_key(
            round_name):
            # Nothing we can do again.
            raise StandingsException("Unknown round name %s" % round_name)

        if group == "team":
            entries = ScoreboardEntry.objects.filter(
                profile__team=user_profile.team,
                round_name=round_name,
            ).order_by("-points", "-last_awarded_submission")
            title = "Your standings in %s %s, %s" % (
            get_team_label(), user_profile.team.number, round_name)
        else:
            entries = ScoreboardEntry.objects.filter(
                round_name=round_name).order_by("-points",
                "-last_awarded_submission")
            title = "Your standings in all dorms, %s" % round_name

    else:
        # Calculate overall standings.
        user_entry = user_profile

        if group == "team":
            entries = Profile.objects.filter(team=user_profile.team).order_by(
                "-points", "-last_awarded_submission")
            title = "Individual standings, %s" % user_profile.team

        else:
            entries = Profile.objects.all().order_by("-points",
                "-last_awarded_submission")
            title = "Individual standings, Everyone"

    info, user_index = _calculate_user_standings(user_entry, entries)

    # Construct JSON return dictionary.
    return json.dumps({
        "title": title,
        "info": info,
        "myindex": user_index,
        "type": standings_type,
        })


def _calculate_user_standings(user_entry, entries, competition_round=None):
    """Finds user standings based on the user's entry and a list of entries.
Note that this code works when the passed instances are Profiles or
ScoreboardEntries, since it only accesses the points field.

Returns dictionary of points and the index of the user."""

    _ = competition_round
    # First and last users are easy enough to retrieve.
    first = entries[0]
    entry_count = entries.count()
    last = entries[entry_count - 1]

    # Search for user.
    rank = 1
    above_points = first.points
    below_points = last.points
    found_user = False
    for entry in entries:
        if entry == user_entry:
            # Set flag that we found the user.
            found_user = True
        elif not found_user:
            # If we haven't found the user yet, keep going.
            above_points = entry.points
            rank += 1
        elif found_user:
            # If we found the user, then this is the person just after.
            below_points = entry.points
            break

    # Construct the return dictionary.
    index = 0
    info = [{"points": first.points, "rank": 1, "label": ''}]

    # Append above points
    if rank == 2:
        # There's no above points, since that is #1
        index = 1
    elif rank > 2:
        info.append({"points": above_points, "rank": rank - 1, "label": ''})
        index = 2

    # Append user points if they are not #1
    if rank > 1:
        info.append({"points": user_entry.points, "rank": rank, "label": ''})

    # Append below and/or last only if the user is not ranked last.
    if rank < entry_count:
        if rank < entry_count - 1:
            # Append the below points if the user is ranked higher than second to last.
            info.append({"points": below_points, "rank": rank + 1, "label": ''})
        info.append({"points": last.points, "rank": entry_count, "label": ''})

    return info, index


def generate_standings_for_profile(user, is_me):
    return_dict = {"user_standings": []}

    team_standings = get_all_standings_for_user(user, is_me, "team")
    all_standings = get_all_standings_for_user(user, is_me, "all")
    # length of team_standings and all standings should be identical.
    for index in range(0, len(team_standings)):
        return_dict["user_standings"].append(
                {"team": team_standings[index], "all": all_standings[index]})

    # Default selected tab to overall.
    return_dict["selected_tab"] = len(return_dict["user_standings"]) - 1
    return_dict["standings_titles"] = []
    today = datetime.datetime.today()

    rounds = settings.COMPETITION_ROUNDS
    keys = settings.COMPETITION_ROUNDS.keys()
    keys.sort(_compare_rounds)

    for index, key in enumerate(keys):
        return_dict["standings_titles"].append(key)
        start = datetime.datetime.strptime(rounds[key]["start"], "%Y-%m-%d")
        end = datetime.datetime.strptime(rounds[key]["end"], "%Y-%m-%d")
        if today >= start and today < end:
            return_dict["selected_tab"] = index

    return_dict["standings_titles"].append("Overall")

    return return_dict