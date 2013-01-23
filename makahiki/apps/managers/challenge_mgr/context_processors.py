"""Provides competition settings in the request context to be used within a template."""
from django.utils import importlib
import re
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.models import Profile
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr.models import Team
from apps.widgets.smartgrid import smartgrid
from django.conf import settings


def competition(request):
    """Provides access to standard competition constants within a template.

    :param request: The request object.
    :return: a dictionary of game settings."""
    # Get user-specific information.

    if _pass_through(request):
        return {}

    user = request.user
    team_member_count = None
    team_count = None
    overall_member_count = None
    available_events = None
    default_view_objects = None
    all_page_info = None
    site_admin_models = None
    sys_admin_models = None
    game_admin_models = None

    challenge = challenge_mgr.get_challenge()
    css_theme = challenge.theme
    page_name = request.path[1:][:-1]
    if user.is_authenticated():
        profile = user.get_profile()

        default_view_objects = _get_default_view_objects(request)
        all_page_info = challenge_mgr.all_page_info(user)

        if profile.team:
            team_member_count = profile.team.profile_set.count()
            team_count = Team.objects.count()
            overall_member_count = Profile.objects.count()
            available_events = smartgrid.get_next_available_event(user)

        # override the site theme if there is any
        if profile.theme:
            css_theme = profile.theme

        if page_name == "admin":
            site_admin_models = challenge_mgr.get_site_admin_models()
            sys_admin_models = challenge_mgr.get_sys_admin_models()
            game_admin_models = challenge_mgr.get_game_admin_models()

    return {
        "CHALLENGE": challenge,
        "SCORE_SETTINGS": score_mgr.score_setting(),
        "CSS_THEME": css_theme,
        "TEAM_LABEL": challenge.competition_team_label,
        "MAKAHIKI_FACEBOOK_APP_ID":
            settings.MAKAHIKI_FACEBOOK_APP_ID if settings.MAKAHIKI_USE_FACEBOOK else '',
        "MAKAHIKI_USE_LESS": settings.MAKAHIKI_USE_LESS,
        "CURRENT_ROUND_INFO": settings.CURRENT_ROUND_INFO,
        "TEAM_COUNT": team_count,
        "TEAM_MEMBER_COUNT": team_member_count,
        "OVERALL_MEMBER_COUNT": overall_member_count,
        "DEFAULT_VIEW_OBJECTS": default_view_objects,
        "AVAILABLE_EVENTS": available_events,
        "ALL_PAGE_INFO": all_page_info,
        "MAKAHIKI_SITE_ADMIN_MODELS": site_admin_models,
        "MAKAHIKI_SYS_ADMIN_MODELS": sys_admin_models,
        "MAKAHIKI_GAME_ADMIN_MODELS": game_admin_models,
        "ACTIVE_PAGE": page_name
    }


def _get_default_view_objects(request):
    """Load the default widgets view objects for all pages."""

    default_view_objects = {}
    for widget in settings.INSTALLED_DEFAULT_WIDGET_APPS:

        view_module_name = 'apps.widgets.' + widget + '.views'
        page_views = importlib.import_module(view_module_name)
        widget = widget.replace(".", "_")
        default_view_objects[widget] = page_views.supply(request, None)
    return default_view_objects


def _pass_through(request):
    """pass through for trivial requests."""
    path = request.path
    pattern = "^/(log/|site_media/|favicon.ico)"
    return re.compile(pattern).match(path)
