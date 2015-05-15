"""Urls definition for notification widget."""

from django.conf.urls import url, patterns

urlpatterns = patterns('apps.widgets.notifications.views',
    url(r'^(\d+)/read/$', 'read', name="notifications_read"),
)
