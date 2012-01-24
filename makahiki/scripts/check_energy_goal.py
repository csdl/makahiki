#!/usr/bin/env python
import sys
import datetime
from decimal import *

from os.path import abspath, dirname, join

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you have it installed or use pinax-boot.py to properly create a virtual environment.")
    sys.exit(1)

from django.conf import settings
from django.core.management import setup_environ

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
  
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from services.player_mgr.models import *
from services.player_mgr import *
from gamelets.smartgrid_game.models import *
from gamelets.notifications.models import UserNotification, NoticeTemplate
from services.base_mgr import in_competition, get_round_info
from gamelets.energy_game.models import FloorEnergyGoal
from services.team_mgr.models import Floor
from django.db.models import Q


__EMAIL__ = settings.GDATA_EMAIL
__PASSWORD__ = settings.GDATA_PASSWORD
__KEY__ = settings.GDATA_KEY

class GDataGoal:

  def __init__(self):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = __EMAIL__
    self.gd_client.password = __PASSWORD__
    self.gd_client.source = 'Spreadsheets GData Goal'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = __KEY__
      
  def _checkCellGoal(self):
    feed = self.gd_client.GetCellsFeed(self.curr_key)
    ## self._PrintFeed(feed)
    for i, entry in enumerate(feed.entry):
      if i >= 6:  
        ## print entry.content.text
        if i % 6 == 0:
          source = entry.content.text
        if i % 6 == 2:
   	      actual = Decimal(entry.content.text)
        if i % 6 == 3:
          goal = Decimal(entry.content.text)
          if goal != 0 and actual <= goal:
            is_meet_goal = True
          else:
            is_meet_goal = False;
        if i % 6 == 5:
          ## end of row
          print '---- %s actual=%d goal=%d' % (source, actual, goal) 
          if is_meet_goal:
            print "**** "+ source + " MEET the GOAL!"
            self.award_point(source, goal, actual)
			
  def _PrintFeed(self, feed):
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
        print '%s %s\n' % (entry.title.text, entry.content.text)

  def award_point(self, source, goal, actual):
    try:
      floor = Floor.objects.get(floor_identifier=source)
      goal = FloorEnergyGoal(
          floor=floor,
          goal_usage=goal,
          actual_usage=actual,
      )
      goal.save()
    except Floor.DoesNotExist:
      print 'floor with identifier %s does not exist' % source
    
  def Run(self):
    self._checkCellGoal()
        
def check_energy_goal():
  gdata = GDataGoal()
  gdata.Run()
              
if __name__ == "__main__":
    print '****** Processing check_energy_goal for %s *******\n' % datetime.datetime.today()

    check_energy_goal()
