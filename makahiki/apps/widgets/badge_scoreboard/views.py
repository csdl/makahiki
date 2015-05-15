"""Views handler for the Badge Scoreboard widget."""
from apps.managers.player_mgr.models import Profile
from django.db.models.aggregates import Count


def supply(request, page_name):
    """Supply the view_objects content for this widget, the badge scoreboard data."""

    user = request.user
    team = user.profile.team
    num_results = 10 if page_name != "status" else None
    all_profiles = Profile.objects.annotate(num_badges=Count('badgeaward')).order_by('-num_badges')
    if num_results:
        all_profiles = all_profiles[:num_results]

    team_profiles = None
    if team:
        team_profiles = team.profile_set.annotate(
            num_badges=Count('badgeaward')).order_by('-num_badges')
        if num_results:
            team_profiles = team_profiles[:num_results]

    return {
        "no_carousel": page_name == "status",
        "profiles": all_profiles,
        "team": team_profiles,
        "team_name": team.name if team else None,
    }
