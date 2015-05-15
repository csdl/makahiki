"""Defines the abstract resource storage such as wattdepot or eGauge."""


class ResourceStorage:
    """abstract class for the resource data storage."""

    class Meta:
        """Meta"""
        abstract = True

    def name(self):
        """returns the name of the resource storage."""
        raise Exception("'name' can not be called in abstract class.")

    def get_latest_resource_data(self, session, source_name, date):
        """Returns the latest usage of the specified resource for the current date."""
        _ = session
        _ = source_name
        _ = date
        raise Exception("'get_latest_resource_data' can not be called in abstract class.")

    def get_history_resource_data(self, session, source_name, date, hour):
        """Return the history energy usage of the team for the date and hour."""
        _ = session
        _ = source_name
        _ = date
        _ = hour
        raise Exception("'get_history_resource_data' can not be called in abstract class.")
