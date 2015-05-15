"""urls"""
from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^more_posts/user/$', 'apps.widgets.wallpost.user_wallpost.views.more_posts',
        name='news_more_user_posts'),
    url(r'^more_posts/system/$', 'apps.widgets.wallpost.system_wallpost.views.more_posts',
        name='news_more_system_posts'),
    url(r'^post/$', 'apps.widgets.wallpost.views.post', name="news_post"),
)
