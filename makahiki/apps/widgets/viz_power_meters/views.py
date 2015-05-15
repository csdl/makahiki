"""Power meters visualization."""
from django.conf import settings

from apps.managers.team_mgr.models import Team


def supply(request, page_name):
    """ Handle the viz request."""

    _ = page_name

    team = request.user.profile.team
    group_lounges_count = 5
    all_lounges = Team.objects.order_by('name').all()
    for team in all_lounges:
        wattdepot_source_name = team.energygoalsetting_set.all()[0].wattdepot_source_name
        if not wattdepot_source_name:
            wattdepot_source_name = team.name
        team.wattdepot_source_name = wattdepot_source_name

    group_lounges_list = []

    if team:
        group_lounges = team.group.team_set.order_by('name').all()[:group_lounges_count]
        remainer = group_lounges_count - group_lounges.count()
        if remainer:
            remainer_lounges = Team.objects.exclude(group=team.group).order_by('name')[:remainer]
            if remainer_lounges.count():
                for l in group_lounges:
                    group_lounges_list.append(l)
                for l in remainer_lounges:
                    group_lounges_list.append(l)
    else:
        group_lounges = all_lounges[:group_lounges_count]

    if group_lounges_list:
        group_lounges = group_lounges_list
        group_lounges_count = len(group_lounges)
    else:
        group_lounges_count = group_lounges.count()

    for team in group_lounges:
        wattdepot_source_name = team.energygoalsetting_set.all()[0].wattdepot_source_name
        if not wattdepot_source_name:
            wattdepot_source_name = team.name
        if settings.MAKAHIKI_USE_WATTDEPOT3:
            wattdepot_source_name = wattdepot_source_name.lower()

        team.wattdepot_source_name = wattdepot_source_name

    if settings.MAKAHIKI_USE_WATTDEPOT3:
        wattdepot_version = "WATTDEPOT3"
    else:
        wattdepot_version = "WATTDEPOT2"

    return  {
        "all_lounges": all_lounges,
        "group_lounges": group_lounges,
        "group_lounges_count": group_lounges_count,
        "wattdepot_version": wattdepot_version,
        }


def remote_supply(request, page_name):
    """ Supports remote requests."""
    return supply(request, page_name)
