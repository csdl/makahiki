"""Urls definition for my_info widget."""

from django.conf.urls import url, patterns

urlpatterns = patterns('apps.widgets.my_info.views',
    url(r'^save/$', 'save', name="profile_save"),
)
