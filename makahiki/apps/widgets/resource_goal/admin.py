"""Energy goal widget administrator interface; shows the team, actual vs. goal, last update."""

from django.contrib import admin


class GoalSettingsAdmin(admin.ModelAdmin):
    """EnergyGoal administrator interface definition."""
    fields = ("team", "goal_percent_reduction", 'goal_points', 'baseline_method', 'data_storage',
              'wattdepot_source_name',
              ('manual_entry', 'manual_entry_time'), 'realtime_meter_interval')
    list_display = ["team", "goal_percent_reduction", "goal_points",
                    'baseline_method', 'data_storage', 'wattdepot_source_name', "manual_entry", ]


class GoalAdmin(admin.ModelAdmin):
    """EnergyGoal administrator interface definition."""
    list_display = ["date", "team", "goal_status", "actual_usage", "goal_usage",
                    "percent_reduction", "current_goal_percent_reduction", "updated_at"]
    search_fields = ["team__name", ]
    list_filter = ['team', 'date', 'goal_status']


class BaselineDailyAdmin(admin.ModelAdmin):
    """EnergyGoal administrator interface definition."""
    list_display = ["team", "day", "usage", "updated_at"]
    search_fields = ["team__name", ]
    list_filter = ['team', 'day']


class BaselineHourlyAdmin(admin.ModelAdmin):
    """EnergyGoal administrator interface definition."""
    list_display = ["team", "day", "hour", "usage", "updated_at"]
    search_fields = ["team__name", ]
    list_filter = ['team', 'day', 'hour']
