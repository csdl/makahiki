"""Prize page view test"""
import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from apps.managers.challenge_mgr import challenge_mgr
from apps.utils import test_utils

from apps.widgets.prizes.models import Prize


class PrizesFunctionalTestCase(TransactionTestCase):
    """test prize page view"""

    fixtures = ["base_settings.json"]

    def setUp(self):
        """Set up a team and log in."""
#        challenge_mgr.init()
        test_utils.set_competition_round()
        self.user = test_utils.setup_user(username="user", password="changeme")

        test_utils.setup_round_prize("Round 1", "team_overall", "energy_usage")
        test_utils.setup_round_prize("Round 2", "team_overall", "energy_usage")
        test_utils.setup_round_prize("Round 1", "team_overall", "points")
        test_utils.setup_round_prize("Round 2", "team_overall", "points")
        test_utils.setup_round_prize("Round 1", "individual_overall", "points")
        test_utils.setup_round_prize("Round 2", "individual_overall", "points")
        test_utils.setup_round_prize("Round 1", "individual_team", "points")
        test_utils.setup_round_prize("Round 2", "individual_team", "points")

        print "setUp prize count %d" % Prize.objects.count()

        challenge_mgr.register_page_widget("win", "prizes")

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()

        profile = self.user.profile
        profile.add_points(10, datetime.datetime.today(), "test")
        profile.save()

        self.client.login(username="user", password="changeme")

    def testIndex(self):
        """Check that we can load the index page."""
        test_utils.set_competition_round()

        response = self.client.get(reverse("win_index"))
        self.failUnlessEqual(response.status_code, 200)

        print "testIndex prize count %d" % Prize.objects.count()

        for prize in Prize.objects.all():
            self.assertContains(response, prize.title, msg_prefix="Prize not found on prize page")

    def testLeadersInRound1(self):
        """Test that the leaders are displayed correctly in round 1."""
        #test_utils.set_competition_round()

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()

        profile = self.user.profile
        profile.name = "Test User"
        profile.add_points(10, datetime.datetime.today(), "test")
        team = profile.team
        profile.save()

        response = self.client.get(reverse("win_index"))
        self.assertContains(response, " place: " + str(profile), count=2,
            msg_prefix="Individual prizes should have user as the leader.")
        self.assertContains(response, " place: " + str(team), count=1,
            msg_prefix="Team points prizes should have team as the leader")
        self.assertContains(response, " place: TBD", count=4,
            msg_prefix="Round 2 prizes should not have a leader yet.")

        # Test XSS vulnerability.
        profile.name = '<div id="xss-script"></div>'
        profile.save()

        response = self.client.get(reverse("win_index"))
        self.assertNotContains(response, profile.name,
            msg_prefix="<div> tag should be escaped.")

    def testLeadersInRound2(self):
        """Test that the leaders are displayed correctly in round 2."""

        print "testLeadersInRound2.1 prize count %d" % Prize.objects.count()
        test_utils.set_three_rounds()
        print "testLeadersInRound2.2 prize count %d" % Prize.objects.count()
        test_utils.setup_round_prize("Round 1", "team_overall", "energy_usage")
        test_utils.setup_round_prize("Round 2", "team_overall", "energy_usage")
        test_utils.setup_round_prize("Round 1", "team_overall", "points")
        test_utils.setup_round_prize("Round 2", "team_overall", "points")
        test_utils.setup_round_prize("Round 1", "individual_overall", "points")
        test_utils.setup_round_prize("Round 2", "individual_overall", "points")
        test_utils.setup_round_prize("Round 1", "individual_team", "points")
        test_utils.setup_round_prize("Round 2", "individual_team", "points")
        print "testLeadersInRound2.3 prize count %d" % Prize.objects.count()

        profile = self.user.profile
        profile.add_points(10, datetime.datetime.today(), "test")
        profile.name = "Test User"
        team = profile.team
        profile.save()

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()
        print "testLeadersInRound2.4 prize count %d" % Prize.objects.count()

        response = self.client.get(reverse("win_index"))
        self.assertContains(response, "Winner: ", count=3,
            msg_prefix="There should be winners for three prizes.")
        self.assertContains(response, " place: " + str(profile), count=2,
            msg_prefix="Individual prizes should have user as the leader.")
        self.assertContains(response, " place: " + str(team), count=1,
            msg_prefix="Team points prizes should have team as the leader")

        # Test XSS vulnerability.
        profile.name = '<div id="xss-script"></div>'
        profile.save()

        response = self.client.get(reverse("win_index"))
        self.assertNotContains(response, profile.name,
            msg_prefix="<div> tag should be escaped.")
