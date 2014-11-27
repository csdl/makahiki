"""Retrieve the data from the wattdepot."""

from xml.etree.ElementTree import ParseError
import datetime
from requests.exceptions import Timeout
from apps.managers.challenge_mgr import challenge_mgr
from xml.etree import ElementTree
from apps.managers.resource_mgr.storage import ResourceStorage
import json
from django.conf import settings


class Wattdepot(ResourceStorage):
    """Define the wattdepot data retrieval functions."""

    def name(self):
        """returns the name of the resource storage."""
        return "Wattdepot"

    def _get_usage_from_XML(self, xml_response):
        """get the usage from the XML response"""
        usage = 0
        property_elements = ElementTree.XML(xml_response).findall(".//Property")
        for p in property_elements:
            key_value = p.getchildren()
            if key_value and key_value[0].text == "energyConsumed":
                usage = key_value[1].text
        return usage

    def _get_usage_from_json(self, json_response):
        """get the usage from the JSON response"""
        value_object = json.loads(json_response)
        value = value_object["value"]
        if value:
            return value
        else:
            return 0

    def get_latest_resource_data_wattdepot3(self, session, source_name, date):
        """Returns the latest usage of the specified resource for the current date."""
        _ = date
        source_name = source_name.lower()

        session.params = {'sensor': source_name,
                          'latest': "true"}
        url = "%s/depository/energy/value/" % (challenge_mgr.get_challenge().wattdepot_server_url)
        return self._get_energy_usage(session, url, source_name) / 1000

    def get_history_resource_data_wattdepot3(self, session, source_name, date, hour):
        """Return the history energy usage of the team for the date and hour."""
        if hour and hour < 24:
            timestamp = date.strftime("%Y-%m-%dT") + "%.2d:00:00.000" % hour
        else:
            timestamp = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000")

        source_name = source_name.lower()
        session.params = {'sensor': source_name,
                          'timestamp': timestamp}
        url = "%s/depository/energy/value/" % (challenge_mgr.get_challenge().wattdepot_server_url)

        return self._get_energy_usage(session, url, source_name) / 1000

    def get_latest_resource_data_wattdepot2(self, session, source_name, date):
        """Returns the latest usage of the specified resource for the current date."""
        start_time = date.strftime("%Y-%m-%dT00:00:00")
        end_time = "latest"

        session.params = {'startTime': start_time, 'endTime': end_time}
        url = "%s/sources/%s/energy/" % (
            challenge_mgr.get_challenge().wattdepot_server_url, source_name)
        return self._get_energy_usage(session, url, source_name)

    def get_history_resource_data_wattdepot2(self, session, source_name, date, hour):
        """Return the history energy usage of the team for the date and hour."""
        start_time = date.strftime("%Y-%m-%dT00:00:00")
        if hour and hour < 24:
            end_time = date.strftime("%Y-%m-%dT") + "%.2d:00:00" % hour
        else:
            end_time = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")

        session.params = {'startTime': start_time, 'endTime': end_time}
        url = "%s/sources/%s/energy/" % (
            challenge_mgr.get_challenge().wattdepot_server_url, source_name)
        return self._get_energy_usage(session, url, source_name)

    def get_latest_resource_data(self, session, source_name, date):
        """Returns the latest usage of the specified resource for the current date."""
        if settings.MAKAHIKI_USE_WATTDEPOT3:
            return self.get_latest_resource_data_wattdepot3(session, source_name, date)
        else:
            return self.get_latest_resource_data_wattdepot2(session, source_name, date)

    def get_history_resource_data(self, session, source_name, date, hour):
        """Return the history energy usage of the team for the date and hour."""
        if settings.MAKAHIKI_USE_WATTDEPOT3:
            return self.get_history_resource_data_wattdepot3(session, source_name, date, hour)
        else:
            return self.get_history_resource_data_wattdepot2(session, source_name, date, hour)

    def _get_energy_usage(self, session, url, source):
        """Return the energy usage from wattdepot."""

        # comment out for debug
        #import sys
        #session.config['verbose'] = sys.stderr

        session.timeout = 5
        try:
            if settings.MAKAHIKI_USE_WATTDEPOT3:
                session.auth = (settings.WATTDEPOT_ADMIN_NAME, settings.WATTDEPOT_ADMIN_PASSWORD)
                response = session.get(url)

                #print response.text
                usage = self._get_usage_from_json(response.text)
            else:
                response = session.get(url)
                #print response.text

                usage = self._get_usage_from_XML(response.text)

            return abs(int(round(float(usage))))

        except ValueError:
            print 'Wattdepot data retrieval for team %s error: No JSON object.' % source
        except Timeout:
            print 'Wattdepot data retrieval for team %s error: connection timeout.' % source
        except ParseError as exception:
            print 'Wattdepot data retrieval for team %s ParseError : %s' % (source, exception)

        return 0
