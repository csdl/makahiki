'''
Created on May 7, 2013

@author: Cam Moore
'''
from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/$',
        'apps.widgets.education.views.view_action',
        name='education_task'),
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/add/$',
        'apps.widgets.education.views.add_action',
        name='education_add_task'),
    url(r'^(?P<action_type>[\w]+)/(?P<slug>[\w\d\-]+)/drop/$',
        'apps.widgets.education.views.drop_action',
        name='education_drop_task'),

)
