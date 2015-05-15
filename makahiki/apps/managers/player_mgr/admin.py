"""Defines the class for administration of players."""
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.models import Profile
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site


class ProfileAdminInline(admin.StackedInline):
    """Admin configuration for Profiles."""
    model = Profile
    fk_name = 'user'
    can_delete = False


class MakahikiUserAdmin(UserAdmin):
    """User Admin."""
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email',
                                      'is_active', 'is_superuser', 'is_staff',
                                     )}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )

    list_display = ('username', 'first_name', 'last_name', 'team',
                    'display_name', 'points', 'is_active', 'is_superuser', 'is_ra',
                    'setup_complete', 'referred_by')

    list_filter = ('is_active', 'is_superuser', 'profile__is_ra')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__name')
    ordering = ('username',)

    filter_horizontal = ()

    actions = ["set_active", "set_inactive"]
    page_text = "Click on the name in the Username column to edit a player's " + \
                "password, personal information, roles, and site administration groups.  " + \
                "Click on the name in the Profile column to edit a player's display name, " + \
                "team, badges, etc. " + \
                "<span style=\"font-weight:bold\">A player's username cannot contain uppercase" \
                " letters.</span>"

    inlines = (ProfileAdminInline, )

    def set_active(self, request, queryset):
        """set the active flag priority."""
        _ = request
        for obj in queryset:
            obj.is_active = True
            obj.save()
    set_active.short_description = "Activate the selected users."

    def set_inactive(self, request, queryset):
        """set the active flag priority."""
        _ = request
        for obj in queryset:
            obj.is_active = False
            obj.save()
    set_inactive.short_description = "Deactivate the selected users."

    def display_name(self, obj):
        """return the user name."""
        return obj.profile.name
    display_name.short_description = 'Display Name'

    def team(self, obj):
        """return the user name."""
        return obj.profile.team
    team.short_description = 'Team'

    def is_ra(self, obj):
        """return the user name."""
        return obj.profile.is_ra
    is_ra.short_description = 'Is RA'

    def points(self, obj):
        """return the user name."""
        return obj.profile.points()
    points.short_description = 'Points'

    def setup_complete(self, obj):
        """return the user name."""
        return obj.profile.setup_complete
    setup_complete.short_description = 'Setup completed'

    def referred_by(self, obj):
        """return the name of the referrer."""
        return obj.profile.referring_user
    referred_by.short_description = 'Referred by'

User.__doc__ = "Represents a player in the system."
User.admin_tool_tip = "Challenge Players. They must be defined before anyone can play."

challenge_designer_site.register(User, MakahikiUserAdmin)
challenge_manager_site.register(User, MakahikiUserAdmin)
developer_site.register(User, MakahikiUserAdmin)

challenge_mgr.register_designer_challenge_info_model("Players", 2, User, 2)
challenge_mgr.register_developer_challenge_info_model("Players", 2, User, 3)
