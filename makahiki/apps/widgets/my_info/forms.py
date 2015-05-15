"""Provide the forms for the My_Info widget."""
from django.conf import settings
import re

from django import forms
from localflavor.us.forms import USPhoneNumberField

from apps.managers.player_mgr.models import Profile
from apps.widgets.smartgrid.models import TextReminder


class ProfileForm(forms.Form):
    """Define the form for the My_Info widget."""
    def __init__(self, *args, **kwargs):
        """Override init to take a user argument."""
        self.username = kwargs.pop('user', None)
        self.message = None
        super(ProfileForm, self).__init__(*args, **kwargs)

    display_name = forms.CharField(required=True, max_length=16, min_length=1)
    THEME_CHOICES = ((key, key[6:].capitalize()) for key in settings.INSTALLED_THEMES)

    theme = forms.ChoiceField(choices=THEME_CHOICES)

    # Event notifications
    contact_email = forms.EmailField(required=False)
    contact_text = USPhoneNumberField(required=False, widget=forms.TextInput(attrs={
        "style": "width: 100px",
        }))
    contact_carrier = forms.ChoiceField(choices=TextReminder.TEXT_CARRIERS)

    def clean_display_name(self):
        """Check if this profile name is valid."""
        name = self.cleaned_data['display_name'].strip()
        # Remove extra whitespace from the name.
        spaces = re.compile(r'\s+')
        name = spaces.sub(' ', name)

        # Check for name that is just whitespace.
        if name == '':
            raise forms.ValidationError('This field is required')

        # Check for duplicate name
        if Profile.objects.exclude(user__username=self.username).filter(name=name).count() > 0:
            raise forms.ValidationError("%s is taken.  Please use another name.")

        return name

    def clean_contact_email(self):
        """make the email lower case."""
        return self.cleaned_data['contact_email'].lower()
