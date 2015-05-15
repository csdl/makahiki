"""
main views module to render pages.
"""
#import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import importlib
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.resource_goal import resource_goal


@never_cache
def root_index(request):
    """
    handle the landing page.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("home_index"))
    return HttpResponseRedirect(reverse("landing", args=()))


@never_cache
@login_required
def index(request):
    """
    handle top level pages.
    """
    page_name = request.path[1:][:-1]

    view_objects = {}

    if page_name != "home" and not challenge_mgr.is_page_unlock(request.user, page_name):
        return HttpResponseForbidden('<h1>Permission denied</h1>')

    # get the view_objects
    is_page_defined = supply_view_objects(request, page_name, view_objects)

    if not is_page_defined:
        raise Http404

    # get user resource rank and usage
    team = request.user.profile.team
    if team:
        if challenge_mgr.is_page_unlock(request.user, "energy"):
            view_objects["energy_rank_info"] = resource_goal.resource_goal_rank_info(team, "energy")
        if challenge_mgr.is_page_unlock(request.user, "water"):
            view_objects["water_rank_info"] = resource_goal.resource_goal_rank_info(team, "water")

    #time_start = datetime.datetime.now()
    response = render_to_response("%s.html" % page_name, {
        "view_objects": view_objects,
        }, context_instance=RequestContext(request))
    #time_end = datetime.datetime.now()
    #print "%s time: %s" % ("render", (time_end - time_start))
    return response


def supply_view_objects(request, page_name, view_objects):
    """ Returns view_objects supplied widgets defined in PageSetting. """

    widget_infos = challenge_mgr.get_enabled_widgets(page_name)
    if not widget_infos:
        return False

    view_objects['left_templates'] = []
    view_objects['right_templates'] = []

    for widget_info in widget_infos:
        view_module_name = 'apps.widgets.' + widget_info.widget + '.views'
        page_views = importlib.import_module(view_module_name)

        #time_start = datetime.datetime.now()
        widget_name = widget_info.widget.replace(".", "__")
        view_objects[widget_name] = page_views.supply(request, page_name)
        #time_end = datetime.datetime.now()
        #print "%s time: %s" % (view_module_name, (time_end - time_start))

        widget_template = "widgets/" + \
                          widget_info.widget.replace(".", "/") + \
                          "/templates/index.html"
        if widget_info.location == "Left":
            view_objects['left_templates'].append(widget_template)
        if widget_info.location == "Right":
            view_objects['right_templates'].append(widget_template)

    return True


@user_passes_test(lambda u: u.is_staff, login_url="/landing")
def clear_cache(request):
    """clear all cached content."""
    _ = request
    cache_mgr.clear()
    return HttpResponseRedirect("/admin")
