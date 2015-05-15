"""Prize administrative interface."""
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib import admin
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.team_mgr.models import Team
from apps.widgets.notifications.models import UserNotification, NoticeTemplate

from apps.widgets.prizes.models import Prize
from django.http import HttpResponseRedirect
from django.db.utils import IntegrityError
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site


class PrizeAdmin(admin.ModelAdmin):
    """raffle admin"""
    list_display = ('round', 'title', 'value', 'award_to', 'competition_type', 'place',
                    'winner', 'notice_sent')
    list_display_links = ('title',)
    list_filter = ['round']
    actions = ["notify_winner", "change_round", "copy_prize"]

    def _send_winner_notification(self, prize, leader):
        """send notification."""
        if leader and not self._notification_exists(prize, leader):
            # Notify winner using the template.
            template = NoticeTemplate.objects.get(notice_type='prize-winner')
            message = template.render({'PRIZE': prize})
            UserNotification.create_info_notification(leader.user, message, True, prize)

            challenge = challenge_mgr.get_challenge()
            subject = "[%s] Congratulations, you won a prize!" % challenge.name
            UserNotification.create_email_notification(
                leader.user.email, subject, message, message)

    def _notification_exists(self, prize, leader):
        """returns true if the notification already created."""
        return prize.competition_type == "points" and leader and UserNotification.objects.filter(
            recipient=leader.user,
            content_type=ContentType.objects.get(model="prize"),
            object_id=prize.id).exists()

    def notify_winner(self, request, queryset):
        """pick winner."""
        _ = request
        for obj in queryset:
            if obj.award_to == 'individual_overall':
                leader = obj.leader()
                self._send_winner_notification(obj, leader)
            elif obj.award_to == 'individual_team':
                teams = Team.objects.all()
                for team in teams:
                    leader = obj.leader(team=team)
                    self._send_winner_notification(obj, leader)
        self.message_user(request, "Winners notification sent.")

    notify_winner.short_description = "Notify winner for selected prizes."

    def change_round(self, request, queryset):
        """Change the round for the selected Prizes."""
        _ = queryset
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse("bulk_prize_round_change",
                                            args=("prize", "round",)) +
                                     "?ids=%s" % (",".join(selected)))
    change_round.short_description = "Change the round"

    def copy_prize(self, request, queryset):
        """Copy the selected Prize(s)."""
        _ = request
        for obj in queryset:
            obj.id = None
            obj.round = None
            try:
                obj.save()
            except IntegrityError:
                # How do we indicate an error to the admin?
                pass
    copy_prize.short_description = "Copy selected Prize(s)"

    def winner(self, obj):
        """return the winner and link to pickup form."""
        if obj.award_to == 'individual_overall' and obj.competition_type == "points":
            leader = obj.leader()
            if leader:
                return "%s (<a href='%s'>View pickup form</a>)" % (leader,
                    reverse('prize_view_form', args=(obj.pk, leader.user.pk)))
        elif obj.award_to == 'individual_team':
            return "<a href='%s'>View winners</a>" % reverse('prize_team_winners',
                                                             args=(obj.pk, ))
        else:
            leader = obj.leader()
            return leader

    winner.allow_tags = True
    winner.short_description = 'Current Winner'

    def notice_sent(self, obj):
        """return True if the notification had been sent."""
        if obj.award_to == 'individual_overall':
            leader = obj.leader()
            return self._notification_exists(obj, leader)
        elif obj.award_to == 'individual_team':
            teams = Team.objects.all()
            for team in teams:
                leader = obj.leader(team=team)
                return self._notification_exists(obj, leader)
        else:
            return "N/A"

    notice_sent.short_description = 'Winner Notice Sent'


admin.site.register(Prize, PrizeAdmin)
challenge_designer_site.register(Prize, PrizeAdmin)
challenge_manager_site.register(Prize, PrizeAdmin)
developer_site.register(Prize, PrizeAdmin)
challenge_mgr.register_designer_game_info_model("Top Score Game", Prize)
challenge_mgr.register_developer_game_info_model("Top Score Game", Prize)
