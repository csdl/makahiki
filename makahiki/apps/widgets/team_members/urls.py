"""specify team member directory url"""

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^team-members/$', 'apps.widgets.team_members.views.team_members',
        name="news_team_members"),
)
