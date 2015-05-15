"""Retrieve the data from the egauge energy meter directly."""
from datetime import datetime
from time import mktime

from xml.etree.ElementTree import ParseError
from requests.exceptions import Timeout
from xml.etree import ElementTree
from apps.managers.resource_mgr.storage import ResourceStorage


class EGauge(ResourceStorage):
    """Define the wattdepot data retrieval functions."""

    def name(self):
        """returns the name of the resource storage."""
        return "eGauge"

    def get_latest_resource_data(self, session, source_name, date):
        """Returns the latest usage of the specified resource for the current date."""

        start_time = datetime(date.year, date.month, date.day)
        start_timestamp = int(mktime(start_time.timetuple()) + 1e-6 * start_time.microsecond)

        end_timestamp = int(mktime(date.timetuple()) + 1e-6 * date.microsecond)

        session.params = {"T": "%d,%d" % (start_timestamp, end_timestamp)}

        return self._get_energy_usage(session, source_name)

    def get_history_resource_data(self, session, source_name, date, hour):
        """Return the history energy usage of the team for the date and hour."""
        start_time = datetime(date.year, date.month, date.day)
        start_timestamp = int(mktime(start_time.timetuple()) + 1e-6 * start_time.microsecond)

        if hour and hour < 24:
            end_time = datetime(date.year, date.month, date.day, hour, 0, 0)
        else:
            end_time = datetime(date.year, date.month, date.day + 1)
        end_timestamp = int(mktime(end_time.timetuple()) + 1e-6 * end_time.microsecond)

        session.params = {"T": "%d,%d" % (start_timestamp, end_timestamp)}
        return self._get_energy_usage(session, source_name)

    def _get_source_name(self, source_name):
        """returns the eGauge meter name for the team."""
        team_source = {
            "Lehua": "hawaii1108",  # hawaii1108
            "Kukui": "hawaii1192",
            "Ilima": "hawaii1193",
            "Mokihana": "hawaii1194",
            "Melia": "hawaii1195",
            "Lokelani": "hawaii1199",
        }
        return team_source[source_name]

    def _get_energy_usage(self, session, source_name):
        """Return the energy usage from eGauge."""

        rest_url = "http://%s.egaug.es/cgi-bin/egauge-show?a&C" % self._get_source_name(source_name)

        # xpath for cgi-bin/egauge?tot
        # ".//*[@title='Student Usage V']/energy"
        # uncomment for debug
        #import sys
        #session.config['verbose'] = sys.stderr

        session.timeout = 5

        try:
            response = session.get(url=rest_url)

            #print response.text
            datas = ElementTree.XML(response.text).findall(".//data")

            # look for the column number of "Student Usage V" in meta row, row 1
            index = 0
            for column in datas[0].iter():
                if column.text == "Student Usage V":
                    break
                index += 1

            # the last data element is what we are looking for,
            columns = datas[-1].findall(".//c")
            # the third column is the student usage
            usage = columns[index - 1].text
            return abs(int(usage)) / 3600

        except Timeout:
            print 'eGauge data retrieval for team %s error: connection timeout.' % source_name
        except ParseError as exception:
            print 'eGauge data retrieval for team %s ParseError : %s' % (source_name, exception)

        return 0
