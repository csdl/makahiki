"""Predicates indicating if a level or cell should be unlocked."""

from django.db.models.query_utils import Q
from apps.widgets.smartgrid_play_tester import play_tester
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerGrid
from apps.managers.smartgrid_mgr import smartgrid_mgr
from django.http import Http404


def approved_action(user, draft_slug, action_slug):
    """Returns true if the action is approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft, action__slug=action_slug,
                                            approval_status="approved").count() > 0
    except Http404:
        return False


def approved_all_of_level(user, draft_slug, level_priority):
    """Returns True if the user has had all Actions on the given level approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        c = 0
        count = len(DesignerGrid.objects.filter(draft=draft, level__priority=level_priority))
        for action in DesignerGrid.objects.filter(level__priority=level_priority):
            c += user.testeractionsubmittion_set.filter(action=action,
                                              approval_status="approved").count()
        return c >= count
    except Http404:
        return False


def approved_all_of_resource(user, draft_slug, resource):
    """Returns True if the user has had all Actions of the given resource approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        count = DesignerAction.objects.filter(draft=draft, related_resource=resource).count()
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      action__related_resource=resource,
                                            approval_status="approved").count() == count
    except Http404:
        return False


def approved_all_of_type(user, draft_slug, action_type):
    """Returns True if the user has had all Actions of the action_type approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        count = DesignerAction.objects.filter(draft=draft, type=action_type).count()
        return user.testeractionsubmittion_set.filter(action__type=action_type,
                                            approval_status="approved").count() == count
    except Http404:
        return False


def approved_some(user, draft_slug, count=1):
    """Returns True if the user has had count Actions approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      approval_status='approved').count() >= count
    except Http404:
        return False


def approved_some_of_level(user, draft_slug, level_priority, count=1):
    """Returns True if the user has had count Actions approved for the given level."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        c = 0
        for action in DesignerGrid.objects.filter(draft=draft, level__priority=level_priority):
            c += user.testeractionsubmittion_set.filter(action=action,
                                              approval_status="approved").count()
        return c >= count
    except Http404:
        return False


def approved_some_of_resource(user, draft_slug, resource, count=1):
    """Returns true of the user has had count Actions approved with the given resource."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      action__related_resource=resource,
                                            approval_status="approved").count() >= count
    except Http404:
        return False


def approved_some_of_type(user, draft_slug, action_type, count=1):
    """Returns true if the user has had count Actions approved with the given action_type."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft, action__type=action_type,
                                            approval_status="approved").count() >= count
    except Http404:
        return False


def approved_some_full_spectrum(user, draft_slug, count=1):
    """Returns true if the user has had count Activities, Commitments, and Events approved."""
    ret = approved_some_of_type(user, draft_slug, action_type='activity', count=count)
    ret = ret and approved_some_of_type(user, draft_slug, action_type='commitment', count=count)
    ret = ret and approved_some_of_type(user, draft_slug, action_type='event', count=count)
    return ret


def completed_level(user, draft_slug, level_priority):
    """Returns true if the user has had all Activities and Commiments on the give level
    approved."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        count = len(DesignerGrid.objects.filter(draft=draft,
                                                level__priority=level_priority,
                                                action__type='activity'))
        count += len(DesignerGrid.objects.filter(draft=draft,
                                                 level__priority=level_priority,
                                                 action__type='commitment'))
        c = 0
        for grid in DesignerGrid.objects.filter(draft=draft,
                                                  level__priority=level_priority):
            c += user.testeractionsubmittion_set.filter(draft=draft, action=grid.action,
                                                            approval_status="approved").count()
            c += user.testeractionsubmittion_set.filter(draft=draft, action=grid.action,
                                                        action__type="commitment",
                                                        approval_status="pending").count()
        return c >= count
    except Http404:
        return False


def social_bonus_count(user, draft_slug, count):
    """Returns True if the number of social bonus the user received equals to count."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      social_bonus_awarded=True).count() >= count
    except Http404:
        return False


def submitted_action(user, draft_slug, action_slug):
    """Returns true if the user complete the action."""
    try:
        return action_slug in play_tester.get_submitted_actions(user, draft_slug)
    except Http404:
        return False


def submitted_all_of_level(user, draft_slug, level_priority):
    """Returns True if the user has submitted all Actions on the given level."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        c = 0
        count = len(DesignerGrid.objects.filter(draft=draft, level__priority=level_priority))
        for action in DesignerGrid.objects.filter(draft=draft, level__priority=level_priority):
            c += user.testeractionsubmittion_set.filter(draft=draft, action=action).count()
        return c >= count
    except Http404:
        return False


def submitted_all_of_resource(user, draft_slug, resource):
    """Returns true if user has submitted all Actions of the given resoruce."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        count = DesignerAction.objects.filter(draft=draft, related_resource=resource).count()
        c = user.testeractionsubmittion_set.filter(draft=draft,
                                                   action__related_resource=resource).count()
        return c == count
    except Http404:
        return False


def submitted_all_of_type(user, draft_slug, action_type):
    """Returns true if user has submitted all Actions of the given action_type."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        count = DesignerAction.objects.filter(draft=draft, type=action_type).count()
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      action__type=action_type).count() == count
    except Http404:
        return False


def submitted_some(user, draft_slug, count=1):
    """Returns true if the user has completed count Actions."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft).count() >= count
    except Http404:
        return False


def submitted_some_of_level(user, draft_slug, level_priority, count=1):
    """Returns true if the user has completed count Actions of the specified level."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        c = 0
        for grid in DesignerGrid.objects.filter(draft=draft, level__priority=level_priority):
            c += user.testeractionsubmittion_set.filter(action=grid.action).count()
        return c >= count
    except Http404:
        return False


def submitted_some_of_resource(user, draft_slug, resource, count=1):
    """Returns True if user has submitted count Actions with the given resource."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      action__related_resource=resource).count() \
                                                      >= count
    except Http404:
        return False


def submitted_some_of_type(user, draft_slug, action_type, count=1):
    """Returns True if user has submitted count Actions with the given action_type."""
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        return user.testeractionsubmittion_set.filter(draft=draft,
                                                      action__type=action_type).count() >= count
    except Http404:
        return False


def submitted_some_full_spectrum(user, draft_slug, count=1):
    """Returns true if the user has completed some activities, commitments, and
    events."""
    ret = submitted_some_of_type(user, draft_slug, action_type='activity', count=count)
    ret = ret and submitted_some_of_type(user, draft_slug, action_type='commitment', count=count)
    ret = ret and submitted_some_of_type(user, draft_slug, action_type='event', count=count)
    return ret


def submitted_level(user, draft_slug, level_priority):
    """Returns true if the user has performed all activities successfully, and
      attempted all commitments."""
    _ = user
    try:
        draft = smartgrid_mgr.get_designer_draft(draft_slug)
        num_completed = 0
        level_actions = DesignerGrid.objects.filter(
            Q(action__type='activity') | Q(action__type='commitment'),
            draft=draft, level__priority=level_priority)
        for grid in level_actions:
            testeractionsubmittion = user.testeractionsubmittion_set.filter(draft=draft,
                                                                            action=grid.action)
            if testeractionsubmittion:
                num_completed += 1
        num_level = level_actions.count()

        # check if there is any activity or commitment
        if not num_level:
            return False

        return num_completed == num_level
    except Http404:
        return False


def unlock_on_date(user, draft_slug, date_string):
    """Returns True."""
    _ = user
    _ = draft_slug
    _ = date_string
    return True


def unlock_on_event(user, draft_slug, event_slug, days=0, lock_after_days=0):
    """Returns true if the current date is equal to or after the date of the Event
    defined by the event_slug, optionally days before. days should be a negative number.
    Optionally lock_after_days, if not zero then will return false lock_after_days
    after the event."""
    _ = user
    _ = draft_slug
    _ = event_slug
    _ = days
    _ = lock_after_days
    return True
