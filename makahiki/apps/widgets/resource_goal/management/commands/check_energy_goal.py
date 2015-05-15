"""Invocation:  python manage.py check_energy_goal

Checks whether or not each team made their energy goal, and awards points to team members if it's
at the end of the day."""

import datetime
from apps.managers.challenge_mgr import challenge_mgr

from apps.managers.challenge_mgr.challenge_mgr import MakahikiBaseCommand
from apps.widgets.resource_goal import resource_goal


class Command(MakahikiBaseCommand):
    """command"""
    help = 'Check the energy goal for all teams, award points for meeting the goal'

    def handle(self, *args, **options):
        """check the energy goal for all teams and update the daily baseline"""
        today = datetime.datetime.today()
        print '****** Processing check_energy_goal for %s *******\n' % today

        if not challenge_mgr.is_game_enabled("Energy Game"):
            print "Energy Game is not enabled. Do nothing."
            return

        today = today.date()
        resource_goal.check_resource_goals("energy", today)

        # update the baseline
        resource_goal.update_resource_baseline("energy", today, 2)
