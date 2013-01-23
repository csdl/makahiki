"""Implements the admin interface for game settings."""
from django.contrib import admin
from django.db import models
from django.forms.widgets import Textarea
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.challenge_mgr.models import ChallengeSetting, RoundSetting, PageSetting, \
    PageInfo, Sponsor, UploadImage, GameSetting, GameInfo


class PageSettingInline(admin.TabularInline):
    """PageSettingInline admin."""
    model = PageSetting
    #can_delete = False
    fields = ['game', 'widget', 'enabled', ]
    #readonly_fields = ['widget', ]
    extra = 0

    #def has_add_permission(self, request):
    #    return False


class PageInfoAdmin(admin.ModelAdmin):
    """PageSetting administrator interface definition."""
    list_display = ["name", "unlock_condition", "priority"]

    fieldsets = (
        (None,
            {"fields":
                  (("name", "label"),
                   "title",
                   "introduction",
                   "unlock_condition",
                   ("url", "priority"), )
            }),
    )

    inlines = [PageSettingInline]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 70})},
        }

admin.site.register(PageInfo, PageInfoAdmin)


class PageSettingAdmin(admin.ModelAdmin):
    """PageSetting administrator interface definition."""
    list_display = ["page", "game", "widget", "enabled"]
    list_editable = ["game", "widget", "enabled"]

admin.site.register(PageSetting, PageSettingAdmin)


class GameSettingInline(admin.TabularInline):
    """PageSettingInline admin."""
    model = GameSetting
    fields = ['widget', 'enabled', ]
    extra = 0


class GameInfoAdmin(admin.ModelAdmin):
    """PageSetting administrator interface definition."""
    list_display = ["name", "enabled", "priority"]
    fieldsets = (
        (None,
            {"fields":
                  (("name", "enabled"), "priority")
            }),
    )
    inlines = [GameSettingInline]

admin.site.register(GameInfo, GameInfoAdmin)


class RoundSettingAdmin(admin.ModelAdmin):
    """PageSetting administrator interface definition."""
    list_display = ["name", "start", "end", "round_reset", "display_scoreboard"]

admin.site.register(RoundSetting, RoundSettingAdmin)


class SponsorsInline(admin.TabularInline):
    """SponsorsInline admin."""
    model = Sponsor
    extra = 0


class ChallengeSettingAdmin(admin.ModelAdmin):
    """ChallengeSetting administrator interface definition."""

    fieldsets = (
        ("Challenge",
            {"description": "<div class='content-box'>I have no idea what this does<br>does it look ok?</div>",
             "fields":
                  (("name", "location"),
                   ("logo", "domain"),
                   ("team_label", "theme"),
                  )}),
        ("Authentication",
            {"fields":
                  (("use_cas_auth", "cas_server_url", "cas_auth_text"),
                   ("use_ldap_auth", "ldap_server_url", "ldap_search_base", "ldap_auth_text"),
                   ("use_internal_auth", "internal_auth_text"),
                  )}),
        ("WattDepot server for real time energy data",
            {"fields":
                  ("wattdepot_server_url", )}),
        ("Email",
             {"fields":
                  ("email_enabled",
                   "contact_email",
                   ("email_host", "email_port", "email_use_tls"), )}),
        ("Landing Page",
             {"fields":
                  ("landing_slogan",
                   "landing_introduction",
                   "landing_participant_text",
                   "landing_non_participant_text", )}),
        ("About Page",
            {"fields":
                  ("about_page_text", )}),
    )

    inlines = [SponsorsInline]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
        }
    page_text = "Under normal circumstances, there is only one challenge instance per system.  <br>" +\
"By default, this is called 'Kukui Cup/UH'. <br> " +\
"Select this instance; you will be able to change its name below."

admin.site.register(ChallengeSetting, ChallengeSettingAdmin)
admin.site.register(UploadImage)

challenge_mgr.register_site_admin_model("Challenge", ChallengeSetting)
challenge_mgr.register_site_admin_model("Challenge", RoundSetting)
challenge_mgr.register_sys_admin_model("Other Settings", PageInfo)
challenge_mgr.register_sys_admin_model("Other Settings", GameInfo)

from djcelery.models import CrontabSchedule, PeriodicTask, IntervalSchedule
challenge_mgr.register_sys_admin_model("Celery Scheduler", CrontabSchedule)
challenge_mgr.register_sys_admin_model("Celery Scheduler", IntervalSchedule)
challenge_mgr.register_sys_admin_model("Celery Scheduler", PeriodicTask)
