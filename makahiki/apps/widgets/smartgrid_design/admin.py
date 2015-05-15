"""Admin definition for Smart Grid Game widget."""
from django.db import models
from apps.managers.cache_mgr import cache_mgr
from apps.managers.challenge_mgr import challenge_mgr
from apps.widgets.smartgrid_design.views import designer_action_admin, \
    designer_action_admin_list

from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django.forms import TextInput, Textarea
from django.db.utils import IntegrityError
from apps.admin.admin import challenge_designer_site, challenge_manager_site, developer_site
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerActivity, \
    DesignerTextPromptQuestion, DesignerCommitment, DesignerEvent, DesignerFiller, \
    DesignerColumnName, DesignerLevel, DesignerQuestionChoice, Draft, DesignerColumnGrid, \
    DesignerGrid
from django.http import HttpResponseRedirect
from apps.managers.predicate_mgr import predicate_mgr


class DesignerDraftAdmin(admin.ModelAdmin):
    """Admin for Drafts."""
    list_display = ["name", ]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Draft, DesignerDraftAdmin)
challenge_designer_site.register(Draft, DesignerDraftAdmin)
challenge_manager_site.register(Draft, DesignerDraftAdmin)
developer_site.register(Draft, DesignerDraftAdmin)
challenge_mgr.register_designer_challenge_info_model("Smart Grid Game Designer", 5, \
                                                     Draft, 1)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      Draft, 1)


class DesignerActionAdmin(admin.ModelAdmin):
    """abstract admin for action."""
    actions = ["delete_selected", "copy_action"]
    list_display = ["draft", "slug", "title", "type", "point_value"]
    search_fields = ["draft", "slug", "title"]
    list_filter = ['draft', 'type', ]

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

admin.site.register(DesignerAction, DesignerActionAdmin)
challenge_designer_site.register(DesignerAction, DesignerActionAdmin)
challenge_manager_site.register(DesignerAction, DesignerActionAdmin)
developer_site.register(DesignerAction, DesignerActionAdmin)
challenge_mgr.register_designer_challenge_info_model("Smart Grid Game Designer", 5, \
                                                     DesignerAction, 2)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      DesignerAction, 2)


class DesignerActivityAdminForm(forms.ModelForm):
    """Activity Admin Form."""
    class Meta:
        """Meta"""
        model = DesignerActivity

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

        super(DesignerActivityAdminForm, self).clean()

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
        activity = super(DesignerActivityAdminForm, self).save(*args, **kwargs)
        activity.type = 'activity'
        activity.save()
        cache_mgr.clear()

        # If the activity's confirmation type is text, make sure to save the questions.
        if self.cleaned_data.get("confirm_type") == "text":
            self.save_m2m()

        return activity


class DesignerTextQuestionInlineFormSet(BaseInlineFormSet):
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
    model = DesignerTextPromptQuestion
    fieldset = (
        (None, {
            'fields': ('question', 'answer'),
            })
        )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
        }

    extra = 1
    formset = DesignerTextQuestionInlineFormSet


class DesignerActivityAdmin(admin.ModelAdmin):
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

    form = DesignerActivityAdminForm
    inlines = [TextQuestionInline]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerActivity, DesignerActivityAdmin)
challenge_designer_site.register(DesignerActivity, DesignerActivityAdmin)
challenge_manager_site.register(DesignerActivity, DesignerActivityAdmin)
developer_site.register(DesignerActivity, DesignerActivityAdmin)


class DesignerCommitmentAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = DesignerCommitment

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data

    def save(self, *args, **kwargs):
        """save"""
        commitment = super(DesignerCommitmentAdminForm, self).save(*args, **kwargs)
        commitment.type = 'commitment'
        commitment.save()
        cache_mgr.clear()

        return commitment


class DesignerCommitmentAdmin(admin.ModelAdmin):
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

    form = DesignerCommitmentAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        """override the url definition."""
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerCommitment, DesignerCommitmentAdmin)
challenge_designer_site.register(DesignerCommitment, DesignerCommitmentAdmin)
challenge_manager_site.register(DesignerCommitment, DesignerCommitmentAdmin)
developer_site.register(DesignerCommitment, DesignerCommitmentAdmin)


class DesignerEventAdminForm(forms.ModelForm):
    """Event Admin Form."""

    class Meta:
        """Meta"""
        model = DesignerEvent

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
        event = super(DesignerEventAdminForm, self).save(*args, **kwargs)
        event.type = 'event'
        event.save()

        cache_mgr.clear()

        return event


class DesignerEventAdmin(admin.ModelAdmin):
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

    form = DesignerEventAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerEvent, DesignerEventAdmin)
challenge_designer_site.register(DesignerEvent, DesignerEventAdmin)
challenge_manager_site.register(DesignerEvent, DesignerEventAdmin)
developer_site.register(DesignerEvent, DesignerEventAdmin)


class DesignerFillerAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = DesignerFiller

    def save(self, *args, **kwargs):
        """save"""
        filler = super(DesignerFillerAdminForm, self).save(*args, **kwargs)
        filler.type = 'filler'
        filler.unlock_condition = "False"
        filler.unlock_condition_text = "This cell is here only to fill out the grid. " \
                                       "There is no action associated with it."
        filler.save()
        cache_mgr.clear()

        return filler


class DesignerFillerAdmin(admin.ModelAdmin):
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

    form = DesignerFillerAdminForm

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        }

    def get_urls(self):
        """override the url definition."""
        return redirect_urls(self, "changelist")

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerFiller, DesignerFillerAdmin)
challenge_designer_site.register(DesignerFiller, DesignerFillerAdmin)
challenge_manager_site.register(DesignerFiller, DesignerFillerAdmin)
developer_site.register(DesignerFiller, DesignerFillerAdmin)


class DesignerColumnNameAdmin(admin.ModelAdmin):
    """DesignerColumnName Administration"""
    list_display = ["name", ]
    prepopulated_fields = {"slug": ("name",)}

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerColumnName, DesignerColumnNameAdmin)
challenge_designer_site.register(DesignerColumnName, DesignerColumnNameAdmin)
challenge_manager_site.register(DesignerColumnName, DesignerColumnNameAdmin)
developer_site.register(DesignerColumnName, DesignerColumnNameAdmin)


class DesignerLevelAdminForm(forms.ModelForm):
    """admin form"""
    class Meta:
        """meta"""
        model = DesignerLevel

    def clean_unlock_condition(self):
        """Validates the unlock conditions of the action."""
        data = self.cleaned_data["unlock_condition"]
        predicate_mgr.validate_form_predicates(data)
        return data


class DesignerLevelAdmin(admin.ModelAdmin):
    """Level Admin"""
    list_display = ["draft", "name", "priority", "unlock_condition"]
    form = DesignerLevelAdminForm
    prepopulated_fields = {"slug": ("name",)}

    def response_change(self, request, obj):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("/sgg_designer/?draft=%s" % obj.draft.slug)


admin.site.register(DesignerLevel, DesignerLevelAdmin)
challenge_designer_site.register(DesignerLevel, DesignerLevelAdmin)
challenge_manager_site.register(DesignerLevel, DesignerLevelAdmin)
developer_site.register(DesignerLevel, DesignerLevelAdmin)
challenge_mgr.register_designer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      DesignerLevel, 3)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      DesignerLevel, 3)


class DesignerColumnGridAdminForm(forms.ModelForm):
    """Admin Form for DesignerColumnGrids."""
    class Meta:
        """meta"""
        model = DesignerColumnGrid


class DesignerColumnGridAdmin(admin.ModelAdmin):
    """DesignerColumnGrid Admin interface."""
    list_display = ["draft", "level", "column", "name"]
    form = DesignerColumnGridAdminForm
    list_filter = ['draft', ]


admin.site.register(DesignerColumnGrid, DesignerColumnGridAdmin)
developer_site.register(DesignerColumnGrid, DesignerColumnGridAdmin)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      DesignerColumnGrid, 3)


class DesignerGridAdminForm(forms.ModelForm):
    """Admin Form for DesignerGrid."""
    class Meta:
        """meta"""
        model = DesignerGrid


class DesignerGridAdmin(admin.ModelAdmin):
    """DesignerGrid Admin interface."""
    list_display = ["draft", "level", "column", "row", "action"]
    form = DesignerGridAdminForm
    list_filter = ["draft", ]


admin.site.register(DesignerGrid, DesignerGridAdmin)
developer_site.register(DesignerGrid, DesignerGridAdmin)
challenge_mgr.register_developer_challenge_info_model("Smart Grid Game Designer", 4, \
                                                      DesignerGrid, 4)


class QuestionChoiceInline(admin.TabularInline):
    """Question Choice admin."""
    model = DesignerQuestionChoice
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
            wrap(designer_action_admin_list if url_type == "changelist" else \
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
            wrap(designer_action_admin if url_type == "change" else model_admin.change_view),
            name='%s_%s_change' % info),
    )
    return urlpatterns
