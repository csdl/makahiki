"""Predicates indicating if a level or cell should be unlocked."""

from datetime import datetime, timedelta
from django.db.models.query_utils import Q
from apps.widgets.smartgrid import smartgrid
from apps.widgets.smartgrid.models import Action, Event, Grid


def approved_action(user, action_slug):
    """Returns true if the action is approved."""
    return user.actionmember_set.filter(action__slug=action_slug,
                                        approval_status="approved").count() > 0


def approved_all_of_level(user, level_priority):
    """Returns True if the user has had all Actions on the given level approved."""
    c = 0
    count = len(Grid.objects.filter(level__priority=level_priority))
    for action in Grid.objects.filter(level__priority=level_priority):
        c += user.actionmember_set.filter(action=action,
                                          approval_status="approved").count()
    return c >= count


def approved_all_of_resource(user, resource):
    """Returns True if the user has had all Actions of the given resource approved."""
    count = Action.objects.filter(related_resource=resource).count()
    return user.actionmember_set.filter(action__related_resource=resource,
                                        approval_status="approved").count() == count


def approved_all_of_type(user, action_type):
    """Returns True if the user has had all Actions of the action_type approved."""
    count = Action.objects.filter(type=action_type).count()
    return user.actionmember_set.filter(action__type=action_type,
                                        approval_status="approved").count() == count


def approved_some(user, count=1):
    """Returns True if the user has had count Actions approved."""
    return user.actionmember_set.filter(approval_status='approved').count() >= count


def approved_some_of_level(user, level_priority, count=1):
    """Returns True if the user has had count Actions approved for the given level."""
    c = 0
    for action in Grid.objects.filter(level__priority=level_priority):
        c += user.actionmember_set.filter(action=action,
                                          approval_status="approved").count()
    return c >= count


def approved_some_of_resource(user, resource, count=1):
    """Returns true of the user has had count Actions approved with the given resource."""
    return user.actionmember_set.filter(action__related_resource=resource,
                                        approval_status="approved").count() >= count


def approved_some_of_type(user, action_type, count=1):
    """Returns true if the user has had count Actions approved with the given action_type."""
    return user.actionmember_set.filter(action__type=action_type,
                                        approval_status="approved").count() >= count


def approved_some_full_spectrum(user, count=1):
    """Returns true if the user has had count Activities, Commitments, and Events approved."""
    ret = approved_some_of_type(user, action_type='activity', count=1)
    ret = ret and approved_some_of_type(user, action_type='commitment', count=count)
    ret = ret and approved_some_of_type(user, action_type='event', count=count)
    return ret


def completed_level(user, level_priority):
    """Returns true if the user has had all Activities and Commiments on the give level
    approved."""
    count = len(Grid.objects.filter(level__priority=level_priority, action__type='activity'))
    count += len(Grid.objects.filter(level__priority=level_priority, action__type='commitment'))
    c = 0
    for action in Grid.objects.filter(level__priority=level_priority):
        c += user.actionmember_set.filter(action=action,
                                          approval_status="approved").count()
    return c >= count


def social_bonus_count(user, count):
    """Returns True if the number of social bonus the user received equals to count."""
    return user.actionmember_set.filter(social_bonus_awarded=True).count() >= count


def submitted_action(user, action_slug):
    """Returns true if the user complete the action."""
    return action_slug in smartgrid.get_submitted_actions(user)


def submitted_all_of_level(user, level_priority):
    """Returns True if the user has submitted all Actions on the given level."""
    c = 0
    count = len(Grid.objects.filter(level__priority=level_priority))
    for action in Grid.objects.filter(level__priority=level_priority):
        c += user.actionmember_set.filter(action=action).count()
    return c >= count


def submitted_all_of_resource(user, resource):
    """Returns true if user has submitted all Actions of the given resoruce."""
    count = Action.objects.filter(related_resource=resource).count()
    c = user.actionmember_set.filter(action__related_resource=resource).count()
    return c == count


def submitted_all_of_type(user, action_type):
    """Returns true if user has submitted all Actions of the given action_type."""
    count = Action.objects.filter(type=action_type).count()
    return user.actionmember_set.filter(action__type=action_type).count() == count


def submitted_some(user, count=1):
    """Returns true if the user has completed count Actions."""
    return user.actionmember_set.all().count() >= count


def submitted_some_of_level(user, level_priority, count=1):
    """Returns true if the user has completed count Actions of the specified level."""
    c = 0
    for grid in Grid.objects.filter(level__priority=level_priority):
        c += user.actionmember_set.filter(action=grid.action).count()
    return c >= count


def submitted_some_of_resource(user, resource, count=1):
    """Returns True if user has submitted count Actions with the given resource."""
    return user.actionmember_set.filter(action__related_resource=resource).count() >= count


def submitted_some_of_type(user, action_type, count=1):
    """Returns True if user has submitted count Actions with the given action_type."""
    return user.actionmember_set.filter(action__type=action_type).count() >= count


def submitted_some_full_spectrum(user, count=1):
    """Returns true if the user has completed some activities, commitments, and
    events."""
    ret = submitted_some_of_type(user, action_type='activity', count=count)
    ret = ret and submitted_some_of_type(user, action_type='commitment', count=count)
    ret = ret and submitted_some_of_type(user, action_type='event', count=count)
    return ret


def submitted_level(user, level_priority):
    """Returns true if the user has performed all activities successfully, and
      attempted all commitments."""
#    num_completed = user.actionmember_set.filter(
#        Q(action__type='activity') | Q(action__type='commitment'),
#        action__level__priority=lvl).count()
    _ = user
    num_completed = 0
    level_actions = Grid.objects.filter(
        Q(action__type='activity') | Q(action__type='commitment'),
        level__priority=level_priority)
    for grid in level_actions:
        actionmember = user.actionmember_set.filter(action=grid.action)
        if actionmember:
            num_completed += 1
    num_level = level_actions.count()

    # check if there is any activity or commitment
    if not num_level:
        return False

    return num_completed == num_level


def unlock_on_date(user, date_string):
    """Returns true if the current date is equal to or after the date_string."""
    _ = user
    today = datetime.today()
    unlock_date = datetime.strptime(date_string, "%Y-%m-%d")
    return today >= unlock_date


def unlock_on_event(user, event_slug, days=0, lock_after_days=0):
    """Returns true if the current date is equal to or after the date of the Event
    defined by the event_slug, optionally days before. days should be a negative number.
    Optionally lock_after_days, if not zero then will return false lock_after_days
    after the event."""
    _ = user
    today = datetime.today()
    day_delta = timedelta(days=days)
    try:
        event = Event.objects.get(slug=event_slug)
        if event:
            unlock_date = event.event_date + day_delta
            if lock_after_days != 0:
                day_after = timedelta(days=lock_after_days)
                lock_date = event.event_date + day_after
                return today >= unlock_date and today <= lock_date
            else:
                return today >= unlock_date
        else:
            return True
    except Event.DoesNotExist:
        return True
