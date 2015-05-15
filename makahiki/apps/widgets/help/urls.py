"""Provides the URL pattern for help topics."""

from django.conf.urls import url, patterns

urlpatterns = patterns('', url(r'^(?P<category>\w+)/(?P<slug>[\w\d\-]+)/$',
                               'apps.widgets.help.views.topic',
                               name='help_topic'))
