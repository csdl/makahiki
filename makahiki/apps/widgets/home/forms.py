"""Provides the forms for the first login wizard."""

import re

from django import forms
from django.contrib.auth.models import User
from apps.managers.challenge_mgr import challenge_mgr

from apps.managers.player_mgr.models import Profile


class FacebookForm(forms.Form):
    """Form about can post to facebook."""
    can_post = forms.BooleanField(
        required=False,
        initial=True,
        label="%s can post to my Facebook feed (at most 2 posts per day)" %
              challenge_mgr.get_challenge().competition_name
    )


class ReferralForm(forms.Form):
    """Form for referral bonus."""
    referrer_email = forms.EmailField(
        required=False,
        label='Referrer Email (Optional)'
    )

    def __init__(self, *args, **kwargs):
        """
        Override for init to take a user argument.
        """
        self.user = kwargs.pop('user', None)
        super(ReferralForm, self).__init__(*args, **kwargs)

    def clean_referrer_email(self):
        """Check to make sure the referring user is part of the competition."""
        email = self.cleaned_data['referrer_email'].lower()
        if email:
            """Check to make sure the user is not submitting their own email."""
            if self.user.email == email:
                raise forms.ValidationError(
                    "Please use another user's email address, not your own.")
            else:
                # Check if referer is staff.
                try:
                    User.objects.get(email=email, is_staff=True)
                    raise forms.ValidationError(
                        "Sorry, but admins are invalid referers.")
                except User.DoesNotExist:
                    # Check to see if they exist as players.
                    try:
                        User.objects.get(email=email, is_staff=False)
                    except User.DoesNotExist:
                        raise forms.ValidationError(
                            "Sorry, but that user is not a part of the competition.")
        return email


class ProfileForm(forms.Form):
    """Form for modified profile info"""
    display_name = forms.CharField(
        max_length=16,
        help_text="This is the name others in your lounge will see, and how you"\
                  " will be identified on scoreboards"
    )
    facebook_photo = forms.URLField(widget=forms.HiddenInput, required=False)
    use_fb_photo = forms.BooleanField(required=False)
    avatar = forms.ImageField(required=False)
    pic_method = forms.IntegerField(widget=forms.widgets.RadioSelect(), required=False)

    def __init__(self, *args, **kwargs):
        """Allow init to take a user argument."""
        self.user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_display_name(self):
        """Verify display name: trim whitespace, require non-empty, no duplicates."""
        name = self.cleaned_data['display_name'].strip()
        # Remove extra whitespace from the name.
        spaces = re.compile(r'\s+')
        name = spaces.sub(' ', name)

        # Check for name that is just whitespace.
        if name == '':
            raise forms.ValidationError('This field is required')

        # Check for duplicate name
        if Profile.objects.exclude(user=self.user).filter(
            name=name).count() > 0:
            raise forms.ValidationError(
                "'%s' is already taken.  Please use another name." % name)

        return name
