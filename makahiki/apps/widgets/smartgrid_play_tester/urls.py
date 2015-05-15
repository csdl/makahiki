'''Defines the URLs for the Smart Grid Play Tester.
Created on Jun 23, 2013

@author: Cam Moore
'''

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^$',
        'apps.widgets.smartgrid_play_tester.views.view',
        name='tester_view'),
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/$',
        'apps.widgets.smartgrid_play_tester.views.view_action',
        name='tester_view_action'),
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/add/$',
        'apps.widgets.smartgrid_play_tester.views.add_action',
        name='tester_activity_add'),
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/drop/$',
        'apps.widgets.smartgrid_play_tester.views.drop_action',
        name='tester_activity_drop'),
    )
