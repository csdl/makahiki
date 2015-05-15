"""Prepare the rendering for the bonus_points widget."""
import json
from apps.widgets.bonus_points.models import BonusPoint
from apps.widgets.bonus_points.forms import GenerateBonusPointsForm
from django.core.urlresolvers import reverse
import datetime
from apps.widgets.notifications.models import UserNotification
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.shortcuts import render_to_response
'''
Created on Aug 5, 2012

@author: Cam Moore
'''

from apps.widgets.bonus_points.forms import BonusPointForm
from django.http import HttpResponse, Http404, HttpResponseRedirect


def supply(request, page_name):
    """Supply the view_objects for the Bonus Points widget."""
    _ = request
    _ = page_name
    bonus_form = BonusPointForm()

    return {"bonus_form": bonus_form}


def _check_bonus_code(user, form):
    """Checks the bonus code from AJAX."""
    _ = user
    code = None
    message = None

    try:
        code = BonusPoint.objects.get(code=form.cleaned_data['response'].lower())
        if not code.is_active:
            message = "This code has already been used."

    except BonusPoint.DoesNotExist:
        message = "This code is not valid."
    except KeyError:
        message = "Please input code."
    return message, code


def bonus_code(request):
    """Claim the Bonus Points via code."""

    user = request.user
    message = None
    profile = user.profile

    if request.is_ajax() and request.method == "POST":
        form = BonusPointForm(request.POST)
        if form.is_valid():
            message, code = _check_bonus_code(user, form)

            if message:
                return HttpResponse(json.dumps({
                                               "message": message}),
                                   mimetype="application/json")

            # award points
            points = code.point_value
            s = "Bonus Points: claimed {0} points".format(points)
            profile.add_points(points,
                               datetime.datetime.today(),
                               s)

            code.is_active = False
            code.save()

            response = HttpResponse(json.dumps({
                "redirectUrl": reverse("learn_index")}), mimetype="application/json")
            notification = "You collected " + str(points) + " bonus points!"
            response.set_cookie("bonus_notify", notification)
            UserNotification.create_info_notification(user, s)
            return response

        # At this point there is a form validation error.
        return HttpResponse(json.dumps({
            "message": "Please input bonus points code."
        }), mimetype="application/json")

    raise Http404


@never_cache
@login_required
def generate_codes_form(request):
    """Sets up the Generate Bonus Points page."""
    form = GenerateBonusPointsForm()
    return render_to_response("generate_bonus.html", {
        "form": form,
        }, context_instance=RequestContext(request))


def generate_codes(request):
    """Handles the generate_codes_form from and creates the BonusPoints."""
    if request.method == "POST":
        form = GenerateBonusPointsForm(request.POST)
        if form.is_valid():
            points = form.cleaned_data['point_value']
            num = form.cleaned_data['num_codes']
            BonusPoint.generate_bonus_points(points, num)

            response = HttpResponseRedirect("/admin/bonus_points/bonuspoint/")
            return response

    raise Http404
