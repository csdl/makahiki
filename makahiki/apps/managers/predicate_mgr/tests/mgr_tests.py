"""Tests for the predicate_mgr functions.
Created on Jul 16, 2013

@author: Cam Moore
"""
from django.test.testcases import TransactionTestCase
import unittest
from apps.managers.predicate_mgr import predicate_mgr
from apps.utils import test_utils
from apps.widgets.smartgrid_design.models import Draft


class Test(TransactionTestCase):
    """Test cases for predicate_mgr."""

    def setUp(self):
        """Sets up the test environment."""
        self.user = test_utils.setup_user("user", "changeme")
        self.draft = Draft(name="test", slug="test")
        test_utils.set_competition_round()
        self.team = self.user.profile.team
        self.predicates = ["completed_action('intro-video')",
                            "submitted_all_of_type(action_type='commitment')",
                            "allocated_raffle_ticket()",
                            "badge_awarded('daily-visitor')",
                            "completed_some_of_level(level_priority=1, count=2)",
                            "submitted_some_of_resource(resource='energy', count=2)",
                            "submitted_all_of_level(1)",
                            "approved_all_of_resource(resource='energy')",
                            "approved_some_of_resource(resource='water', count=3)",
                            "set_profile_pic()",
                            "referring_count(4)",
                            "daily_visit_count(10)",
                            "unlock_on_date('2013-07-16')",
                           "unlock_on_event(event_slug='kick-off', days=-3, lock_after_days=5)",
                           "approved_some_of_level(level_priority=3, count=3)",
                           "submitted_level(3)",
                           "completed_some_of('event', 3)",
                           "daily_energy_goal_count(5)",
                           "submitted_action('like-cup')",
                           "approved_all_of_type('commitment')",
                           "approved_all_of_level(4)",
                           "posted_to_wall()",
                           "submitted_some_of_level(3, 4)",
                           "submitted_some_of_type('commitment', 2)",
                           "submitted_some_full_spectrum(3)",
                           "change_theme()",
                           "changed_theme()",
                           "approved_some_full_spectrum(4)",
                           "reached_round('Round 2')",
                           "social_bonus_count(30)",
                           "team_member_point_percent(30, 25)",
                           "approved_some(5)",
                           "completed_level(3)",
                           "approved_action('like-cup')",
                           "has_points(10)",
                           "submitted_all_of_resource('water')",
                           "submitted_some(34)",
                           "game_enabled('foobar')",
                           "is_admin()",
                           "approved_some_of_type('activity', 5)"]

    def tearDown(self):
        """Cleans up the test environment."""
        pass

    def testAllTestPredicateStrings(self):
        """Tests all the predicate strings using the tester predicates."""
        for pred in self.predicates:
            print pred
            predicate_mgr.eval_play_tester_predicates(pred, self.user, "test")

    def testAllPredicateStrings(self):
        """Tests all the predicate strings using the tester predicates."""
        for pred in self.predicates:
            print pred
            predicate_mgr.eval_predicates(pred, self.user)

if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    unittest.main()
