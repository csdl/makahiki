import urllib

from django import template
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from hashlib import md5

from apps.lib.avatar import AVATAR_DEFAULT_NO_URL, AVATAR_DEFAULT_YES_URL, AVATAR_GRAVATAR_BACKUP,\
    AVATAR_DEFAULT_NO_LG_URL
from apps.managers.score_mgr import score_mgr

register = template.Library()

def avatar_url(user, size=80, first_login=False):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return AVATAR_DEFAULT_NO_URL
    avatars = user.avatar_set.order_by('-date_uploaded')
    if avatars:
        avt = avatars[0]
    else:
        avt = None
    if avt is not None:
        if not avt.thumbnail_exists(size):
            avt.create_thumbnail(size)
        return avt.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                md5(user.email).hexdigest(),
                urllib.urlencode({'s': str(size)}),)
        else:
            if user.profile.setup_complete:
                return AVATAR_DEFAULT_YES_URL
            else:
                if size > 60:
                    if first_login:
                        return AVATAR_DEFAULT_YES_URL
                    else:
                        return AVATAR_DEFAULT_NO_LG_URL
                else:
                    if first_login:
                        return AVATAR_DEFAULT_YES_URL
                    else:
                        return AVATAR_DEFAULT_NO_URL
register.simple_tag(avatar_url)

def avatar(user, size=80, *args, **kwargs):
    if 'first_login' in kwargs:
        first_login = kwargs['first_login']
    else:
        first_login = False
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size, first_login)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_NO_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size, first_login)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(avatar)

def render_avatar(avt, size=80):
    if not avt.thumbnail_exists(size):
        avt.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avt.avatar_url(size), str(avatar), size, size)
register.simple_tag(render_avatar)
