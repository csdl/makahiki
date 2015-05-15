"""Admin definition for Smart Grid Game Library."""
from django.db import models
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr

from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django.forms import TextInput, Textarea
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site
from apps.widgets.smartgrid_library.models import LibraryTextPromptQuestion, LibraryColumnName, \
    LibraryActivity, LibraryQuestionChoice, LibraryEvent, LibraryCommitment, LibraryAction
from django.db.utils import IntegrityError
from apps.widgets.smartgrid_library.views import library_action_admin_list, library_action_admin
from django.http import HttpResponseRedirect
from apps.managers.predicate_mgr import predicate_mgr


class LibraryActionAdmin(admin.ModelAdmin):
    """Admin interface for LibraryActions."""
    actions = ["delete_selected", "copy_action"]
    list_display = ["slug", "title", "type", "point_value"]
    search_fields = ["slug", "title"]
    list_filter = ["type", ]

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

admin.site.register(LibraryAction, LibraryActionAdmin)
challenge_designer_site.register(LibraryAction, LibraryActionAdmin)
challenge_manager_site.register(LibraryAction, LibraryActionAdmin)
developer_site.register(LibraryAction, LibraryActionAdmin)
challenge_mgr.register_designer_challenge_info_model("Smart Grid Game Library", 4, \
                                                     LibraryAction, 2)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Library", 4, \
                                                      LibraryAction, 2)


class LibraryColumnNameAdmin(admin.ModelAdmin):
    """LibraryColumnName Admin."""
    list_display = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    fields = ["name", "slug"]

admin.site.register(LibraryColumnName, LibraryColumnNameAdmin)
challenge_designer_site.register(LibraryColumnName, LibraryColumnNameAdmin)
challenge_manager_site.register(LibraryColumnName, LibraryColumnNameAdmin)
developer_site.register(LibraryColumnName, LibraryColumnNameAdmin)
challenge_mgr.register_designer_challenge_info_model("Smart Grid Game Library", 4, \
                                                     LibraryColumnName, 1)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Library", 4, \
                                                      LibraryColumnName, 1)


class LibraryActivityAdminForm(forms.ModelForm):
    """Smart Grid Game Library Activity Admin Form."""
    class Meta:
        """Meta"""
        model = LibraryActivity

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def clean(self):
        """
        Validates the admin form data based on a set of constraints.
            1.  If the verification type is "image" or "code", then a confirm prompt is required.
            2.  Either points or a point range needs to be specified.
        """

        super(LibraryActivityAdminForm, self).clean()

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

        #2 Either points or a point range needs to be specified.
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
        activity = super(LibraryActivityAdminForm, self).save(*args, **kwargs)
        activity.type = 'activity'
        activity.save()
        cache_mgr.clear()

        # If the activity's confirmation type is text, make sure to save the questions.
        if self.cleaned_data.get("confirm_type") == "text":
            self.save_m2m()

        return activity


class LibraryTextQuestionInlineFormSet(BaseInlineFormSet):
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


class LibraryQuestionChoiceInline(admin.TabularInline):
    """Smart Grid Game Library Question Choice admin."""
    model = LibraryQuestionChoice
    fieldset = (
        (None, {
            'fields': ('question', 'choice'),
            'classes': ['wide', ],
            })
        )
    extra = 4


class LibraryTextQuestionInline(admin.TabularInline):
    """Text Question admin."""
    model = LibraryTextPromptQuestion
    fieldset = (
        (None, {
            'fields': ('question', 'answer'),
            })
        )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
        }

    extra = 1
    formset = LibraryTextQuestionInlineFormSet


class LibraryActivityAdmin(admin.ModelAdmin):
    """Smart Grid Game Library Activities Admin."""
    list_display = ["slug", 'title', 'expected_duration', 'point_value']
    fieldsets = (
        ("Basic Information",
         {'fields': (('name', ),
                     ('slug', ),
                     ('title', 'expected_duration'),
                     'image',
                     'description',
                     ('video_id', 'video_source'),
                     'embedded_widget',
                     ('unlock_condition', 'unlock_condition_text'),
                     )}),
        ("Points",
         {"fields": (("point_value", "social_bonus"), ("point_range_start", "point_range_end"), )}),
        ("Admin Note", {'fields': ('admin_note',)}),
        ("Confirmation Type", {'fields': ('confirm_type', 'confirm_prompt')}),
    )
    prepopulated_fields = {"slug": ("name",)}

    form = LibraryActivityAdminForm
    inlines = [LibraryTextQuestionInline]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")


admin.site.register(LibraryActivity, LibraryActivityAdmin)
challenge_designer_site.register(LibraryActivity, LibraryActivityAdmin)
challenge_manager_site.register(LibraryActivity, LibraryActivityAdmin)
developer_site.register(LibraryActivity, LibraryActivityAdmin)


class LibraryCommitmentAdminForm(forms.ModelForm):
    """Smart Grid Game Library Commitment admin form"""
    class Meta:
        """meta"""
        model = LibraryCommitment

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def save(self, *args, **kwargs):
        """save"""
        commitment = super(LibraryCommitmentAdminForm, self).save(*args, **kwargs)
        commitment.type = 'commitment'
        commitment.save()
        cache_mgr.clear()

        return commitment


class LibraryCommitmentAdmin(admin.ModelAdmin):
    """Smart Grid Game Library Commitment Admin."""
    list_display = ["slug", 'title', 'commitment_length', 'point_value']
    fieldsets = (
        ("Basic Information", {
            'fields': (('name', ),
                       ('slug', ),
                       ('title', 'commitment_length'),
                       'image',
                       'description',
                       'unlock_condition', 'unlock_condition_text',
                       ),
            }),
        ("Points", {"fields": (("point_value", 'social_bonus'), )}),
        )
    prepopulated_fields = {"slug": ("name",)}

    form = LibraryCommitmentAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        """override the url definition."""
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")


admin.site.register(LibraryCommitment, LibraryCommitmentAdmin)
challenge_designer_site.register(LibraryCommitment, LibraryCommitmentAdmin)
challenge_manager_site.register(LibraryCommitment, LibraryCommitmentAdmin)
developer_site.register(LibraryCommitment, LibraryCommitmentAdmin)


class LibraryEventAdminForm(forms.ModelForm):
    """Smart Grid Game Library Event Admin Form."""

    class Meta:
        """Meta"""
        model = LibraryEvent

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def save(self, *args, **kwargs):
        """save"""
        event = super(LibraryEventAdminForm, self).save(*args, **kwargs)
        event.type = 'event'
        event.save()
        cache_mgr.clear()

        return event


class LibraryEventAdmin(admin.ModelAdmin):
    """Smart Grid Game Library Event Admin"""
    list_display = ["slug", 'title', 'expected_duration', 'point_value']
    fieldsets = (
        ("Basic Information",
         {'fields': (('name',),
                     ('slug',),
                     ('title', 'expected_duration'),
                     'image',
                     'description',
                     ('unlock_condition', 'unlock_condition_text'),
                     )}),
        ("Points", {"fields": (("point_value", "social_bonus"),)}),
        )
    prepopulated_fields = {"slug": ("name",)}

    form = LibraryEventAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/")


admin.site.register(LibraryEvent, LibraryEventAdmin)
challenge_designer_site.register(LibraryEvent, LibraryEventAdmin)
challenge_manager_site.register(LibraryEvent, LibraryEventAdmin)
developer_site.register(LibraryEvent, LibraryEventAdmin)


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
            wrap(library_action_admin_list if url_type == "changelist" else \
                 model_admin.changelist_view),
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
            wrap(library_action_admin if url_type == "change" else model_admin.change_view),
            name='%s_%s_change' % info),
    )
    return urlpatterns
