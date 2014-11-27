"""line chart visualization."""
from django.conf import settings

from apps.managers.team_mgr.models import Team


def supply(request, page_name):
    """ Handle the request for viz_chart widget."""

    _ = page_name
    _ = request

    all_lounges = Team.objects.order_by('name').all()

    for team in all_lounges:
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
        "wattdepot_version": wattdepot_version,
        }
