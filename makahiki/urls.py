"""Defines the Main URLS."""
# pylint: disable=E1120

import os
from django.conf import settings
from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.views.generic import TemplateView
from apps.admin.admin import sys_admin_site, challenge_designer_site, \
    challenge_manager_site, developer_site

admin.autodiscover()

urlpatterns = patterns('',
    # Main page.
    url(r'^$', "apps.pages.views.root_index", name="root_index"),

    # page urls
    url(r'^home/$', "apps.pages.views.index", name="home_index"),
    url(r'^help/$', "apps.pages.views.index", name="help_index"),
    url(r'^learn/$', "apps.pages.views.index", name="learn_index"),
    url(r'^profile/$', "apps.pages.views.index", name="profile_index"),
    url(r'^energy/$', "apps.pages.views.index", name="energy_index"),
    url(r'^water/$', "apps.pages.views.index", name="water_index"),
    url(r'^news/$', "apps.pages.views.index", name="news_index"),
    url(r'^win/$', "apps.pages.views.index", name="win_index"),
    url(r'^advanced/$', 'apps.pages.views.index', name="advanced_index"),
    url(r'^status/$', 'apps.pages.views.index', name="status_index"),
    url(r'^sgg_designer/$', 'apps.pages.views.index', name='smartgrid_design'),
    url(r'^pages/clear_cache/$', 'apps.pages.views.clear_cache', name="clear_cache"),

    # system level
    url(r'^log/', include('apps.managers.log_mgr.urls')),
    url(r'^help/', include('apps.widgets.help.urls')),
    url(r'^avatar/', include('apps.lib.avatar.urls')),
    url(r'^facebook/$', include('apps.lib.facebook_api.urls')),

    url(r'^account/cas/login/$', 'apps.lib.django_cas.views.login', name='cas_login'),
    url(r'^account/cas/logout/$', 'apps.lib.django_cas.views.logout', name='cas_logout'),
    url(r'^account/login/$', 'apps.managers.auth_mgr.views.login', name='account_login'),
    url(r'^account/logout/$', 'apps.managers.auth_mgr.views.logout', name='account_logout'),
    url(r'^admin/logout/$', 'apps.managers.auth_mgr.views.logout', name='admin_logout'),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^sys_admin/', include(sys_admin_site.urls)),
    url(r'^challenge_setting_admin/', include(challenge_designer_site.urls)),
    url(r'^challenge_admin/', include(challenge_manager_site.urls)),
    url(r'^developer_admin/', include(developer_site.urls)),
    url(r'^admin/login-as/(?P<user_id>\d+)/$', 'apps.managers.auth_mgr.views.login_as',
        name='account_login_as'),
    url(r'^player/bulk_upload_form/$', 'apps.managers.player_mgr.views.bulk_upload_form',
        name="bulk_upload_form"),
    url(r'^player/bulk_create/$', 'apps.managers.player_mgr.views.bulk_create',
        name="bulk_create"),

    url(r'^landing/$', TemplateView.as_view(template_name='landing.html'),
        name='landing'),
    url(r'^restricted/$', TemplateView.as_view(template_name='restricted.html'),
        name="restricted"),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^browser-check/$', TemplateView.as_view(template_name='browser_check.html'),
        name='browser_check'),
    url(r'^coming-soon/$', TemplateView.as_view(template_name='coming_soon.html'),
        name='coming_soon'),
    url(r'^badge-display/$', TemplateView.as_view(template_name='admin/badge-display.html'),
        name='badge-display'),
    url(r'^theme-display/$', TemplateView.as_view(template_name='theme.html'),
        name="theme-display"),

    url(r'^404/$', 'django.views.defaults.page_not_found'),
    url(r'^500/$', 'django.views.defaults.server_error'),
    )

widgets = settings.INSTALLED_DEFAULT_WIDGET_APPS + \
          settings.INSTALLED_COMMON_WIDGET_APPS + \
          settings.INSTALLED_WIDGET_APPS

for widget in widgets:
    if os.path.isfile(
        "%s/apps/widgets/%s/urls.py" % (settings.PROJECT_ROOT, widget)):
        urlpatterns += patterns('',
            (r'^%s/' % widget, include('apps.widgets.%s.urls' % widget)), )

# use django to serve static files FOR NOW
urlpatterns += patterns('',
    (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}), )

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT}), )
