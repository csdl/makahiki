"""urls for raffle widget"""
from django.conf.urls import url, patterns

urlpatterns = patterns('',
    url(r'^(\d+)/add_ticket/$', 'apps.widgets.raffle.views.add_ticket',
        name="raffle_add_ticket"),
    url(r'^(\d+)/remove_ticket/$', 'apps.widgets.raffle.views.remove_ticket',
        name="raffle_remove_ticket"),
    url(r'^(\d+)/view-form/$', 'apps.widgets.raffle.views.raffle_form',
        name="raffle_view_form"),
    url(r'^prize_list/$', 'apps.widgets.raffle.views.raffle_prize_list',
        name="raffle_prize_list"),
    url(r'^pick_winner/$', 'apps.widgets.raffle.views.pick_winner',
        name="raffle_pick_winner"),
    url(r'^notify_winner/$', 'apps.widgets.raffle.views.notify_winner',
        name="raffle_notify_winner"),
    url(r'^summary/(?P<round_name>[\w\d\-]+)/$', 'apps.widgets.raffle.views.prize_summary',
        name="prize_summary"),
    url(r'^bulk_change/(?P<action_type>[\w]+)/(?P<attribute>[\w]+)/$',
        'apps.widgets.raffle.views.bulk_round_change',
        name="bulk_raffle_round_change"),
)
