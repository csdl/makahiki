"""A middleware class for player login checking and tracking."""

import re
import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.models import create_user_profile


class LoginMiddleware(object):
    """This middleware does the following checks and tracking:
         * checks if today is in the competition period
         * checks if user has completed the setup
         * tracks how many days in a row the user has come to the site.
    """

    def process_request(self, request):
        """Check the competition period and that setup is completed."""
        #time_start = datetime.datetime.now()

        path = request.path

        # pass through for trivial requests
        pattern = "^/(log|site_media|favicon.ico)/"
        if re.compile(pattern).match(path):
            return None

        # load the db settings if not done yet.
        challenge_mgr.init()

        # pass through for trivial requests
        pattern = "^/(home\/restricted|admin|about|account)/"
        if re.compile(pattern).match(path):
            return None

        user = request.user
        if not user.is_authenticated():
            return None

        # user logged in
        # if user logged in and go to landing page, re-direct to home page
        if path.startswith("/landing/"):
            return HttpResponseRedirect(reverse("home_index"))

        # now the user is authenticated and going to the non-trivial pages.
        response = self.check_competition_period(request)

        if response is None:
            response = self.check_setup_completed(request)

            if response is None:
                response = self.track_login(request)

        #time_end = datetime.datetime.now()
        #print "%s time: %s" % ("player middleware", (time_end - time_start))
        return response

    def track_login(self, request):
        """Checks if the user is logged in and updates the tracking field."""
        profile = request.user.profile
        last_visit = profile.last_visit_date
        today = datetime.date.today()

        if last_visit:
            day_diff = today - last_visit
        else:
            day_diff = datetime.timedelta(days=30)

        if day_diff > datetime.timedelta(days=0):
            # if it is the first visit of the day
            if day_diff == datetime.timedelta(days=1):
                # consecutive day visit, increase daily login count
                profile.daily_visit_count += 1
            else:
                # gap day visit, reset the daily login count.
                profile.daily_visit_count = 1
            profile.last_visit_date = today
            profile.save()

        return None

    def check_setup_completed(self, request):
        """ Check to see if setup has been completed."""
        user = request.user
        path = request.path
        try:
            profile = user.profile
        except User.DoesNotExist:
            if not self.is_staff(request):
                return HttpResponseRedirect(reverse("restricted"))
            else:
                # if it is admin, recreate the profile
                create_user_profile(user)
                profile = user.profile

        # We need to check if the user is going to the home page so we don't
        # get caught in a redirect loop. We do need to filter out requests
        # for CSS and other resources.
        pattern = "^/home/"

        if not profile.setup_complete and \
           not re.compile(pattern).match(path):
            return HttpResponseRedirect(reverse("home_index"))

        return None

    def check_competition_period(self, request):
        """Checks if we are still in the competition. If the user is logged in,
        they are redirected to a competition status page.
        """
        staff_user = self.is_staff(request)

        if not staff_user and \
           not challenge_mgr.in_competition():
            return HttpResponseRedirect(reverse("home_restricted"))

        return None

    def is_staff(self, request):
        """check if a user is staff or superuser."""
        return request.user.is_superuser or request.user.is_staff
