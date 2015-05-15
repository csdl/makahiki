from django.conf.urls import patterns, url

urlpatterns = patterns('apps.lib.avatar.views',
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
    url('^change/upload-fb/$', 'upload_fb', name='avatar_upload_fb'),
)
