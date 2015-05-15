"""Invocation:  python manage.py setup_test_data <command>

Sets up test data given the specified <command>.  Possible commands are:

  * create_users <number users for each team>
  * delete_users
  * rounds <number_of_rounds>
  * event_dates
  * commitment_durations <days>
  * resource_usages
  * resource_baselines
  * resource_goalsettings
  * all <number users for each team> <number_of_rounds>

"""

import datetime
from django.contrib.auth.models import User
import sys

from apps.managers.challenge_mgr.challenge_mgr import MakahikiBaseCommand
from apps.managers.challenge_mgr.models import RoundSetting
from apps.managers.resource_mgr.models import EnergyUsage, WaterUsage
from apps.managers.team_mgr.models import Team
from apps.widgets.resource_goal.models import EnergyGoalSetting, EnergyBaselineHourly, \
    EnergyBaselineDaily, WaterGoalSetting, WaterBaselineDaily, WaterGoal, EnergyGoal
from apps.widgets.smartgrid.models import Event, Commitment


class Command(MakahikiBaseCommand):
    """command"""
    help = "Setup the test data. Supported commands are : \n" \
           "  create_users <number_of_users for each team>\n" \
           "  delete_users \n" \
           "  rounds <number_of_rounds>\n" \
           "  event_dates \n"\
           "  commitment_durations <days> \n" \
           "  resource_usages \n" \
           "  resource_baselines \n" \
           "  resource_goalsettings \n" \
           "  all <number_of_users for each team>\n"

    def handle(self, *args, **options):
        """set up the test data"""

        if len(args) == 0:
            self.stdout.write(self.help)
            return

        operation = args[0]
        if operation == 'create_users':
            count = self._get_count_args(args, "test users for each team")
            self.create_users(count)
        elif operation == 'delete_users':
            self.delete_users()
        elif operation == 'rounds':
            count = self._get_count_args(args, "rounds")
            self.setup_rounds(count)
        elif operation == 'event_dates':
            self.setup_event_dates()
        elif operation == 'commitment_durations':
            count = self._get_count_args(args, "days for the commitment duration")
            self.setup_commitment_durations(count)
        elif operation == 'resource_usages':
            self.setup_resource_usages()
        elif operation == 'resource_baselines':
            self.setup_resource_baselines()
        elif operation == 'resource_goalsettings':
            self.setup_resource_goalsettings()
        elif operation == 'all':
            if len(args) < 1:
                self.stdout.write("Please specify the number of test users for each team.\n")
                return
            user_count = int(args[1])

            self.delete_users()
            self.create_users(user_count)
            self.setup_event_dates()
            self.setup_resource_usages()
            self.setup_resource_baselines()
            self.setup_resource_goalsettings()
        else:
            self.stdout.write("Invalid command. see help for supported commands.\n")

    def _get_count_args(self, args, mesg):
        """returns the user count specified from command line argument."""
        if len(args) == 1:
            self.stdout.write("Please specify the number of %s.\n" % mesg)
            sys.exit(1)
        return int(args[1])

    def create_users(self, count):
        """Create the specified number of test users for each team."""
        total_count = 0
        for team in Team.objects.all():
            for i in range(0, count):
                _ = i
                username = "player%d" % total_count
                user = User.objects.create_user(username,
                                                username + "@test.com",
                                                password="testuser")
                user.first_name = username.capitalize()
                user.last_name = "Test"
                user.save()

                profile = user.profile
                profile.name = username.capitalize()
                profile.team = team
                profile.save()

                total_count += 1

        self.stdout.write("%d test users created.\n" % total_count)

    def delete_users(self):
        """delete the test users name start with 'testuser-'."""
        users = User.objects.filter(username__startswith="player")
        total_count = 0
        for user in users:
            user.delete()
            total_count += 1
        self.stdout.write("%d test users deleted.\n" % total_count)

    def setup_rounds(self, count):
        """set up test rounds, any existing rounds will be deleted."""

        for r in RoundSetting.objects.all():
            r.delete()

        start = datetime.date.today()
        delta = datetime.timedelta(days=7)

        for i in range(0, count):
            end = start + delta
            end_time = datetime.datetime(year=end.year, month=end.month, day=end.day) - \
                       datetime.timedelta(seconds=1)
            RoundSetting(id=i + 1,
                         name="Round %d" % (i + 1),
                         start=start,
                         end=end_time
                        ).save()
            start = end

        self.stdout.write("set up %d one-week rounds, starting from today.\n" % count)

    def setup_event_dates(self):
        """adjust event dates to start from the beginning of the competition"""
        for event in Event.objects.filter(event_date__lte=datetime.datetime.today()):
            event_day_delta = event.event_date.date() - datetime.date(2011, 10, 17)
            event.event_date = datetime.datetime.today() + event_day_delta

            pub_day_delta = event.pub_date - datetime.date(2011, 10, 17)
            event.pub_date = datetime.date.today() + pub_day_delta

            event.save()
        self.stdout.write("event dates adjusted to round date.\n")

    def setup_commitment_durations(self, days):
        """adjust commitment duration."""
        for commitment in Commitment.objects.all():
            commitment.duration = days
            commitment.save()
        self.stdout.write("commitment duration adjusted to %s days.\n" % days)

    def setup_resource_usages(self):
        """remove any resource usage before the competition"""
        today = datetime.datetime.today()
        for usage in EnergyUsage.objects.filter(date__lte=today):
            usage.delete()
        for usage in WaterUsage.objects.filter(date__lte=today):
            usage.delete()

        # add initialize data for energy and water
        for team in Team.objects.all():
            WaterUsage(team=team, date=today.date(), time=datetime.time(15), usage=1000).save()
            EnergyUsage(team=team, date=today.date(), time=datetime.time(15), usage=1000).save()

        self.stdout.write("created initial resource usages for all teams.\n")

    def setup_resource_baselines(self):
        """set up the resource baseline data, all existing data will be delete."""

        # energy hourly
        for baseline in EnergyBaselineHourly.objects.all():
            baseline.delete()
        for team in Team.objects.all():
            for day in range(0, 7):
                for hour in range(1, 25):
                    EnergyBaselineHourly(team=team, day=day, hour=hour,
                                         usage=1 * 1000 * hour).save()

        # energy daily
        for baseline in EnergyBaselineDaily.objects.all():
            baseline.delete()
        for team in Team.objects.all():
            for day in range(0, 7):
                EnergyBaselineDaily(team=team, day=day, usage=1 * 1000 * 24).save()

        # water daily
        for baseline in WaterBaselineDaily.objects.all():
            baseline.delete()
        for team in Team.objects.all():
            count = team.profile_set.count()
            if count:
                # assume the average water usage is 80 gallon per person per day
                average_usage = 80
                for day in range(0, 7):
                    WaterBaselineDaily(team=team, day=day, usage=average_usage * count).save()

        self.stdout.write("created test baselines for all teams.\n")

    def setup_resource_goalsettings(self):
        """set up the resource goal data. all existing data will be delete."""

        #EnergyGoal
        for goal in EnergyGoal.objects.all():
            goal.delete()
        for goal_setting in EnergyGoalSetting.objects.all():
            goal_setting.delete()

        for team in Team.objects.all():
            EnergyGoalSetting(team=team).save()

        # WaterGoal
        for goal in WaterGoal.objects.all():
            goal.delete()
        for goal_setting in WaterGoalSetting.objects.all():
            goal_setting.delete()

        for team in Team.objects.all():
            WaterGoalSetting(team=team).save()

        self.stdout.write("created goal settings for all teams.\n")
