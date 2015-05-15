"""Handles wall post widget request and rendering."""
import json
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.template.context import RequestContext
from django.template.loader import render_to_string
from apps.managers.team_mgr.models import Post
from apps.widgets.wallpost.forms import WallForm

DEFAULT_POST_COUNT = 10
"""Number of posts to load at a time."""


def supply(request, page_name):
    """supply the view_objects."""
    return {
            "default_post_count": DEFAULT_POST_COUNT,
            "request": request,
            "page_name": page_name,
            }


def super_supply(request, page_name, agent):
    """supply the view_objects."""
    agent_post = agent + "_post"
    user = request.user
    team = user.profile.team

    if "last_post" in request.GET:
        posts = Post.objects.filter(
                    style_class=agent_post,
                    team=team,
                    id__lt=int(request.GET["last_post"])).select_related(
                        'user__profile').order_by("-id")
    else:
        posts = Post.objects.filter(
            style_class=agent_post,
            team=team
        ).select_related('user__profile').order_by("-id")

    user_title = "Team News Feed"
    system_title = "Game Feed"
    description = ""

    post_count = posts.count()
    posts = posts[:DEFAULT_POST_COUNT]
    is_more_posts = True if post_count > DEFAULT_POST_COUNT else False

    wall_form = WallForm(initial={"page_name": page_name})

    return {
        "page_name": page_name,
        "user_title": user_title,
        "system_title": system_title,
        "description": description,
        "posts": posts,
        "more_posts": is_more_posts,
        "wall_form": wall_form,
        }


@login_required
def super_more_posts(request, agent):
    """handle more post link"""
    if request.is_ajax():
        view_objects = {}
        view_objects["wallpost__" + agent + "_wallpost"] = super_supply(
            request,
            request.GET["page_name"],
            agent
        )
        template = render_to_string(agent + "_news_posts.html", {
            "view_objects": view_objects,
            }, context_instance=RequestContext(request))

        return HttpResponse(json.dumps({
            "contents": template,
            }), mimetype='application/json')

    raise Http404


@login_required
def post(request):
    """handle the submission of the wall post"""
    if request.is_ajax() and request.method == "POST":
        form = WallForm(request.POST)
        if form.is_valid():
            wall_post = Post(
                user=request.user,
                team=request.user.profile.team,
                text=form.cleaned_data["post"]
            )
            wall_post.save()

            # Render the post and send it as a response.
            template = render_to_string("user_post.html", {"post": wall_post},
                context_instance=RequestContext(request))
            return HttpResponse(json.dumps({
                "contents": template,
                }), mimetype="application/json")

        # At this point there is a form validation error.
        return HttpResponse(json.dumps({
            "message": "This should not be blank."
        }), mimetype="application/json")

    raise Http404
