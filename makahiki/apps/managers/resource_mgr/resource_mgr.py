"""Provides services for a specific sustainability "resource" such as energy or water."""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.team_mgr.models import Team
from apps.managers.resource_mgr.models import EnergyUsage, WaterUsage, ResourceSetting, \
    WasteUsage, ResourceBlackoutDate
from django.template.defaultfilters import slugify
from apps.utils import utils


def get_resource_setting(name):
    """Returns the resource settings for the specified name."""
    resource_setting = cache_mgr.get_cache("resource_setting-%s" % name)
    if resource_setting is None:
        resource_setting = ResourceSetting.objects.get(name=name)
        cache_mgr.set_cache("resource_setting-%s" % name, resource_setting, 2592000)
    return resource_setting


def is_blackout(date):
    """Returns true if the date falls in the Resource Blackout dates."""
    return ResourceBlackoutDate.objects.filter(date=date).exists()


def team_resource_data(date, team, resource):
    """Returns the latest data for the specified resource on the current date."""

    if not is_blackout(date):
        usage = _get_resource_usage(resource)
        energy_data = usage.objects.filter(team=team, date=date)
        if energy_data:
            return energy_data[0]
        else:
            return None
    else:
        return None


def team_resource_usage(date, team, resource):
    """Returns the latest usage of the specified resource for the current date."""
    energy_data = team_resource_data(date, team, resource)
    if energy_data:
        return energy_data.usage
    else:
        return 0


def update_team_resource_usage(resource, session, date, team, source_name, storage):
    """update the latest energy usage for the team."""
    usage = storage.get_latest_resource_data(session, source_name, date)
    if usage:
        resource_usage = _get_resource_usage(resource)
        try:
            latest_usage = resource_usage.objects.get(team=team, date=date.date())
        except ObjectDoesNotExist:
            latest_usage = resource_usage(team=team, date=date.date())

        latest_usage.time = date.time()
        latest_usage.usage = usage
        latest_usage.save()
        print 'team %s energy usage from %s: %d at %s.' % (team, storage.name(), usage, date)


def get_history_resource_data(session, source_name, date, hour, storage):
    """Return the history energy usage of the team for the date and hour."""
    return storage.get_history_resource_data(session, source_name, date, hour)


def update_fake_water_usage(date):
    """update fake water usage."""
    for team in Team.objects.all():
        count = team.profile_set.count()
        if count:
            # assume the average water usage is 80 gallon per person per day
            average_usage = 80
            actual_usage = average_usage * 0.9
            water = WaterUsage.objects.filter(team=team, date=date.date())
            if water:
                water = water[0]
            else:
                water = WaterUsage(team=team, date=date.date())

            water.time = date.time()
            water.usage = actual_usage * count
            water.save()
            print 'team %s fake water usage updated at %s.' % (team, date)


def _get_resource_usage(name):
    """Returns the resource usage object by name, or None if not found."""
    if name == "energy":
        return EnergyUsage
    elif name == "water":
        return WaterUsage
    elif name == "waste":
        return WasteUsage
    else:
        return None


def resource_ranks(name, round_name=None):
    """Return the ranking of resource use for all teams."""

    cache_key = "%s_ranks-%s" % (name, slugify(round_name))
    ranks = cache_mgr.get_cache(cache_key)
    if ranks is None:
        resource_usage = _get_resource_usage(name)

        resource_setting = get_resource_setting(name)
        rate = resource_setting.conversion_rate
        if resource_setting.winning_order == "Ascending":
            ordering = "total"
        else:
            ordering = "-total"

        start_end = challenge_mgr.get_round_start_end(round_name)
        if start_end is not None:
            start, end = start_end
        else:
            return None

        usage_ranks = resource_usage.objects.filter(
            date__lte=end,
            date__gte=start).values("team__name").annotate(
                total=Sum("usage")).order_by(ordering)

        ranks = []
        for rank in usage_ranks:
            ranks.append({"team__name": rank["team__name"],
                          "total": utils.format_usage(rank["total"], rate)})

        cache_mgr.set_cache(cache_key, ranks, 600)
    return ranks


def group_resource_ranks(name, round_name=None):
    """Return the ranking of resource use for all teams."""

    cache_key = "group_%s_ranks-%s" % (name, slugify(round_name))
    ranks = cache_mgr.get_cache(cache_key)
    if ranks is None:
        resource_usage = _get_resource_usage(name)

        resource_setting = get_resource_setting(name)
        rate = resource_setting.conversion_rate
        if resource_setting.winning_order == "Ascending":
            ordering = "total"
        else:
            ordering = "-total"

        start_end = challenge_mgr.get_round_start_end(round_name)
        if start_end is not None:
            start, end = start_end
        else:
            return None

        usage_ranks = resource_usage.objects.filter(
            date__lte=end,
            date__gte=start).values("team__group__name").annotate(
                total=Sum("usage")).order_by(ordering)

        ranks = []
        for rank in usage_ranks:
            ranks.append({"team__group__name": rank["team__group__name"],
                          "total": utils.format_usage(rank["total"], rate)})

        cache_mgr.set_cache(cache_key, ranks, 600)
    return ranks


def resource_team_rank_info(team, resource):
    """Get the overall rank for the team. Return a dict of the rank number and usage."""
    unit = get_resource_setting(resource).unit
    if team:
        ranks = resource_ranks(resource)
        if ranks:
            for idx, rank in enumerate(ranks):
                if rank["team__name"] == team.name:
                    return {"rank": idx + 1, "usage": rank["total"], "unit": unit, }
    else:
        return None


def resource_leader(name, round_name=None, place=1):
    """Returns the leader (team name) of the resource use."""
    ranks = resource_ranks(name, round_name)
    if len(ranks) >= place:
        return ranks[place - 1]["team__name"]
    else:
        return None
