"""Provides competition settings in the request context to be used within a template."""
from django.contrib.auth.models import User
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
    designer_models = [None, None]
    admin_models = [None, None]
    developer_models = [None, None]

    challenge = challenge_mgr.get_challenge()
    css_theme = challenge.theme
    page_name = request.path[1:][:-1]

    if user.is_authenticated():
        try:
            profile = user.profile
        except User.DoesNotExist:
            profile = None

        if profile:
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

            if page_name == "sys_admin/challenge_mgr/challengesetting/1":
                page_name = "admin"
            if page_name in ("challenge_setting_admin", "challenge_admin", "developer_admin"):
                page_name = "admin"
                designer_models[0] = \
                    challenge_mgr.get_designer_challenge_info_models()
                designer_models[1] = \
                    challenge_mgr.get_designer_game_info_models()
                admin_models[0] = \
                    challenge_mgr.get_admin_challenge_info_models()
                admin_models[1] = challenge_mgr.get_admin_game_info_models()
                developer_models[0] = challenge_mgr.get_developer_challenge_info_models()
                developer_models[1] = challenge_mgr.get_developer_game_info_models()

    return {
        "CHALLENGE": challenge,
        "SCORE_SETTINGS": score_mgr.score_setting(),
        "CSS_THEME": css_theme,
        "TEAM_LABEL": challenge.team_label,
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
        "MAKAHIKI_DESIGNER_CHALLENGE_MODELS": designer_models[0],
        "MAKAHIKI_DESIGNER_GAME_MODELS": designer_models[1],
        "MAKAHIKI_ADMIN_CHALLENGE_MODELS": admin_models[0],
        "MAKAHIKI_ADMIN_GAME_MODELS": admin_models[1],
        "MAKAHIKI_DEVELOPER_CHALLENGE_MODELS": developer_models[0],
        "MAKAHIKI_DEVELOPER_GAME_MODELS": developer_models[1],
        "ACTIVE_PAGE": page_name
    }


def _get_default_view_objects(request):
    """Load the default widgets view objects for all pages."""
    default_view_objects = {}
    if not __is_admin_page(request):
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


def __is_admin_page(request):
    """Returns True if the request is for an admin page."""
    path_list = request.path.split('/')
    if len(path_list) > 1:
        return path_list[1].endswith('admin')
