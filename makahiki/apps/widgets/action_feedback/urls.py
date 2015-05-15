"""urls definition for action_feedback widget."""

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/feedback/$',
        'apps.widgets.action_feedback.views.action_feedback',
        name='add_activity_feedback'),
     url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/view_feedback/$',
        'apps.widgets.action_feedback.views.view_feedback',
        name='view_feedback'),
                      )
