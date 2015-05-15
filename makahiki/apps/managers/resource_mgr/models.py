"""The model for the resource manager."""
import datetime

from django.db import models
from apps.managers.cache_mgr import cache_mgr

from apps.managers.team_mgr.models import Team


class ResourceSetting(models.Model):
    """resource settings model."""

    RESOURCE_CHOICE = (
        ("energy", "energy"),
        ("water", "water"),
        ("waste", "waste"),)
    WINNING_ORDER_CHOICE = (
        ("Ascending", "Ascending"),
        ("Descending", "Descending"),)

    name = models.CharField(
        choices=RESOURCE_CHOICE,
        max_length=20,
        help_text="The name of the resource.",
    )
    unit = models.CharField(
        max_length=20,
        help_text="The unit of the resource, such as kWh, Gallon, etc.",
    )
    conversion_rate = models.IntegerField(
        default=1,
        help_text="The rate of converting the usage data into the unit. For example, 1000 could be "
                  "specified to convert usage data recorded in Wh to kWh.",
    )
    winning_order = models.CharField(
        max_length=10,
        choices=WINNING_ORDER_CHOICE,
        help_text="The winning order. Ascending indicates the lesser/smaller wins."
    )
    admin_tool_tip = ""

    class Meta:
        """Meta"""
        unique_together = ("name",)

    def save(self, *args, **kwargs):
        """Custom save method."""
        super(ResourceSetting, self).save(*args, **kwargs)
        cache_mgr.delete("resource_setting-%s" % self.name)


class ResourceBlackoutDate(models.Model):
    """defines the blackout dates for the resource related games."""
    date = models.DateField(
        help_text="The date when the resource usage should be ignored.")
    description = models.CharField(
        blank=True, null=True,
        max_length=20,
        help_text="The description of the date.")


class ResourceUsage(models.Model):
    """abstract resource usage model."""
    team = models.ForeignKey(Team)
    date = models.DateField(
        default=datetime.date.today(),
        help_text="The date when the usage or reading is recorded.")
    time = models.TimeField(
        default=datetime.datetime.today().time(),
        help_text="The time of the day when the usage or reading is recorded.")
    manual_meter_reading = models.IntegerField(
        default=0,
        help_text="The daily manual reading of the meter, in the unit defined in ResourceSetting. "\
                  "only needed when manually reading the meter.")
    usage = models.IntegerField(
        default=0,
        help_text="The daily usage, if manual_meter_reading is input and the reading from " \
                  "the day before is available, this will be automatically calculated.")

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        """Meta"""
        abstract = True
        unique_together = (("date", "team",),)
        ordering = ("-date", "team")


class EnergyUsage(ResourceUsage):
    """Energy usage model."""
    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        if self.manual_meter_reading:
            day_before = EnergyUsage.objects.filter(
                team=self.team, date=self.date - datetime.timedelta(days=1))
            if day_before:
                self.usage = self.manual_meter_reading - day_before[0].manual_meter_reading

        super(EnergyUsage, self).save(args, kwargs)
    admin_tool_tip = "Team Energy Usage"


class WaterUsage(ResourceUsage):
    """Water usage model."""
    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        if self.manual_meter_reading:
            day_before = WaterUsage.objects.filter(
                team=self.team, date=self.date - datetime.timedelta(days=1))
            if day_before:
                self.usage = self.manual_meter_reading - day_before[0].manual_meter_reading

        super(WaterUsage, self).save(args, kwargs)
    admin_tool_tip = "Team Water Usage"


class WasteUsage(ResourceUsage):
    """Water usage model."""
    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        if self.manual_meter_reading:
            day_before = WasteUsage.objects.filter(
                team=self.team, date=self.date - datetime.timedelta(days=1))
            if day_before:
                self.usage = self.manual_meter_reading - day_before[0].manual_meter_reading

        super(WasteUsage, self).save(args, kwargs)
    admin_tool_tip = "Team Waste Output"
