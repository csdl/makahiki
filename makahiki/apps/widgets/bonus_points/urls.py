"""urls definition for bonus_points widget."""
'''
Created on Aug 5, 2012

@author: Cam Moore
'''

from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^bonus_code/$',
        'apps.widgets.bonus_points.views.bonus_code',
        name="bonus_points_code"),
    url(r'^view_codes/$',
        'apps.widgets.bonus_points.view_bonus_points.view_codes',
        name='bonus_view_codes'),
    url(r'^generate_codes/$',
        'apps.widgets.bonus_points.views.generate_codes_form',
        name="generate_bonus_points"),
    url(r'^bonus_code/add$',
        'apps.widgets.bonus_points.views.generate_codes',
        name="bonus_codes_add"),
)
