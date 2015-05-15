"""Specify the URL pattern to be associated with logging."""

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<obj_type>[\w\d\-]+)/(?P<obj>[\w\d\-]+)/(?P<action>[\w\d\-]+)/$',
        'apps.managers.log_mgr.views.log_ajax', name="logger_log_ajax"),
)
