"""Raffle widget administration"""
import random

from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.notifications.models import NoticeTemplate, UserNotification

from apps.widgets.raffle.models import RafflePrize, RaffleTicket


class RafflePrizeAdminForm(forms.ModelForm):
    """raffle admin form"""
    class Meta:
        """meta"""
        model = RafflePrize

    def __init__(self, *args, **kwargs):
        """Override to have a link to winner of the prize."""
        super(RafflePrizeAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.winner:
            self.fields['winner'].help_text = 'View pickup <a href="%s">form</a>' % reverse(
                'raffle_view_form', args=(self.instance.id,))
        else:
            self.fields['winner'].help_text = ''


class RaffleTicketInline(admin.TabularInline):
    """SponsorsInline admin."""
    model = RaffleTicket
    extra = 0
    can_delete = False
    readonly_fields = ['user', ]

    def has_add_permission(self, request):
        return False


class RafflePrizeAdmin(admin.ModelAdmin):
    """raffle admin"""
    form = RafflePrizeAdminForm
    list_display = ('title', 'round_name', 'value', 'winner_form', 'notice_sent')
    actions = ["pick_winner", "notify_winner"]
    inlines = [RaffleTicketInline]
    list_filter = ['round_name']

    def pick_winner(self, request, queryset):
        """pick winner."""
        _ = request
        for obj in queryset:
            if not obj.winner:
                # Randomly order the tickets and then pick a random ticket.
                tickets = obj.raffleticket_set.order_by("?").all()
                if tickets.count():
                    ticket = random.randint(0, tickets.count() - 1)
                    user = tickets[ticket].user
                    obj.winner = user
                    obj.save()
        self.message_user(request, "Winners shown in the winner column.")

    pick_winner.short_description = "Pick winner for selected raffle prizes."

    def notify_winner(self, request, queryset):
        """pick winner."""
        _ = request
        for obj in queryset:
            if obj.winner and not self.notice_sent(obj):
                # Notify winner using the template.
                template = NoticeTemplate.objects.get(notice_type='raffle-winner')
                message = template.render({'PRIZE': obj})
                UserNotification.create_info_notification(obj.winner, message, True, obj)

                challenge = challenge_mgr.get_challenge()
                subject = "[%s] Congratulations, you won a prize!" % challenge.competition_name
                UserNotification.create_email_notification(
                    obj.winner.email, subject, message, message)

        self.message_user(request, "Winners notification sent.")

    notify_winner.short_description = "Notify winner for selected raffle prizes."

    def winner_form(self, obj):
        """return the winner and link to pickup form."""
        if obj.winner:
            return "%s (<a href='%s'>View pickup form</a>)" % (obj.winner,
            reverse('raffle_view_form', args=(obj.pk,)))
        else:
            return '(None)'
    winner_form.allow_tags = True
    winner_form.short_description = 'Winner'

    def notice_sent(self, obj):
        """return True if the notification had been sent."""
        return UserNotification.objects.filter(
            recipient=obj.winner,
            content_type=ContentType.objects.get(model="raffleprize"),
            object_id=obj.id).exists()
    notice_sent.short_description = 'Winner Notice Sent'

admin.site.register(RafflePrize, RafflePrizeAdmin)
challenge_mgr.register_game_admin_model("Raffle Game", RafflePrize)
