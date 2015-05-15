"""Raffle widget administration"""
import random

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.notifications.models import NoticeTemplate, UserNotification

from apps.widgets.raffle.models import RafflePrize, RaffleTicket
from django.http import HttpResponseRedirect
from django.db.utils import IntegrityError
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site


class RaffleTicketInline(admin.TabularInline):
    """SponsorsInline admin."""
    model = RaffleTicket
    extra = 0
    can_delete = False
    readonly_fields = ['user', 'created_at']

    def has_add_permission(self, request):
        return False


class RafflePrizeAdmin(admin.ModelAdmin):
    """raffle admin"""
    list_display = ('round', 'title', 'value', 'winner_form', 'notice_sent')
    list_display_links = ('title',)
    ordering = ('round', 'value', 'title')
    actions = ["pick_winner", "notify_winner", "change_round", "copy_raffle_prize"]
    inlines = [RaffleTicketInline]
    list_filter = ['round']

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
                subject = "[%s] Congratulations, you won a prize!" % challenge.name
                UserNotification.create_email_notification(
                    obj.winner.email, subject, message, message)

        self.message_user(request, "Winners notification sent.")

    notify_winner.short_description = "Notify winner for selected raffle prizes."

    def change_round(self, request, queryset):
        """Change the round for the selected Raffle Prizes."""
        _ = queryset
        selected = request.RafflePrize.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse("bulk_raffle_round_change",
                                            args=("raffleprize", "round",)) +
                                    "?ids=%s" % (",".join(selected)))
    change_round.short_description = "Change the round"

    def copy_raffle_prize(self, request, queryset):
        """Copies the selected Raffle Prizes."""
        _ = request
        for obj in queryset:
            obj.id = None
            try:
                obj.save()
            except IntegrityError:
                # How do we indicate an error to the admin?
                pass
    copy_raffle_prize.short_description = "Copy selected Raffle Prizes"

    def winner_form(self, obj):
        """return the winner and link to pickup form."""
        if obj.winner:
            return "%s (<a href='%s'>View pickup form</a>)" % (obj.winner.profile,
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
challenge_designer_site.register(RafflePrize, RafflePrizeAdmin)
challenge_manager_site.register(RafflePrize, RafflePrizeAdmin)
developer_site.register(RafflePrize, RafflePrizeAdmin)
challenge_mgr.register_designer_game_info_model("Raffle Game", RafflePrize)
challenge_mgr.register_developer_game_info_model("Raffle Game", RafflePrize)
