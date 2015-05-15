"""Provides the view of the team member widget."""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from apps.managers.score_mgr.models import ScoreboardEntry
from apps.managers.challenge_mgr import  challenge_mgr


def supply(request, page_name):
    """Supply view_objects content, which is the set of team members."""
    _ = page_name

    # Get the team members.
    team = request.user.profile.team
    current_round = challenge_mgr.get_round_name()
    if team and current_round:
        members_with_points = ScoreboardEntry.objects.filter(
            round_name=current_round).select_related(
            'profile').filter(profile__team=team)
        zero_point_members = team.profile_set.exclude(
            id__in=members_with_points.values_list(
            'profile__id', flat=True))

        # calculate and sort by rank
        members_with_points = sorted(list(members_with_points),
            key=lambda member: member.profile.overall_rank())

        zero_point_members = sorted(list(zero_point_members),
            key=lambda member: member.overall_rank())

    else:
        members_with_points = None
        zero_point_members = None

    return {
        "team_members": members_with_points,
        "zero_members": zero_point_members,
        }


@never_cache
@login_required
def team_members(request):
    """Provide the team members."""
    members = supply(request, 'news')
    return render_to_response("team_members.html", {
        "team_members": members,
        }, context_instance=RequestContext(request))
