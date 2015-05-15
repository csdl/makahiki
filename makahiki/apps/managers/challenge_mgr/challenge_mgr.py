"""The manager for challenge related settings."""

import datetime
import operator
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import capfirst
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr.models import ChallengeSetting, RoundSetting, PageSetting, \
    PageInfo, GameInfo, GameSetting
from django.core import management
from apps.managers.predicate_mgr import predicate_mgr

_designer_challenge_info_models = {}
"""private variable to store the registered models for challenge designer challenge page."""

_designer_game_info_models = {}
"""private variable to store the registered models for challenge designer game page."""

_admin_challenge_info_models = {}
"""private variable to store the registered models for challenge admin challenge page."""

_admin_game_info_models = {}
"""private variable to store the registered models for challenge admin game page."""

_developer_challenge_info_models = {}
"""private variable to store the registered models for developer admin challenge page."""

_developer_game_info_models = {}
"""private variable to store the registered models for developer admin game page."""


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
        profile = user.profile
        profile.setup_complete = True
        profile.setup_profile = True
        profile.completion_date = datetime.datetime.today()
        profile.save()


def info():
    """Returns the challenge name and site."""
    init()
    challenge = get_challenge()
    return "Challenge name : %s @ %s" % (challenge.name,
                                         challenge.domain)


def get_challenge():
    """returns the ChallengeSetting object, from cache if cache is enabled"""
    challenge = cache_mgr.get_cache('challenge')
    if not challenge:
        challenge, _ = ChallengeSetting.objects.get_or_create(pk=1)

        if challenge.wattdepot_server_url:
            # check the WattDepot URL to ensure it does't end with '/'
            while challenge.wattdepot_server_url.endswith('/'):
                challenge.wattdepot_server_url = challenge.wattdepot_server_url[:-1]
            # append auth info
            if settings.MAKAHIKI_USE_WATTDEPOT3:
                challenge.wattdepot_server_url = challenge.wattdepot_server_url.replace(
                    "://", "://%s:%s@" % (settings.WATTDEPOT_ADMIN_NAME,
                                          settings.WATTDEPOT_ADMIN_PASSWORD))
                print challenge.wattdepot_server_url

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

    return predicate_mgr.eval_predicates(predicates, user)


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
        page_setting = PageSetting.objects.filter(enabled=True).select_related("page")
        page_widgets = {}

        for ps in page_setting:
            name = ps.page.name
            if not name in page_widgets:
                page_widgets[name] = []

            widgets = page_widgets[name]
            # check if the game this widget belongs to is enabled in the game info
            game_enabled = False
            gss = GameSetting.objects.filter(widget=ps.widget).select_related("game")
            for gs in gss:
                if gs.game.enabled:
                    game_enabled = True
                    break

            if not gss or game_enabled:
                widgets.append(ps)

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


def get_round_start_end(round_name=None):
    """return the start and end date of a round regarding the round_reset."""
    if round_name == "Overall":
        all_round_info = get_all_round_info()
        start = all_round_info["competition_start"]
        end = all_round_info["competition_end"]
    else:
        round_info = get_round_info(round_name)
        if not round_info:
            return None

        end = round_info["end"].date
        if round_info["round_reset"]:
            start = round_info["start"].date
        else:
            # if no round reset, use the competition_start as start date
            start = get_all_round_info()["competition_start"]

    return start, end


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


def get_challenge_start():
    """Returns the start of the earliest round."""
    start = None
    for r in RoundSetting.objects.all():
        if start == None:
            start = r.start
        if start > r.start:
            start = r.start
    return start


def get_challenge_end():
    """Returns the end of the latest round."""
    end = None
    for r in RoundSetting.objects.all():
        if end == None:
            end = r.end
        if end < r.end:
            end = r.end
    return end


def get_designer_challenge_info_models():
    """Returns the challenge info models."""
    return get_challenge_models(_designer_challenge_info_models)


def get_designer_game_info_models():
    """Returns the designer's game related models."""
    game_admins = ()
    for game in GameInfo.objects.all().order_by("priority"):
        if game.name in _designer_game_info_models:
            game_admin = (game.name, game.enabled, game.pk, _designer_game_info_models[game.name],)
            game_admins += (game_admin,)
    return game_admins


def get_admin_challenge_info_models():
    """Returns the Challenge Admin's challenge info models."""
    return get_challenge_models(_admin_challenge_info_models)


def get_admin_game_info_models():
    """Returns the Challenge Admin's game info models."""
    game_admins = ()
    for game in GameInfo.objects.all().order_by("priority"):
        if game.name in _admin_game_info_models:
            game_admin = (game.name, game.enabled, game.pk, _admin_game_info_models[game.name],)
            game_admins += (game_admin,)
    return game_admins


def get_developer_challenge_info_models():
    """Returns the Developer's challenge info models."""
    return get_challenge_models(_developer_challenge_info_models)


def get_developer_game_info_models():
    """Returns the Developer's game info models."""
    game_admins = ()
    for game in GameInfo.objects.all().order_by("priority"):
        if game.name in _developer_game_info_models:
            game_admin = (game.name, game.enabled, game.pk, _developer_game_info_models[game.name],)
            game_admins += (game_admin,)
    return game_admins


def get_admin_models(registry):
    """return the ordered tuple from the model registry."""
    models = ()
    for key in sorted(registry.keys()):
        models += ((key, registry[key]),)
    return models


def get_challenge_models(registry):
    """return the ordered tuple from the model registry, based upon priority."""
    models = ()
    sorted_keys = ()
    for key in registry.keys():
        sorted_keys += ((key, registry[key]['priority']),)
    sorted_keys = sorted(sorted_keys, key=operator.itemgetter(1))
    for key in sorted_keys:
        name = key[0]
        model = registry[key[0]]['models']
        model = sorted(model, key=operator.itemgetter('priority'))
        models += ((name, model),)
    return models


def _get_model_admin_info(model, priority):
    """return the admin info for the model."""
    try:
        tooltip = model.admin_tool_tip
    except AttributeError:
        tooltip = model.__doc__
    url = "%s/%s" % (model._meta.app_label, model._meta.module_name)
    if model._meta.module_name in ['challengesetting', 'scoresetting', 'participationsetting']:
        url = "%s/%s/1" % (model._meta.app_label, model._meta.module_name)
    return {"name": capfirst(model._meta.verbose_name_plural),
            "tooltip": capfirst(tooltip),
            "url": url,
            "priority": priority}


def register_designer_challenge_info_model(group, g_priority, model, priority):
    """Register the model of the challenge info for the designer."""
    register_challenge_model(_designer_challenge_info_models, group, g_priority, model, priority)


def register_designer_game_info_model(game, model):
    """Register the model of the game for the designer."""
    register_admin_model(_designer_game_info_models, game, model)


def register_admin_challenge_info_model(group, g_priority, model, m_priority):
    """Register the model of the challenge info for challenge admin."""
    register_challenge_model(_admin_challenge_info_models, group, g_priority, model, m_priority)


def register_admin_game_info_model(group, model):
    """Register the model of the game for the challenge admin."""
    register_admin_model(_admin_game_info_models, group, model)


def register_developer_challenge_info_model(group, g_priority, model, m_priority):
    """Register the model of the challenge info for challenge admin."""
    register_challenge_model(_developer_challenge_info_models, group, g_priority, model, m_priority)


def register_developer_game_info_model(group, model):
    """Register the model of the game for the challenge admin."""
    register_admin_model(_developer_game_info_models, group, model)


def register_admin_model(registry, group, model, priority=None):
    """Register the model into a registry."""
    model_admin_info = _get_model_admin_info(model, priority)
    if group in registry:
        registry[group] += (model_admin_info,)
    else:
        registry[group] = (model_admin_info,)

        registry[group] = sorted(registry[group], key=operator.itemgetter('priority'))


def register_challenge_model(registry, group, g_priority, model, m_priority):
    """Registers the model into the group with priorities for both group and model."""
    model_admin_info = _get_model_admin_info(model, m_priority)
    if group in registry:
        registry[group]['models'] += (model_admin_info,)
        registry[group]['priority'] = g_priority
    else:
        registry[group] = {}
        registry[group]['models'] = (model_admin_info,)
        registry[group]['priority'] = g_priority

        registry[group]['models'] = sorted(registry[group]['models'], \
                                           key=operator.itemgetter('priority'))


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
