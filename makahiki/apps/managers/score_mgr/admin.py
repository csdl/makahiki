"""Administrator interface to score_mgr."""
from django.contrib import admin
from apps.managers.challenge_mgr import challenge_mgr

from apps.managers.score_mgr.models import ScoreSetting, ScoreboardEntry, PointsTransaction, \
    ReferralSetting


class PointsTransactionAdmin(admin.ModelAdmin):
    """PointsTransaction administrator interface definition."""
    list_display = ["user", "transaction_date", "points", "message"]
    search_fields = ["user__username", "message"]
    date_hierarchy = "transaction_date"

admin.site.register(PointsTransaction, PointsTransactionAdmin)


class ScoreboardEntryAdmin(admin.ModelAdmin):
    """PointsTransaction administrator interface definition."""
    list_display = ["round_name", "profile", "points", "last_awarded_submission"]
    search_fields = ["profile__name", "profile__user__username"]
    list_filter = ["round_name"]

admin.site.register(ScoreboardEntry, ScoreboardEntryAdmin)


class ScoreSettingAdmin(admin.ModelAdmin):
    """PointsTransaction administrator interface definition."""
    list_display = ["setup_points", "active_threshold_points",
                    "signup_bonus_points", "noshow_penalty_points", "feedback_bonus_points", ]

admin.site.register(ScoreSetting, ScoreSettingAdmin)


class ReferralSettingAdmin(admin.ModelAdmin):
    """PointsTransaction administrator interface definition."""
    list_display = ["normal_referral_points", "super_referral_points",
                    "mega_referral_points", "start_dynamic_bonus", ]

admin.site.register(ReferralSetting, ReferralSettingAdmin)


challenge_mgr.register_site_admin_model("Challenge", ScoreSetting)
challenge_mgr.register_game_admin_model("Referral Game Mechanics", ReferralSetting)
challenge_mgr.register_sys_admin_model("Status", PointsTransaction)
challenge_mgr.register_sys_admin_model("Status", ScoreboardEntry)
