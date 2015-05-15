"""Admin definition for Smart Grid Game widget."""
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import markdown
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.smartgrid.models import ActionMember, Activity, ColumnName, Event, \
                                     Commitment, ConfirmationCode, TextPromptQuestion, \
                                     QuestionChoice, Level, Action, Filler, \
                                     EmailReminder, TextReminder, ColumnGrid, Grid
from apps.widgets.smartgrid.views import action_admin, action_admin_list

from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django.forms import TextInput, Textarea
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.utils import IntegrityError
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site
from apps.managers.predicate_mgr import predicate_mgr


class ActionAdmin(admin.ModelAdmin):
    """abstract admin for action."""
    actions = ["delete_selected", "copy_action"]
    list_display = ["slug", "title", "type", "point_value"]
    search_fields = ["slug", "title"]
    list_filter = ['type', ]

    def delete_selected(self, request, queryset):
        """override the delete selected."""
        _ = request
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Delete the selected objects."

    def copy_action(self, request, queryset):
        """Copy the selected Actions."""
        _ = request
        for obj in queryset:
            obj.id = None
            slug = obj.slug
            obj.slug = slug + "-copy"
            try:
                obj.save()
            except IntegrityError:
                # How do we indicate an error to the admin?
                pass
    copy_action.short_description = "Copy selected Action(s)"

    def get_urls(self):
        return redirect_urls(self, "change")

admin.site.register(Action, ActionAdmin)
challenge_designer_site.register(Action, ActionAdmin)
challenge_manager_site.register(Action, ActionAdmin)
developer_site.register(Action, ActionAdmin)
challenge_mgr.register_designer_game_info_model("Smart Grid Game", Action)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", Action)


class ActivityAdminForm(forms.ModelForm):
    """Activity Admin Form."""
    class Meta:
        """Meta"""
        model = Activity

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def clean(self):
        """
        Validates the admin form data based on a set of constraints.
            1.  If the verification type is "image" or "code", then a confirm prompt is required.
            2.  Publication date must be before expiration date.
            3.  Either points or a point range needs to be specified.
        """

        super(ActivityAdminForm, self).clean()

        # Data that has passed validation.
        cleaned_data = self.cleaned_data

        #1 Check the verification type.
        confirm_type = cleaned_data.get("confirm_type")
        prompt = cleaned_data.get("confirm_prompt")
        if confirm_type != "text" and len(prompt) == 0:
            self._errors["confirm_prompt"] = ErrorList(
                [u"This confirmation type requires a confirmation prompt."])
            del cleaned_data["confirm_type"]
            del cleaned_data["confirm_prompt"]

        #2 Publication date must be before the expiration date.
        if "pub_date" in cleaned_data and "expire_date" in cleaned_data:
            pub_date = cleaned_data.get("pub_date")
            expire_date = cleaned_data.get("expire_date")

            if expire_date and pub_date >= expire_date:
                self._errors["expire_date"] = ErrorList(
                    [u"The expiration date must be after the pub date."])
                del cleaned_data["expire_date"]

        #3 Either points or a point range needs to be specified.
        points = cleaned_data.get("point_value")
        point_range_start = cleaned_data.get("point_range_start")
        point_range_end = cleaned_data.get("point_range_end")
        if not points and not (point_range_start or point_range_end):
            self._errors["point_value"] = ErrorList(
                [u"Either a point value or a range needs to be specified."])
            del cleaned_data["point_value"]
        elif points and (point_range_start or point_range_end):
            self._errors["point_value"] = ErrorList(
                [u"Please specify either a point_value or a range."])
            del cleaned_data["point_value"]
        elif not points:
            point_range_start = cleaned_data.get("point_range_start")
            point_range_end = cleaned_data.get("point_range_end")
            if not point_range_start:
                self._errors["point_range_start"] = ErrorList(
                    [u"Please specify a start value for the point range."])
                del cleaned_data["point_range_start"]
            elif not point_range_end:
                self._errors["point_range_end"] = ErrorList(
                    [u"Please specify a end value for the point range."])
                del cleaned_data["point_range_end"]
            elif point_range_start >= point_range_end:
                self._errors["point_range_start"] = ErrorList(
                    [u"The start value must be less than the end value."])
                del cleaned_data["point_range_start"]
                del cleaned_data["point_range_end"]

        return cleaned_data

    def save(self, *args, **kwargs):
        """save"""
        activity = super(ActivityAdminForm, self).save(*args, **kwargs)
        activity.type = 'activity'
        activity.save()
        cache_mgr.clear()

        # If the activity's confirmation type is text, make sure to save the questions.
        if self.cleaned_data.get("confirm_type") == "text":
            self.save_m2m()

        return activity


class TextQuestionInlineFormSet(BaseInlineFormSet):
    """Custom formset model to override validation."""

    def clean(self):
        """Validates the form data and checks if the activity confirmation type is text."""

        # Form that represents the activity.
        activity = self.instance
        if not activity.pk:
            # If the activity is not saved, we don't care if this validates.
            return

        # Count the number of questions.
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass

        if activity.confirm_type == "text" and count == 0:
            # Why did I do this?
            # activity.delete()
            raise forms.ValidationError(
                "At least one question is required if the activity's confirmation type is text.")

        elif activity.confirm_type != "text" and count > 0:
            # activity.delete()
            raise forms.ValidationError("Questions are not required for this confirmation type.")


class TextQuestionInline(admin.TabularInline):
    """Text Question admin."""
    model = TextPromptQuestion
    fieldset = (
        (None, {
            'fields': ('question', 'answer'),
            })
        )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
        }

    extra = 1
    formset = TextQuestionInlineFormSet


class ActivityAdmin(admin.ModelAdmin):
    """Activity Admin"""
    fieldsets = (
        ("Basic Information",
         {'fields': (('name', ),
                     ('slug', 'related_resource'),
                     ('title', 'expected_duration'),
                     'image',
                     'description',
                     ('video_id', 'video_source'),
                     'embedded_widget',
                     ('pub_date', 'expire_date'),
                     ('unlock_condition', 'unlock_condition_text'),
                     )}),
        ("Points",
         {"fields": (("point_value", "social_bonus"), ("point_range_start", "point_range_end"), )}),
        ("Admin Note", {'fields': ('admin_note',)}),
        ("Confirmation Type", {'fields': ('confirm_type', 'confirm_prompt')}),
    )
    prepopulated_fields = {"slug": ("name",)}

    form = ActivityAdminForm
    inlines = [TextQuestionInline]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")


admin.site.register(Activity, ActivityAdmin)
challenge_designer_site.register(Activity, ActivityAdmin)
challenge_manager_site.register(Activity, ActivityAdmin)
developer_site.register(Activity, ActivityAdmin)


class CommitmentAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = Commitment

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def save(self, *args, **kwargs):
        """save"""
        commitment = super(CommitmentAdminForm, self).save(*args, **kwargs)
        commitment.type = 'commitment'
        commitment.save()
        cache_mgr.clear()

        return commitment


class CommitmentAdmin(admin.ModelAdmin):
    """Commitment Admin."""
    fieldsets = (
        ("Basic Information", {
            'fields': (('name', ),
                       ('slug', 'related_resource'),
                       ('title', 'commitment_length'),
                       'image',
                       'description',
                       'unlock_condition', 'unlock_condition_text',
                       ),
            }),
        ("Points", {"fields": (("point_value", 'social_bonus'), )}),
        )

    form = CommitmentAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        """override the url definition."""
        return redirect_urls(self, "changelist")


admin.site.register(Commitment, CommitmentAdmin)
challenge_designer_site.register(Commitment, CommitmentAdmin)
challenge_manager_site.register(Commitment, CommitmentAdmin)
developer_site.register(Commitment, CommitmentAdmin)


class EventAdminForm(forms.ModelForm):
    """Event Admin Form."""

    class Meta:
        """Meta"""
        model = Event

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def clean(self):
        """
        Validates the admin form data based on a set of constraints.

            1.  Events must have an event date.
            2.  Publication date must be before expiration date.
        """

        # Data that has passed validation.
        cleaned_data = self.cleaned_data

        #1 Check that an event has an event date.
        event_date = cleaned_data.get("event_date")
        has_date = "event_date" in cleaned_data   # Check if this is in the data dict.
        if has_date and not event_date:
            self._errors["event_date"] = ErrorList([u"Events require an event date."])
            del cleaned_data["event_date"]

        #2 Publication date must be before the expiration date.
        if "pub_date" in cleaned_data and "expire_date" in cleaned_data:
            pub_date = cleaned_data.get("pub_date")
            expire_date = cleaned_data.get("expire_date")

            if expire_date and pub_date >= expire_date:
                self._errors["expire_date"] = ErrorList(
                    [u"The expiration date must be after the pub date."])
                del cleaned_data["expire_date"]

        return cleaned_data

    def save(self, *args, **kwargs):
        """save"""
        event = super(EventAdminForm, self).save(*args, **kwargs)
        event.type = 'event'
        event.save()

        cache_mgr.clear()

        return event


class EventAdmin(admin.ModelAdmin):
    """Event Admin"""
    fieldsets = (
        ("Basic Information",
         {'fields': (('name', ),
                     ('slug', 'related_resource'),
                     ('title', 'expected_duration'),
                     'image',
                     'description',
                     ('pub_date', 'expire_date'),
                     ('event_date', 'event_location', 'event_max_seat'),
                     ('unlock_condition', 'unlock_condition_text'),
                     )}),
        ("Points", {"fields": (("point_value", "social_bonus"),)}),
        )

    form = EventAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")


admin.site.register(Event, EventAdmin)
challenge_designer_site.register(Event, EventAdmin)
challenge_manager_site.register(Event, EventAdmin)
developer_site.register(Event, EventAdmin)


class FillerAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = Filler

    def save(self, *args, **kwargs):
        """save"""
        filler = super(FillerAdminForm, self).save(*args, **kwargs)
        filler.type = 'filler'
        filler.unlock_condition = "False"
        filler.unlock_condition_text = "This cell is here only to fill out the grid. " \
                                       "There is no action associated with it."
        filler.save()
        cache_mgr.clear()

        return filler


class FillerAdmin(admin.ModelAdmin):
    """Commitment Admin."""
    fieldsets = (
        ("Basic Information", {
            'fields': (('name', ),
                       ('slug', ),
                       ('title', ),
                       ),
            }),
        )
    prepopulated_fields = {"slug": ("name",)}

    form = FillerAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        """override the url definition."""
        return redirect_urls(self, "changelist")


admin.site.register(Filler, FillerAdmin)
challenge_designer_site.register(Filler, FillerAdmin)
challenge_manager_site.register(Filler, FillerAdmin)
developer_site.register(Filler, FillerAdmin)


class ColumnNameAdmin(admin.ModelAdmin):
    """ColumnName Admin"""
    list_display = ["name", ]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(ColumnName, ColumnNameAdmin)
challenge_designer_site.register(ColumnName, ColumnNameAdmin)
challenge_manager_site.register(ColumnName, ColumnNameAdmin)
developer_site.register(ColumnName, ColumnNameAdmin)
challenge_mgr.register_designer_game_info_model("Smart Grid Game", ColumnName)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", ColumnName)


class LevelAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = Level

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data


class LevelAdmin(admin.ModelAdmin):
    """Level Admin"""
    list_display = ["name", "priority", "unlock_condition"]
    form = LevelAdminForm
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Level, LevelAdmin)
challenge_designer_site.register(Level, LevelAdmin)
challenge_manager_site.register(Level, LevelAdmin)
developer_site.register(Level, LevelAdmin)
challenge_mgr.register_designer_game_info_model("Smart Grid Game", Level)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", Level)


class ConfirmationCodeAdmin(admin.ModelAdmin):
    """admin for Bonus Points."""
    actions = ["delete_selected", "view_selected", "print_selected"]
    list_display = ["pk", "code", "create_date", "is_active",
                    "printed_or_distributed", "user"]
    ordering = ["-create_date", "is_active"]
    list_filter = ["is_active", "printed_or_distributed"]
    date_hierarchy = "create_date"

    def delete_selected(self, request, queryset):
        """override the delete selected method."""
        _ = request
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Delete the selected codes."

    def view_selected(self, request, queryset):
        """Views the Codes for printing."""
        return render_to_response("admin/view_codes.html", {
            "activity": queryset[0].action,
            "codes": queryset,
            "per_page": 10,
        }, context_instance=RequestContext(request))

    view_selected.short_description = "view the selected codes."

    def print_selected(self, request, queryset):
        """Changes the printed_or_distributed flag to True for the selected
        Confirmation Codes."""
        _ = request
        queryset.update(printed_or_distributed=True)

    print_selected.short_description = "Set the printed or distributed flag."

    def view_codes(self, request, queryset):
        """Views the Codes for printing."""
        _ = request
        _ = queryset

        response = HttpResponseRedirect(reverse("activity_view_codes", args=()))
        return response


admin.site.register(ConfirmationCode, ConfirmationCodeAdmin)
challenge_designer_site.register(ConfirmationCode, ConfirmationCodeAdmin)
challenge_manager_site.register(ConfirmationCode, ConfirmationCodeAdmin)
developer_site.register(ConfirmationCode, ConfirmationCodeAdmin)


class QuestionChoiceInline(admin.TabularInline):
    """Question Choice admin."""
    model = QuestionChoice
    fieldset = (
        (None, {
            'fields': ('question', 'choice'),
            'classes': ['wide', ],
            })
        )
    extra = 4


def redirect_urls(model_admin, url_type):
    """change the url redirection."""
    from django.conf.urls import patterns, url
    from functools import update_wrapper

    def wrap(view):
        """wrap the view fuction."""
        def wrapper(*args, **kwargs):
            """return the wrapper."""
            return model_admin.admin_site.admin_view(view)(*args, **kwargs)
        return update_wrapper(wrapper, view)

    info = model_admin.model._meta.app_label, model_admin.model._meta.module_name
    urlpatterns = patterns('',
        url(r'^$',
            wrap(action_admin_list if url_type == "changelist" else model_admin.changelist_view),
            name='%s_%s_changelist' % info),
        url(r'^add/$',
            wrap(model_admin.add_view),
            name='%s_%s_add' % info),
        url(r'^(.+)/history/$',
            wrap(model_admin.history_view),
            name='%s_%s_history' % info),
        url(r'^(.+)/delete/$',
            wrap(model_admin.delete_view),
            name='%s_%s_delete' % info),
        url(r'^(.+)/$',
            wrap(action_admin if url_type == "change" else model_admin.change_view),
            name='%s_%s_change' % info),
    )
    return urlpatterns


class ActionMemberAdminForm(forms.ModelForm):
    """Activity Member admin."""
    def __init__(self, *args, **kwargs):
        """Override to dynamically change the form if the activity specifies a point range.."""

        super(ActionMemberAdminForm, self).__init__(*args, **kwargs)
        # Instance points to an instance of the model.
        member = self.instance
        if member and member.action:
            action = member.action
            message = "Specify the number of points to award. "
            if not action.point_value:
                message += "This default points for this action should be between %d and %d." % (
                    action.activity.point_range_start, action.activity.point_range_end)
            else:
                message += "The default points for this action is %d." % (
                    action.point_value)

            self.fields["points_awarded"].help_text = message

    class Meta:
        """Meta"""
        model = ActionMember

    def clean(self):
        """Custom validator that checks values for variable point activities."""

        # Data that has passed validation.
        cleaned_data = self.cleaned_data
        status = cleaned_data.get("approval_status")

        action = self.instance.action
        if status == "approved" and not action.point_value:
            # Check if the point value is filled in.
            if "points_awarded" not in cleaned_data:
                self._errors["points_awarded"] = ErrorList(
                    [u"This action requires that you specify the number of points to award."])

            # Check if the point value is valid.
            elif cleaned_data["points_awarded"] < action.activity.point_range_start or \
                 cleaned_data["points_awarded"] > action.activity.point_range_end:
                message = "The points to award must be between %d and %d" % (
                    action.activity.point_range_start, action.activity.point_range_end)
                self._errors["points_awarded"] = ErrorList([message])
                del cleaned_data["points_awarded"]

        return cleaned_data


class ActionMemberAdmin(admin.ModelAdmin):
    """ActionMember Admin."""
    radio_fields = {"approval_status": admin.HORIZONTAL}
    readonly_fields = (
        "user", "action", "admin_link", "question", "admin_note", "full_response", "social_email")
    list_display = (
        "action", "submission_date", "user_link", "approval_status", "short_question",
        "short_response")

    list_filter = ["approval_status", "action__type"]
    actions = ["approve_selected", "delete_selected"]
    search_fields = ["action__slug", "action__title", "user__username"]

    date_hierarchy = "submission_date"
    ordering = ["submission_date"]

    form = ActionMemberAdminForm

    def get_object(self, request, object_id):
        obj = super(ActionMemberAdmin, self).get_object(request, object_id)
        if obj and not obj.points_awarded:
            obj.points_awarded = obj.action.point_value
        return obj

    def short_question(self, obj):
        """return the short question."""
        return "%s" % (obj.question)

    short_question.short_description = 'Question'

    def short_response(self, obj):
        """return the short response"""
        return "%s" % obj.response[:160]

    short_response.short_description = 'Response'

    def full_response(self, obj):
        """return the full response."""
        return "%s" % (obj.response).replace("\n", "<br/>")

    full_response.short_description = 'Response'
    full_response.allow_tags = True

    def admin_note(self, obj):
        """return the short question."""
        if obj.action.activity.admin_note:
            note = markdown.markdown(obj.action.activity.admin_note)
        else:
            note = None
        return "%s<a href='/admin/smartgrid/activity/%d'> [Edit Admin Note]</a>" % \
               (note, obj.action.pk)

    admin_note.short_description = 'Admin note'
    admin_note.allow_tags = True

    def changelist_view(self, request, extra_context=None):
        """
        Set the default filter of the admin view to pending.
        Based on iridescent's answer to
        http://stackoverflow.com/questions/851636/default-filter-in-django-admin
        """
        if 'HTTP_REFERER' in request.META and 'PATH_INFO' in request.META:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test[-1] and test[-1].startswith('?'):
                return super(ActionMemberAdmin, self).changelist_view(request,
                                                                      extra_context=extra_context)

        if not 'approval_status__exact' in request.GET:
            q = request.GET.copy()
            q['approval_status__exact'] = 'pending'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        if not 'action__type__exact' in request.GET:
            q = request.GET.copy()
            q['action__type__exact'] = 'activity'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(ActionMemberAdmin, self).changelist_view(request,
                                                              extra_context=extra_context)

    def approve_selected(self, request, queryset):
        """delete priority."""
        _ = request
        for obj in queryset:
            obj.approval_status = "approved"
            obj.admin_comment = ""
            obj.save()
            messages.success(request, "%s approved." % obj.action)

    approve_selected.short_description = "Approve the selected objects (USE CAUTIONS)"

    def delete_selected(self, request, queryset):
        """override the delete selected."""
        _ = request
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = "Delete the selected objects."

    def get_form(self, request, obj=None, **kwargs):
        """Override to remove the points_awarded field if the action
        does not have variable points."""
        if obj and not obj.action.point_value:
            self.fields = (
                "user", "action", "admin_link", "question", "admin_note", "full_response",
                "image", "social_email",
                "approval_status", "points_awarded", "admin_comment")
        else:
            if obj.action.type == "activity":
                self.fields = (
                    "user", "action", "admin_link", "question", "admin_note", "full_response",
                    "image", "social_email",
                    "approval_status", "points_awarded", "admin_comment")
            else:
                self.fields = (
                        "user", "action", "admin_link", "social_email", "completion_date",
                        "points_awarded", "approval_status")

        return super(ActionMemberAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(ActionMember, ActionMemberAdmin)
challenge_designer_site.register(ActionMember, ActionMemberAdmin)
challenge_manager_site.register(ActionMember, ActionMemberAdmin)
developer_site.register(ActionMember, ActionMemberAdmin)

challenge_mgr.register_admin_game_info_model("Smart Grid Game", ActionMember)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", ActionMember)


class EmailReminderAdmin(admin.ModelAdmin):
    """reminder admin"""
    readonly_fields = ('user', 'action', 'sent')
    fields = ("send_at", "email_address", 'user', 'action', 'sent')
    list_display = ('send_at', 'user', 'email_address', 'action', 'sent')
    search_fields = ('user__username', 'email_address', 'action__title')


class TextReminderAdmin(admin.ModelAdmin):
    """reminder admin"""
    readonly_fields = ('user', 'action', 'sent')
    fields = ("send_at", "text_number", 'user', 'action', 'sent')
    list_display = ('send_at', 'user', 'text_number', 'action', 'sent')
    search_fields = ('user__username', 'text_number', 'action__title')


admin.site.register(EmailReminder, EmailReminderAdmin)
challenge_designer_site.register(EmailReminder, EmailReminderAdmin)
challenge_manager_site.register(EmailReminder, EmailReminderAdmin)
developer_site.register(EmailReminder, EmailReminderAdmin)
admin.site.register(TextReminder, TextReminderAdmin)
challenge_designer_site.register(TextReminder, TextReminderAdmin)
challenge_manager_site.register(TextReminder, TextReminderAdmin)
developer_site.register(TextReminder, TextReminderAdmin)
challenge_mgr.register_admin_challenge_info_model("Notifications", 2, EmailReminder, 2)
challenge_mgr.register_admin_challenge_info_model("Notifications", 2, TextReminder, 3)
challenge_mgr.register_developer_challenge_info_model("Status", 3, EmailReminder, 7)
challenge_mgr.register_developer_challenge_info_model("Status", 3, TextReminder, 8)


class ColumnGridAdminForm(forms.ModelForm):
    """Admin form for ColumnGrids."""
    class Meta:
        """meta"""
        model = ColumnGrid


class ColumnGridAdmin(admin.ModelAdmin):
    """Admin interface for ColumnGrid."""
    list_display = ["level", "column", "name"]
    form = ColumnGridAdminForm


admin.site.register(ColumnGrid, ColumnGridAdmin)
developer_site.register(ColumnGrid, ColumnGridAdmin)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", ColumnGrid)


class GridAdminForm(forms.ModelForm):
    """Admin form for Grids."""
    class Meta:
        """meta"""
        model = Grid


class GridAdmin(admin.ModelAdmin):
    """Admin interface for ColumnGrid."""
    list_display = ["level", "column", "row", "action"]
    form = GridAdminForm


admin.site.register(Grid, GridAdmin)
developer_site.register(Grid, GridAdmin)
challenge_mgr.register_developer_game_info_model("Smart Grid Game", Grid)
