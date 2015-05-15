"""Provides the view of a help topic."""
import json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import  HttpResponse

from apps.widgets.help.models import HelpTopic


def supply(request, page_name):
    """ supply view_objects for widget rendering."""
    _ = request
    _ = page_name
    return {}


@login_required
def topic(request, category, slug):
    """Shows a help topic.  This method handles both a regular request and an
    AJAX request for dialog boxes."""
    help_topic = get_object_or_404(HelpTopic, slug=slug, category=category)

    if request.is_ajax():
        contents = render_to_string("help/dialog.html", {"topic": help_topic})
        return HttpResponse(json.dumps({
            "title": help_topic.title,
            "contents": contents,
            }), mimetype="application/json")

    return render_to_response("help/topic.html", {
        "topic": help_topic,
        }, context_instance=RequestContext(request))
