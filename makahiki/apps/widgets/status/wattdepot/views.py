"""Power meters visualization."""
from django.conf import settings

from apps.widgets.resource_goal.models import EnergyGoalSetting
from apps.managers.team_mgr.models import Team


def supply(request, page_name):
    """ Call the remote viz request."""

    _ = page_name
    _ = request

    goal_settings = EnergyGoalSetting.objects.all()
    if goal_settings:
        setting = goal_settings[0]
        interval = setting.realtime_meter_interval
    else:
        interval = 10

    all_lounges = Team.objects.order_by('name').all()

    for team in all_lounges:
        team.source_name = team.energygoalsetting_set.all()[0].wattdepot_source_name
        if not team.source_name:
            team.source_name = team.name
        if settings.MAKAHIKI_USE_WATTDEPOT3:
            team.source_name = team.source_name.lower()

    if settings.MAKAHIKI_USE_WATTDEPOT3:
        wattdepot_version = "WATTDEPOT3"
    else:
        wattdepot_version = "WATTDEPOT2"

    return {
        "interval": interval,
        "wattdepot_version": wattdepot_version,
        "data": {"all_lounges": all_lounges, }
    }
