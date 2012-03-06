"""Support logging of AJAX-based interactions."""
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


@never_cache
@login_required
def log_ajax(request, obj_type, obj, action):
    """Simple AJAX view provided to support logging actions.

    Note that since the logger intercepts requests and responses,
    this method just returns a success response.
    """
    _ = obj_type
    _ = obj
    _ = action
    if request.is_ajax() and request.method == "GET":
        return HttpResponse()

    raise Http404
