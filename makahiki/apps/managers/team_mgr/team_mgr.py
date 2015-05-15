"""The manager for managing team."""
import datetime
from django.db.models.aggregates import Count, Max
from django.template.defaultfilters import slugify
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr.models import Team, Group


def team_members(team):
    """Get the team members."""
    return team.profile_set.all()


def team_normalize_size():
    """returns the normalize size for all the teams. It is the max team size across all teams."""
    size = cache_mgr.get_cache('team_normalize_size')
    if size is None:
        size = Team.objects.all().aggregate(max=Max('size'))["max"]
        if not size:
            size = 0
        cache_mgr.set_cache('team_normalize_size', size, 2592000)
    return size


def team_points_leader(round_name=None, place=1):
    """Returns the team points leader (the first place) across all groups, as a Team object."""
    if not round_name:
        round_name = challenge_mgr.get_round_name()

    team_id = score_mgr.team_points_leader(round_name=round_name, place=place)
    if team_id:
        return Team.objects.get(id=team_id)
    else:
        teams = Team.objects.all()
        if len(teams) >= place:
            return teams[place - 1]
        else:
            return None


def team_points_leaders(num_results=None, round_name=None):
    """Returns the team points leaders across all groups, as a dictionary profile__team__name
    and points.
    """
    size = team_normalize_size()
    if size:
        entries = score_mgr.team_points_leaders(round_name=round_name)
    else:
        entries = score_mgr.team_points_leaders(num_results=num_results, round_name=round_name)

    if entries:
        if size:
            for entry in entries:
                team = Team.objects.get(name=entry["profile__team__name"])
                if team.size:
                    entry["points"] = int(entry["points"] * float(size / team.size))
            # resort the entries after the normalization
            entries = sorted(entries, key=lambda e: e["points"], reverse=True)
            return entries[:num_results]
        else:
            return entries
    else:
        results = Team.objects.all().extra(
            select={'profile__team__name': 'name', 'points': 0}).values(
            'profile__team__name', 'points')
        if num_results:
            results = results[:num_results]
        return results


def group_points_leader(round_name=None, place=1):
    """Returns the team points leader (the place) across all groups, as a Team object."""
    if not round_name:
        round_name = challenge_mgr.get_round_name()

    group_id = score_mgr.group_points_leader(round_name=round_name, place=place)
    if group_id:
        return Group.objects.get(id=group_id)
    else:
        groups = Group.objects.all()
        if len(groups) >= place:
            return groups[place - 1]
        else:
            return None


def group_points_leaders(num_results=None, round_name=None):
    """Returns the group points leaders across all groups, as a dictionary profile__team__name
    and points.
    """

    entries = score_mgr.group_points_leaders(num_results=num_results, round_name=round_name)

    if entries:
        return entries
    else:
        results = Group.objects.all().extra(
            select={'profile__team__group__name': 'name', 'points': 0}).values(
            'profile__team__group__name', 'points')
        if num_results:
            results = results[:num_results]
        return results


def team_active_participation(num_results=None, round_name=None):
    """Calculate active participation."""
    if not round_name:
        round_name = challenge_mgr.get_round_name()

    participation = cache_mgr.get_cache('active_p-%s' % slugify(round_name))
    if participation is None:
        active_participation = Team.objects.filter(
            profile__scoreboardentry__points__gte=score_mgr.active_threshold_points(),
            profile__scoreboardentry__round_name=round_name).annotate(
                user_count=Count('profile')).order_by('-user_count')

        if num_results:
            active_participation = active_participation[:num_results]

        participation = []
        for t in active_participation:
            if t.size:
                t.active_participation = (t.user_count * 100) / t.size
            else:
                t.active_participation = (t.user_count * 100) / t.profile_set.count()
            participation.append(t)

        for t in Team.objects.all():
            if len(participation) == num_results:
                break

            if not t in active_participation:
                t.active_participation = 0
                participation.append(t)
        cache_mgr.set_cache('active_p-%s' % slugify(round_name), participation, 1800)
    return participation


def group_active_participation(num_results=None, round_name=None):
    """Calculate active participation."""
    if not round_name:
        round_name = challenge_mgr.get_round_name()

    participation = cache_mgr.get_cache('group_active_p-%s' % slugify(round_name))
    if participation is None:
        active_participation = Group.objects.filter(
            team__profile__scoreboardentry__points__gte=score_mgr.active_threshold_points(),
            team__profile__scoreboardentry__round_name=round_name).annotate(
                user_count=Count('team__profile')).order_by('-user_count')

        if num_results:
            active_participation = active_participation[:num_results]

        participation = []
        for g in active_participation:
            group_size = 0
            for t in g.team_set.all():
                group_size += t.profile_set.count()
            g.active_participation = (g.user_count * 100) / group_size
            participation.append(g)

        for g in Group.objects.all():
            if len(participation) == num_results:
                break

            if not g in active_participation:
                g.active_participation = 0
                participation.append(g)
        cache_mgr.set_cache('group_active_p-%s' % slugify(round_name), participation, 1800)
    return participation


def award_member_points(team, points, reason):
    """Award points to the members of the team."""
    count = 0
    for profile in team.profile_set.all():
        if profile.setup_complete:
            today = datetime.datetime.today()
            date = "%d/%d/%d" % (today.month, today.day, today.year)
            profile.add_points(points, today, "%s for %s" % (reason, date))
            profile.save()
            count += 1
    print '%d users in %s are awarded %s points for %s.' % (
        count,
        team,
        points,
        reason)
