"""handles rendering events."""
import json
import urlparse

from django.db import  IntegrityError
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from apps.managers.player_mgr import player_mgr
from apps.managers.score_mgr import score_mgr

from apps.widgets.smartgrid.models import  ActionMember, \
    Action, Event, ConfirmationCode
from apps.widgets.smartgrid.forms import EventCodeForm, ActivityCodeForm, GenerateCodeForm
from apps.widgets.bonus_points.models import BonusPoint
import datetime
from apps.widgets.notifications.models import UserNotification


def view(request, action):
    """Returns the activity info"""

    social_email = None
    if action.member:
        social_email = action.member.social_email

    form = ActivityCodeForm(
            initial={"social_email": social_email, },
            request=request)

    if not action.event.is_event_completed():
        form.form_title = "Sign up for this event"
    else:
        form.form_title = "Get your points"

    return form


def add(request, event):
    """Handle the Submission and claim point of the event."""
    if event.is_event_completed():
        return complete(request, event)
    else:
        return signup(request, event)


def signup(request, event):
    """Commit the current user to the activity."""
    user = request.user

    action_member = ActionMember(user=user, action=event)
    action_member.save()

    response = HttpResponseRedirect(
        reverse("activity_task", args=(event.type, event.slug,)))
    value = score_mgr.signup_points()
    notification = "You just earned " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


def complete(request, event):
    """complete the event and try to claim point."""

    user = request.user

    if request.method == "POST":
        form = ActivityCodeForm(request.POST, request=request, action=event)

        if form.is_valid():
            # Approve the activity (confirmation code is validated in
            # forms.ActivityTextForm.clean())
            code = ConfirmationCode.objects.get(code=form.cleaned_data["response"].lower())
            code.is_active = False
            code.user = user
            code.save()

            try:
                action_member = ActionMember.objects.get(user=user, action=event)
            except ObjectDoesNotExist:
                action_member = ActionMember(user=user, action=event)

            action_member.approval_status = "approved"
            value = event.point_value

            action_member.social_email = form.cleaned_data["social_email"].lower()
            try:
                action_member.save()
            except IntegrityError:
                messages.error = 'Sorry, but it appears that you have already added this activity.'
                return HttpResponseRedirect(
                    reverse("activity_task", args=(event.type, event.slug,)))

            response = HttpResponseRedirect(
                reverse("activity_task", args=(event.type, event.slug,)))
            if value:
                notification = "You just earned " + str(value) + " points."
                response.set_cookie("task_notify", notification)

            return response

        # invalid form
        # rebuild the form
        form.form_title = "Get your points"
        return render_to_response("task.html", {
            "action": event,
            "form": form,
            "completed_count": 0,
            "team_members": None,
            "display_form": True,
            "reminders": None,
            }, context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse("activity_task", args=(event.type, event.slug,)))


def _get_event_id_from_request(request):
    """return the event id from the request."""
    event_id = None
    if 'HTTP_REFERER' in request.META and 'PATH_INFO' in request.META:
        qs = request.META['HTTP_REFERER'].split('?')
        qs = urlparse.parse_qs(qs[-1])  # remove the '?'
        if "action__exact" in qs:
            event_id = int(qs['action__exact'][0])
    return event_id


@never_cache
@login_required
def view_codes(request, action_type, event_id):
    """View the confirmation codes for a given activity."""
    _ = action_type

    if not request.user or not request.user.is_staff:
        raise Http404

    if not event_id or event_id == '0':
        event_id = _get_event_id_from_request(request)

    per_page = 10

    # Check for a rows parameter
    if "rows" in request.GET:
        per_page = int(request.GET['rows'])

    event = get_object_or_404(Event, pk=event_id)
    codes = ConfirmationCode.objects.filter(action=event)

    return render_to_response("admin/view_codes.html", {
        "activity": event,
        "codes": codes,
        "per_page": per_page,
        }, context_instance=RequestContext(request))


@never_cache
@login_required
def generate_codes(request):
    """Handles the generate_codes_form from and creates the BonusPoints."""

    if request.method == "POST":
        form = GenerateCodeForm(request.POST)
        if form.is_valid():
            num = form.cleaned_data['num_codes']
            event_id = form.cleaned_data['event_id']
            event = get_object_or_404(Event, pk=event_id)
            ConfirmationCode.generate_codes_for_activity(event, num)
            url = "/admin/smartgrid/confirmationcode/?action__exact=%d" % event.id
            response = HttpResponseRedirect(url)
            return response
    else:
        event_id = _get_event_id_from_request(request)
        form = GenerateCodeForm(initial={"event_id": event_id})
        return render_to_response("admin/generate_code.html", {
            "form": form,
        }, context_instance=RequestContext(request))


@never_cache
@login_required
def view_rsvps(request, action_type, event_id):
    """View the RSVP list"""
    _ = action_type
    if not request.user or not request.user.is_staff:
        raise Http404

    action = get_object_or_404(Action, pk=event_id)

    rsvps = ActionMember.objects.filter(
        action=action,
        approval_status='pending'
    ).order_by('user__last_name', 'user__first_name')

    return render_to_response("admin/rsvps.html", {
        "activity": action,
        "rsvps": rsvps,
        }, context_instance=RequestContext(request))


def _check_attend_code(user, form):
    """Check the confirmation code in AJAX."""
    social_email = None
    code = None
    message = None
    is_bonus = False

    try:
        code = ConfirmationCode.objects.get(code=form.cleaned_data["response"].lower())
        # CAM 11/08/12 this assumes that ConfirmationCodes are only for events.
        if code.action.event.event_date > datetime.datetime.today():
            message = "The Event has not occurred, Please wait till after the event date to submit."
        elif code.action in user.action_set.filter(actionmember__award_date__isnull=False):
            message = "You have already redeemed a code for this event."
        elif not code.is_active:
            message = "This code has already been used."
        elif code.action.social_bonus:
            if form.cleaned_data["social_email"]:
                if form.cleaned_data["social_email"] != "Email":
                    ref_user = player_mgr.get_user_by_email(
                        form.cleaned_data["social_email"].lower())
                    if ref_user == None or ref_user == user:
                        message = "Invalid email. Please input only one valid email."
                        social_email = "true"
                else:
                    message = "Please enter one Kukui Cup email or clear the email to submit"
                    social_email = "true"

    except ConfirmationCode.DoesNotExist:
        try:
            code = BonusPoint.objects.get(code=form.cleaned_data['response'].lower())
            is_bonus = True
            if not code.is_active:
                message = "This code has already been used."

        except BonusPoint.DoesNotExist:
            message = "This code is not valid."
    except KeyError:
        message = "Please input code."
    return message, social_email, code, is_bonus


def attend_code(request):
    """Claim the attendance code or the Bonus Points code"""

    user = request.user
    action_member = None
    message = None
    social_email = None

    if request.is_ajax() and request.method == "POST":
        form = EventCodeForm(request.POST)
        if form.is_valid():
            message, social_email, code, is_bonus = _check_attend_code(user, form)

            if message:
                return HttpResponse(json.dumps({
                    "message": message,
                    "social_email": social_email
                }), mimetype="application/json")

            if not is_bonus:  # It was an event code.
                try:
                    action_member = ActionMember.objects.get(user=user, action=code.action)
                except ObjectDoesNotExist:
                    action_member = ActionMember(user=user, action=code.action)

                action_member.approval_status = "approved"
                value = code.action.point_value

                if "social_email" in form.cleaned_data and \
                    form.cleaned_data["social_email"] != "Email":
                    action_member.social_email = form.cleaned_data["social_email"].lower()

                # Model save method will award the points.
                action_member.save()
            else:  # It was a bonus point code.
                profile = user.profile
                value = code.point_value
                s = "Bonus Points: claimed {0} points".format(value)
                profile.add_points(value,
                                   datetime.datetime.today(),
                                   s)
                code.claim_date = datetime.datetime.now()

            code.is_active = False
            code.user = user
            code.save()

            notification = "You just earned " + str(value) + " points."
            if not is_bonus:
                response = HttpResponse(json.dumps({
                            "redirectUrl": reverse("activity_task",
                                                   args=(code.action.type, code.action.slug))
                            }), mimetype="application/json")
                response.set_cookie("task_notify", notification)
            else:
                response = HttpResponse(json.dumps({
                            "redirectUrl": reverse("learn_index")}),
                                        mimetype="application/json")
                response.set_cookie("bonus_notify", notification)
                UserNotification.create_info_notification(user, s)
            return response

        # At this point there is a form validation error.
        return HttpResponse(json.dumps({
            "message": "Please input code."
        }), mimetype="application/json")

    raise Http404
