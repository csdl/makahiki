"""Provides the views for the home page and the first login wizard."""
import cgi
import json
import datetime
import urllib2

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from apps.lib.avatar.models import avatar_file_path, Avatar
import apps.lib.facebook_api.facebook as facebook
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.score_mgr import score_mgr
from apps.widgets.home.forms import ProfileForm, ReferralForm
from apps.widgets.smartgrid import smartgrid
from apps.widgets.help.models import HelpTopic


def supply(request, page_name):
    """Simply directs the user to the home page.

:return: an empty dict."""
    _ = request
    _ = page_name

    return {}


@login_required
def restricted(request):
    """The view when they have logged in before the competition begins."""

    # If we are in the competition, bring them back to the home page.
    if challenge_mgr.in_competition():
        return HttpResponseRedirect(reverse('home_index'))
    rounds_info = challenge_mgr.get_all_round_info()
    today = datetime.datetime.today()
    start = rounds_info["competition_start"]
    before = today < start
    end = today > rounds_info["competition_end"]
    if not before:
        next_round = challenge_mgr.get_next_round_info()
        if next_round:
            start = next_round["start"]

    return render_to_response("widgets/home/templates/restricted.html", {
        "before": before,
        "start": start,
        "end": end,
        }, context_instance=RequestContext(request))


@never_cache
@login_required
def setup_welcome(request):
    """Display page 1 (welcome) of the first login wizard."""
    if request.is_ajax():
        response = render_to_string("first-login/welcome.html", {},
            context_instance=RequestContext(request))

        return HttpResponse(json.dumps({
            "title": "Introduction: Step 1 of 7",
            "contents": response,
            }), mimetype='application/json')

    raise Http404


@never_cache
@login_required
def terms(request):
    """Display page 2 (terms and conditions) of first login wizard."""
    if request.is_ajax():
        referral_enabled = challenge_mgr.is_game_enabled("Referral Game Mechanics")
        tcObj = HelpTopic.objects.filter(slug="terms-and-conditions")
        if tcObj:
            termsObj = tcObj[0].contents

        response = render_to_string("first-login/terms.html", {
            "terms": termsObj,
            "referral_enabled": referral_enabled,
        }, context_instance=RequestContext(request))

        return HttpResponse(json.dumps({
            "title": "Introduction: Step 2 of 7",
            "contents": response,
            }), mimetype='application/json')

    raise Http404


@login_required
def referral(request):
    """Display page 3 (referral bonus) of the first login wizard."""

    if request.is_ajax():
        profile = request.user.profile
        form = None

        if request.method == 'POST':
            form = ReferralForm(request.POST, user=request.user)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                if 'referrer_email' in cleaned_data and len(
                    cleaned_data['referrer_email']) > 0:
                    profile.referring_user = User.objects.\
                    get(email=cleaned_data['referrer_email'])
                else:
                    # Double check just in case user comes back and deletes
                    # the email.
                    profile.referring_user = None
                profile.save()

                return _get_profile_form(request)

                # If form is not valid, it falls through here
        if not form and profile.referring_user:
            form = ReferralForm(initial={
                'referrer_email': profile.referring_user.email
            })
        elif not form:
            form = ReferralForm()

        response = render_to_string('first-login/referral.html', {
            'form': form,
            'referral_points': score_mgr.referral_points(profile),
            'active_threshold_points': score_mgr.active_threshold_points(),
            }, context_instance=RequestContext(request))

        return HttpResponse(json.dumps({
            "title": "Introduction: Step 3 of 7",
            "contents": response,
            }), mimetype='application/json')

    raise Http404


@never_cache
@login_required
def setup_profile(request):
    """Display page 4 (profile) of the first login wizard."""

    # Fields with file uploads are not AJAX requests.
    if request.method == "POST":
        form = ProfileForm(request.POST, user=request.user)
        profile = request.user.profile

        if form.is_valid():
            profile.name = form.cleaned_data["display_name"].strip()
            if not profile.setup_profile:
                profile.setup_profile = True
                profile.add_points(score_mgr.setup_points(),
                                   datetime.datetime.today(),
                                   "Set up profile")

            profile.save()

            if form.cleaned_data["pic_method"] == 0:
                name = request.user
                for avatar in Avatar.objects.filter(user=name):
                    avatar.delete()

            elif form.cleaned_data["pic_method"] == 2 and form.cleaned_data["facebook_photo"]:
                # Need to download the image from the url and save it.
                photo_temp = NamedTemporaryFile(delete=True)
                fb_url = form.cleaned_data["facebook_photo"]
                photo_temp.write(urllib2.urlopen(fb_url).read())
                photo_temp.flush()
                photo_temp.seek(0)

                path = avatar_file_path(user=request.user,
                    filename="fb_photo.jpg")
                avatar = Avatar(
                    user=request.user,
                    primary=True,
                    avatar=path,
                )
                avatar.avatar.storage.save(path, File(photo_temp))
                avatar.save()
            return HttpResponseRedirect(reverse("setup_activity"))
        return _get_profile_form(request, form=form, non_xhr=False)
    return _get_profile_form(request)


@never_cache
def _get_profile_form(request, form=None, non_xhr=False):
    """Helper method to render the profile form."""
    fb_id = None
    facebook_photo = None
    if settings.MAKAHIKI_USE_FACEBOOK:
        fb_id = facebook.get_user_from_cookie(
            request.COOKIES,
            settings.MAKAHIKI_FACEBOOK_APP_ID,
            settings.MAKAHIKI_FACEBOOK_SECRET_KEY)

    if fb_id:
        facebook_photo = "http://graph.facebook.com/%s/picture?type=normal" % fb_id

    if not form:
        form = ProfileForm(initial={
            "display_name": request.user.profile.name,
            "facebook_photo": facebook_photo,
            })

    referral_enabled = challenge_mgr.is_game_enabled("Referral Game Mechanics")

    response = render_to_string("first-login/profile.html", {
        "form": form,
        "fb_id": fb_id,
        "referral_enabled": referral_enabled,
        }, context_instance=RequestContext(request))

    if non_xhr:
        return HttpResponse('<textarea>' + json.dumps({
            "title": "Introduction: Step 4 of 7",
            "contents": cgi.escape(response),
            }) + '</textarea>', mimetype='text/html')
    else:
        return HttpResponse(json.dumps({
            "title": "Introduction: Step 4 of 7",
            "contents": response,
            }), mimetype='application/json')


@never_cache
@login_required
def setup_activity(request):
    """Display page 5 (activity) of the first login wizard."""

    activity = smartgrid.get_setup_activity()

    if request.is_ajax():
        template = render_to_string("first-login/activity.html", {'activity': activity},
            context_instance=RequestContext(request))

        response = HttpResponse(json.dumps({
            "title": "Introduction: Step 5 of 7",
            "contents": template,
            }), mimetype='application/json')

        return response

    else:
        template = render_to_string("first-login/activity.html", {'activity': activity},
            context_instance=RequestContext(request))

        response = HttpResponse("<textarea>" + json.dumps({
            "title": "Introduction: Step 5 of 7",
            "contents": cgi.escape(template),
            }) + "</textarea>", mimetype='text/html')

        return response


@never_cache
@login_required
def setup_question(request):
    """Display page 6 (activity question) of the first login wizard."""

    if request.is_ajax():
        template = render_to_string("first-login/question.html", {},
            context_instance=RequestContext(request))
        activity = smartgrid.get_setup_activity()
        points = str(activity.point_value) + " points"

        response = HttpResponse(json.dumps({
            "title": "Introduction: Step 6 of 7",
            "contents": template,
            "points": points,
            }), mimetype='application/json')

        return response
    raise Http404


@never_cache
@login_required
@csrf_exempt
def setup_complete(request):
    """Display page 7 (complete) of the first login wizard."""

    if request.is_ajax():
        profile = request.user.profile

        if request.method == "POST":
            # User got the question right.
            # link it to an activity.
            smartgrid.complete_setup_activity(request.user)

        profile.setup_complete = True
        profile.completion_date = datetime.datetime.today()
        profile.save()

        quest_enabled = challenge_mgr.is_game_enabled("Quest Game Mechanics")

        template = render_to_string("first-login/complete.html",
                {"quest_enabled": quest_enabled, },
                context_instance=RequestContext(request))

        response = HttpResponse(json.dumps({
            "title": "Introduction: Step 7 of 7",
            "contents": template,
            }), mimetype='application/json')

        return response
    raise Http404
