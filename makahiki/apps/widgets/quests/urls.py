"""Quest related urls."""

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)/accept/$', 'apps.widgets.quests.views.accept', name="quests_accept"),
    url(r'^(?P<slug>[-\w]+)/opt-out/$', 'apps.widgets.quests.views.opt_out', name="quests_opt_out"),
    url(r'^(?P<slug>[-\w]+)/cancel/$', 'apps.widgets.quests.views.cancel', name="quests_cancel"),
)
