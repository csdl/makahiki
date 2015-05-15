'''Provides the Education Game functionality.
Created on May 7, 2013
@author: Cam Moore
'''
from apps.widgets.smartgrid.models import ActionMember, Grid
from apps.widgets.smartgrid import smartgrid, view_commitments, view_activities, view_events, \
    view_reminders
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import importlib
from apps.widgets.action_feedback.models import ActionFeedback
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from apps.managers.score_mgr import score_mgr
from django.contrib import messages


def supply(request, page_name):
    """Supplies view_objects for education widget."""
    _ = page_name

    user = request.user
    completed = []
    available = {'activity': [], 'commitment': [], 'event': [], }
    pending = []
    for member in ActionMember.objects.filter(user=user):
        if member.approval_status == 'approved':
            completed.append(member.action)
        elif member.approval_status == 'pending':
            pending.append(member.action)
    for grid in Grid.objects.all():
        action = grid.action
        if smartgrid.is_unlock(user, action) and not action in pending and not action in completed:
            if smartgrid.availablity(action) == 0:
                available[action.type].append(action)

    return {
            'completed': completed,
            'pending': pending,
            'available_activities': available['activity'],
            'available_commitments': available['commitment'],
            'available_events': available['event'],
            }


@never_cache
@login_required
def view_action(request, action_type, slug):
    """individual action page"""
    action = smartgrid.get_action(slug=slug)
    user = request.user
    team = user.profile.team
    view_objects = {}

    action = smartgrid.annotate_action_details(user, action)

    if not action.is_unlock:
        response = HttpResponseRedirect(reverse("learn_index", args=()))
        response.set_cookie("task_unlock_condition", action.unlock_condition_text)
        return response

    completed_members = smartgrid.get_action_members(action)
    completed_count = completed_members.count()
    team_members = completed_members.select_related('user__profile').filter(
        user__profile__team=team)

    if action_type == "commitment":
        form = view_commitments.view(request, action)
    elif action_type == "activity":
        form = view_activities.view(request, action)

        # if there is embedded widget, get the supplied objects
        if action.embedded_widget:
            view_module_name = 'apps.widgets.' + action.embedded_widget + '.views'
            view_objects[action.embedded_widget] = importlib.import_module(
                view_module_name).supply(request, None)
            view_objects['embedded_widget_template'] = "widgets/" + \
                action.embedded_widget + "/templates/index.html"
    elif action.type in ("event", "excursion"):  # action.event:
        form = view_events.view(request, action)
        # calculate available seat
        action.available_seat = action.event.event_max_seat - completed_count
    elif action_type == "filler":
        response = HttpResponseRedirect(reverse("learn_index", args=()))
        return response

    user_reminders = view_reminders.load_reminders(action, user)
    try:
        feedback = ActionFeedback.objects.get(user=user.pk, action=action.pk)
    except ObjectDoesNotExist:
        feedback = None

    return render_to_response("task.html", {
        "action": action,
        "form": form,
        "completed_count": completed_count,
        "team_members": team_members,
        "display_form": True if "display_form" in request.GET else False,
        "reminders": user_reminders,
        "view_objects": view_objects,
        "feedback_p": feedback,
        }, context_instance=RequestContext(request))


@never_cache
@login_required
def add_action(request, action_type, slug):
    """Handle the Submission of the task."""

    action = smartgrid.get_action(slug=slug)
    if action_type == "commitment":
        return view_commitments.add(request, action.commitment)
    elif action_type == "activity":
        return view_activities.add(request, action.activity)
    else:       # event
        return view_events.add(request, action.event)


@never_cache
@login_required
def drop_action(request, action_type, slug):
    """Handle the drop task request."""
    _ = action_type
    action = smartgrid.get_action(slug=slug)
    user = request.user

    try:
        member = user.actionmember_set.get(action=action, approval_status="pending")
        member.delete()

        response = HttpResponseRedirect(
            reverse("activity_task", args=(action.type, action.slug,)))

        value = score_mgr.signup_points()
        notification = "%s dropped. you lose %d points." % (action.type, value)
        response.set_cookie("task_notify", notification)
        return response

    except ObjectDoesNotExist:
        pass

    messages.error = 'It appears that you are not participating in this action.'
    # Take them back to the action page.
    return HttpResponseRedirect(reverse("activity_task", args=(action.type, action.slug,)))
