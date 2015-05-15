"""urls definition for status widget."""

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^analysis/(?P<command>[\w]+)/$',
        'apps.widgets.status.views.analysis_view',
        name="status_analysis"),
    )
