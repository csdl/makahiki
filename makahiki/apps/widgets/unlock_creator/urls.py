'''URls for Unlock Condition Creator.
Created on Jun 10, 2013

@author: Cam Moore
'''

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^predicate_parameters/(?P<predicate>[\w\d\-]+)/$',
        'apps.widgets.unlock_creator.views.predicate_parameters',
        name='predicate_parameters'),
)
