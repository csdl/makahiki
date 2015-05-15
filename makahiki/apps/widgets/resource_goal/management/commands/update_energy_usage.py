"""Invocation:  python manage.py update_energy_usage

For each team, queries WattDepot server to find out cumulative energy usage from
midnight to now. Used for updating the status of the Energy Goal Game."""

import datetime
from apps.managers.challenge_mgr import challenge_mgr

from apps.managers.challenge_mgr.challenge_mgr import MakahikiBaseCommand
from apps.widgets.resource_goal import resource_goal


class Command(MakahikiBaseCommand):
    """command"""
    help = 'Update the energy usage for all teams from wattdepot server.'

    def handle(self, *args, **options):
        """Update the energy usage for all teams."""
        date = datetime.datetime.today()
        print '****** Processing energy usage update at %s *******\n' % date

        if not challenge_mgr.is_game_enabled("Energy Game"):
            print "Energy Game is not enabled. Do nothing."
            return

        resource_goal.update_resource_usage("energy", date)
