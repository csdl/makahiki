"""Url definitions for the home page and first login wizard."""

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^restricted/$', 'apps.widgets.home.views.restricted', name="home_restricted"),
    url(r'^setup/welcome/$', 'apps.widgets.home.views.setup_welcome', name="setup_welcome"),
    url(r'^setup/terms/$', 'apps.widgets.home.views.terms', name="setup_terms"),
    url(r'^setup/referral/$', 'apps.widgets.home.views.referral', name='setup_referral'),
    url(r'^setup/profile/$', 'apps.widgets.home.views.setup_profile', name="setup_profile"),
    url(r'^setup/activity/$', 'apps.widgets.home.views.setup_activity', name="setup_activity"),
    url(r'^setup/question/$', 'apps.widgets.home.views.setup_question', name="setup_question"),
    url(r'^setup/complete/$', 'apps.widgets.home.views.setup_complete', name="setup_complete"),
)
