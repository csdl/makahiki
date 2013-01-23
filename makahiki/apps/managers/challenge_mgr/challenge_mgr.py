"""The manager for challenge related settings."""

import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import capfirst
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr.models import ChallengeSetting, RoundSetting, PageSetting, \
    PageInfo, GameInfo, GameSetting
from apps.utils import utils
from django.core import management


_game_admin_models = {}
"""private variable to store the registered models for game admin page."""


_site_admin_models = {}
"""private variable to store the registered models for site admin page."""


_sys_admin_models = {}
"""private variable to store the registered models for sys admin page."""


def init():
    """Initialize the challenge."""

    if settings.DEBUG:
        import logging
    #    logger = logging.getLogger('django.db.backends')
    #    logger.setLevel(logging.DEBUG)
    #    logger.addHandler(logging.StreamHandler())

        logger = logging.getLogger('django_auth_ldap')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    # set the CHALLENGE setting from DB or cache
    set_challenge_settings(get_challenge())


def create_admin_user():
    """Create the admin user.
    Creates the admin user if it does not exist. Otherwise, reset the password to the ENV."""
    try:
        user = User.objects.get(username=settings.ADMIN_USER)

        if settings.MAKAHIKI_DEBUG and not user.check_password(settings.ADMIN_PASSWORD):
            user.set_password(settings.ADMIN_PASSWORD)
            user.save()
    except ObjectDoesNotExist:
        user = User.objects.create_superuser(settings.ADMIN_USER, "", settings.ADMIN_PASSWORD)
        profile = user.get_profile()
        profile.setup_complete = True
        profile.setup_profile = True
        profile.completion_date = datetime.datetime.today()
        profile.save()


def info():
    """Returns the challenge name and site."""
    init()
    challenge = get_challenge()
    return "Challenge name : %s @ %s" % (challenge.competition_name,
                                         challenge.site_name)


def get_challenge():
    """returns the ChallengeSetting object, from cache if cache is enabled"""
    challenge = cache_mgr.get_cache('challenge')
    if not challenge:
        challenge, _ = ChallengeSetting.objects.get_or_create(pk=1)

        # create the admin
        create_admin_user()

        cache_mgr.set_cache('challenge', challenge, 2592000)
    return challenge


def set_challenge_settings(challenge):
    """set the challenge related settings as django settings."""
    # round info
    settings.COMPETITION_ROUNDS = get_all_round_info_from_cache()
    settings.CURRENT_ROUND_INFO = get_current_round_info_from_cache()

    # email settings
    if challenge.email_enabled:
        settings.SERVER_EMAIL = challenge.contact_email
        settings.EMAIL_HOST = challenge.email_host
        settings.EMAIL_PORT = challenge.email_port
        settings.EMAIL_USE_TLS = challenge.email_use_tls
        settings.ADMINS = (('Admin', challenge.contact_email),)

    # setting for the CAS authentication service.
    if challenge.use_cas_auth:
        settings.CAS_SERVER_URL = challenge.cas_server_url
        settings.CAS_REDIRECT_URL = '/'
        settings.CAS_IGNORE_REFERER = True
        settings.LOGIN_URL = "/account/cas/login/"
    else:
        settings.LOGIN_URL = "/account/login/"

    # ldap settings
    if challenge.use_ldap_auth:
        from django_auth_ldap.config import LDAPSearch
        import ldap

        settings.AUTH_LDAP_SERVER_URI = challenge.ldap_server_url
        if settings.MAKAHIKI_LDAP_USE_CN:
            search_filter = "(cn=%(user)s)"
        else:
            search_filter = "(uid=%(user)s)"
        settings.AUTH_LDAP_USER_SEARCH = LDAPSearch("%s" % challenge.ldap_search_base,
                                           ldap.SCOPE_SUBTREE, search_filter)
        settings.AUTH_LDAP_ALWAYS_UPDATE_USER = False


def pages():
    """Returns a list of page names in this challenge."""
    return PageInfo.objects.all().values_list("name", flat=True)


def eval_page_unlock(user, page):
    """Returns True if the given page is unlocked based upon evaluation of its dependencies."""
    predicates = page.unlock_condition
    if not predicates:
        return False

    return utils.eval_predicates(predicates, user)


def all_page_info(user):
    """Returns a list of all pages with their current lock state."""
    all_pages = cache_mgr.get_cache("all_page_info-%s" % user.username)
    if not all_pages:
        all_pages = PageInfo.objects.exclude(name="home").order_by("priority")
        for page in all_pages:
            page.is_unlock = eval_page_unlock(user, page)
        cache_mgr.set_cache("all_page_info-%s" % user.username, all_pages, 1800)

    return all_pages


def is_page_unlock(user, page_name):
    """Returns the specific page unlock info."""
    for page in all_page_info(user):
        if page.name == page_name:
            return page.is_unlock
    return False


def get_enabled_widgets(page_name):
    """Returns the enabled widgets for the specified page, taking into account of the PageSetting
    and GameSetting."""
    return get_all_enabled_widgets()[page_name]


def get_all_enabled_widgets():
    """Returns the enabled widgets for each page, taking into account of the PageSetting
    and GameSetting."""
    page_widgets = cache_mgr.get_cache("enabled_widgets")
    if page_widgets is None:
        page_setting = PageSetting.objects.filter(enabled=True).select_related("page", "game")
        page_widgets = {}

        enabled_gs = GameSetting.objects.filter(enabled=True).select_related("game")

        for ps in page_setting:
            name = ps.page.name
            if not name in page_widgets:
                page_widgets[name] = []

            widgets = page_widgets[name]
            if ps.widget:
                widgets.append(ps.widget)
            if ps.game and ps.game.enabled:
                for gs in enabled_gs:
                    if gs.game.id == ps.game.id:
                        widgets.append(gs.widget)
        cache_mgr.set_cache("enabled_widgets", page_widgets, 2592000)
    return page_widgets


def is_game_enabled(name):
    """returns True if the game is enabled."""
    return name in get_all_enabled_games()


def get_all_enabled_games():
    """Returns the enabled games."""
    games = cache_mgr.get_cache("enabled_games")
    if games is None:
        games = []
        for game in GameInfo.objects.filter(enabled=True):
            games.append(game.name)
        cache_mgr.set_cache("enabled_games", games, 2592000)
    return games


def register_page_widget(page_name, widget, label=None):
    """Register the page and widget."""
    if not label:
        label = page_name
    page, _ = PageInfo.objects.get_or_create(name=page_name, label=label)
    PageSetting.objects.get_or_create(page=page, widget=widget)


def available_widgets():
    """Returns a list of all the available widgets for the challenge."""
    return settings.INSTALLED_WIDGET_APPS


def get_all_round_info():
    """Returns a dictionary containing all the round information.
    example: {"rounds": {"Round 1": {"start": start_date, "end": end_date,},},
              "competition_start": start_date,
              "competition_end": end_date}
    """
    return settings.COMPETITION_ROUNDS


def get_all_round_info_from_cache():
    """Returns a dictionary containing all the round information.
    example: {"rounds": {"Round 1": {"start": start_date, "end": end_date,},},
              "competition_start": start_date,
              "competition_end": end_date}
    """
    rounds_info = cache_mgr.get_cache('rounds')
    if rounds_info is None:
        roundsettings = RoundSetting.objects.all()
        if not roundsettings:
            RoundSetting.objects.create()
            roundsettings = RoundSetting.objects.all()
        rounds_info = {}
        rounds = {}
        index = 0
        # roundsettings is ordered by "start"
        r = None
        for r in roundsettings:
            rounds[r.name] = {
                "start": r.start,
                "end": r.end,
                "round_reset": r.round_reset,
                "display_scoreboard": r.display_scoreboard}
            if index == 0:
                rounds_info["competition_start"] = r.start
            index += 1

        rounds_info["competition_end"] = r.end
        rounds_info["rounds"] = rounds
        cache_mgr.set_cache('rounds', rounds_info, 2592000)

    return rounds_info


def get_current_round_info():
    """Returns a dictionary containing the current round information,
    if competition end, return the last round.
    example: {"name": round_name, "start": start_date, "end": end_date,} """
    return settings.CURRENT_ROUND_INFO


def get_current_round_info_from_cache():
    """Returns a dictionary containing the current round information,
    if competition end, return the last round.
    example: {"name": round_name, "start": start_date, "end": end_date,} """

    rounds_info = get_all_round_info()

    # Find which round this belongs to.
    today = datetime.datetime.today()
    if today < rounds_info["competition_start"]:
        return None

    rounds = rounds_info["rounds"]

    round_name = None
    for key in rounds:
        start = rounds[key]["start"]
        end = rounds[key]["end"]
        if start <= today < end:
            round_name = key
            break

    if round_name:
        return {"name": round_name,
                "start": rounds[round_name]['start'],
                "end": rounds[round_name]['end'],
                "round_reset": rounds[round_name]['round_reset'],
                "display_scoreboard": rounds[round_name]['display_scoreboard'],
        }
    else:
        return None


def get_next_round_info():
    """returns the next round info."""
    today = datetime.datetime.today()
    rounds_info = get_all_round_info()
    rounds = rounds_info["rounds"]

    next_round_name = None
    for key in rounds:
        start = rounds[key]["start"]
        if today <= start:
            next_round_name = key
            break

    if next_round_name:
        return {"name": next_round_name,
                "start": rounds[next_round_name]['start'],
                "end": rounds[next_round_name]['end'],
                "round_reset": rounds[next_round_name]['round_reset'],
                "display_scoreboard": rounds[next_round_name]['display_scoreboard'],
        }
    else:
        return None


def get_round_info(round_name=None):
    """Returns a dictionary containing round information, if round_name is not specified,
    returns the current round info. if competition end, return the last round.
    example: {"name": round_name, "start": start_date, "end": end_date,} """
    if not round_name:
        return get_current_round_info()
    else:
        rounds = get_all_round_info()["rounds"]
        return {"name": round_name,
                "start": rounds[round_name]['start'],
                "end": rounds[round_name]['end'],
                "round_reset": rounds[round_name]['round_reset'],
                "display_scoreboard": rounds[round_name]['display_scoreboard'],
        }


def get_round_name(submission_date=None):
    """Return the round name associated with the specified date, or else return None.
    if submission_date is not specified, return the current round name.
    if competition not started, return None,
    if competition end, return the last round."""
    if not submission_date:
        rounds_info = get_current_round_info()
        if rounds_info:
            return rounds_info["name"]
        else:
            return None

    rounds_info = get_all_round_info()
    if submission_date < rounds_info["competition_start"]:
        return None

    # Find which round this belongs to.
    round_name = None
    rounds = rounds_info["rounds"]
    for key in rounds:
        start = rounds[key]["start"]
        end = rounds[key]["end"]
        if start <= submission_date < end:
            round_name = key

    return round_name


def in_competition(submission_date=None):
    """Return True if we are currently in the competition."""
    return get_round_name(submission_date) is not None


def get_game_admin_models():
    """Returns the game related apps' info for admin purpose."""

    game_admins = ()
    for game in GameInfo.objects.all().order_by("priority"):
        game_admin = (game.name, game.enabled, game.pk, _game_admin_models[game.name],)
        game_admins += (game_admin,)
    return game_admins


def get_sys_admin_models():
    """return the sys admin models."""
    return get_admin_models(_sys_admin_models)


def get_site_admin_models():
    """return the site admin models."""
    return get_admin_models(_site_admin_models)


def get_admin_models(registry):
    """return the ordered tuple from the model registry."""
    models = ()
    for key in sorted(registry.keys()):
        models += ((key, registry[key]),)
    return models


def _get_model_admin_info(model):
    """return the admin info for the model."""
    return {"name": capfirst(model._meta.verbose_name_plural),
            "url": "%s/%s" % (model._meta.app_label, model._meta.module_name)}


def register_game_admin_model(game, model):
    """Register the model of the game for admin purpose."""
    register_admin_model(_game_admin_models, game, model)


def register_sys_admin_model(group, model):
    """Register the model for sys admin."""
    register_admin_model(_sys_admin_models, group, model)


def register_site_admin_model(group, model):
    """Register the model of site admin."""
    register_admin_model(_site_admin_models, group, model)


def register_admin_model(registry, group, model):
    """Register the model into a registry."""
    model_admin_info = _get_model_admin_info(model)
    if group in registry:
        registry[group] += (model_admin_info,)
    else:
        registry[group] = (model_admin_info,)

    registry[group] = sorted(registry[group])


class MakahikiBaseCommand(management.base.BaseCommand):
    """The base class for Makahiki command. Used when the init method of the
    challenge_mgr is called."""
    def __init__(self, *args, **kwargs):
        """Initialize the challenge_mgr."""
        init()
        super(MakahikiBaseCommand, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        """Handle the command. Should be overridden by sub class."""
        pass
