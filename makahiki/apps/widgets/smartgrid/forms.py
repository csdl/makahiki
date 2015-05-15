"""Forms for activity."""

from django import forms
from django.forms.util import ErrorList

from apps.widgets.smartgrid.models import ConfirmationCode, TextReminder, Level, \
    ColumnName
from apps.managers.player_mgr import player_mgr
from apps.widgets.smartgrid_library.models import LibraryQuestionChoice


class GenerateCodeForm(forms.Form):
    """Form for generating confirmation codes."""
    event_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    num_codes = forms.IntegerField(initial=0)


class ChangeLevelForm(forms.Form):
    """change level form."""
    level_choice = forms.ModelChoiceField(queryset=Level.objects.all(), required=True)
    column_choice = forms.ModelChoiceField(queryset=ColumnName.objects.all(), required=True)


class ActivityTextForm(forms.Form):
    """Text form."""
    question = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    response = forms.CharField(widget=forms.Textarea(attrs={'rows': '2'}), required=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.action = kwargs.pop('action', None)
        qid = None
        if 'question_id' in kwargs:
            qid = kwargs.pop('question_id')

        super(ActivityTextForm, self).__init__(*args, **kwargs)

        if qid:
            self.fields['choice_response'] = forms.ModelChoiceField(
                queryset=LibraryQuestionChoice.objects.filter(question__id=qid), required=True)

    def clean(self):
        """Custom validation to verify confirmation codes."""
        cleaned_data = self.cleaned_data

        # Check if we are validating quetion
        if cleaned_data["question"] > 0:
            if not "response" in cleaned_data and not "choice_response" in cleaned_data:
                self._errors["response"] = ErrorList(["You need to answer the question."])
                if "response" in cleaned_data:
                    del cleaned_data["response"]
                if "choice_response" in cleaned_data:
                    del cleaned_data["choice_response"]

        _validate_social_email(self.request, self.action, cleaned_data, self._errors)

        return cleaned_data


class ActivityCodeForm(forms.Form):
    """confirmation code form."""
    response = forms.CharField(widget=forms.TextInput(attrs={'size': '15'}), required=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.action = kwargs.pop('action', None)

        super(ActivityCodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        """Custom validation to verify confirmation codes."""
        cleaned_data = self.cleaned_data

        # Check if we are validating a confirmation code.
        try:
            code = ConfirmationCode.objects.get(code=cleaned_data["response"].lower())
            # Check if the code is inactive.
            if not code.is_active:
                self._errors["response"] = ErrorList(["This code has already been used."])
                del cleaned_data["response"]
            # Check if this action is the same as the added action (if provided)
            elif self.action and code.action.event != self.action:
                self._errors["response"] = ErrorList(
                    ["This confirmation code is not valid for this action."])
                del cleaned_data["response"]
            # Check if the user has already submitted a code for this action.
            elif code.action in self.request.user.action_set.filter(
                actionmember__award_date__isnull=False):
                self._errors["response"] = ErrorList(
                    ["You have already redeemed a code for this action."])
                del cleaned_data["response"]
        except ConfirmationCode.DoesNotExist:
            self._errors["response"] = ErrorList(["This code is not valid."])
            del cleaned_data["response"]
        except KeyError:
            self._errors["response"] = ErrorList(["Please input code."])

        _validate_social_email(self.request, self.action, cleaned_data, self._errors)

        return cleaned_data


class ActivityFreeResponseForm(forms.Form):
    """Free response form."""
    response = forms.CharField(widget=forms.Textarea)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.action = kwargs.pop('action', None)
        super(ActivityFreeResponseForm, self).__init__(*args, **kwargs)

    def clean(self):
        """clean"""
        cleaned_data = self.cleaned_data
        _validate_social_email(self.request, self.action, cleaned_data, self._errors)
        return cleaned_data


class ActivityImageForm(forms.Form):
    """Image upload form."""
    image_response = forms.ImageField()
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.action = kwargs.pop('action', None)
        super(ActivityImageForm, self).__init__(*args, **kwargs)

    def clean(self):
        """clean"""
        cleaned_data = self.cleaned_data
        _validate_social_email(self.request, self.action, cleaned_data, self._errors)
        return cleaned_data


class ActivityFreeResponseImageForm(forms.Form):
    """Free response and image upload form."""
    response = forms.CharField(widget=forms.Textarea)
    image_response = forms.ImageField()
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False)
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.action = kwargs.pop('action', None)
        super(ActivityFreeResponseImageForm, self).__init__(*args, **kwargs)

    def clean(self):
        """clean"""
        cleaned_data = self.cleaned_data
        _validate_social_email(self.request, self.action, cleaned_data, self._errors)
        return cleaned_data


class CommitmentCommentForm(forms.Form):
    """commitment comment form."""
    social_email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('user', None)
        super(CommitmentCommentForm, self).__init__(*args, **kwargs)

    def clean_social_email(self):
        """Check if this social_email is valid."""
        email = self.cleaned_data['social_email'].strip().lower()
        if email:
            user = player_mgr.get_user_by_email(email)
            if user == None:
                raise forms.ValidationError('Can not find a registered user with such email.')
            elif user.username == self.username:
                raise forms.ValidationError('Can not use your own email.')
        return email


class SurveyForm(forms.Form):
    """survey form."""
    def __init__(self, *args, **kwargs):
        questions = None
        if 'questions' in kwargs:
            questions = kwargs.pop('questions')

        super(SurveyForm, self).__init__(*args, **kwargs)

        if questions:
            for i, q in enumerate(questions):
                self.fields['choice_response_%s' % i] = forms.ModelChoiceField(
                    queryset=LibraryQuestionChoice.objects.filter(question__id=q.pk),
                    label=q.question,
                    required=True
                )

    def clean(self):
        """clean"""
        cleaned_data = self.cleaned_data
        return cleaned_data


def _validate_social_email(request, action, cleaned_data, errors):
    """validate the two social email."""
    _ = action
    _validate_one_email(request, cleaned_data, "social_email", errors)


def _validate_one_email(request, cleaned_data, email, errors):
    """validate one email."""
    if cleaned_data[email]:
        user = player_mgr.get_user_by_email(cleaned_data[email].lower())
        if user == None or user == request.user:
            errors[email] = ErrorList(["Invalid email. Please input only one valid email."])
            del cleaned_data[email]


class EventCodeForm(forms.Form):
    """event code form in the upcoming event widget."""
    response = forms.CharField(widget=forms.TextInput(attrs={'size': '12'}))
    social_email = forms.CharField(widget=forms.TextInput(attrs={'size': '15'}), initial="Email",
        required=False)

#------ Reminder form ---------
from localflavor.us.forms import USPhoneNumberField

REMINDER_TIME_CHOICES = (
    ("1", "1 hour"),
    ("2", "2 hours"),
    ("3", "3 hours"),
    ("4", "4 hours"),
    ("5", "5 hours"),
    )


class ReminderForm(forms.Form):
    """reminder form."""
    send_email = forms.BooleanField(required=False)
    email = forms.EmailField(required=False, label="Email Address")
    send_text = forms.BooleanField(required=False)
    email_advance = forms.ChoiceField(choices=REMINDER_TIME_CHOICES,
        label="Send reminder how far in advance?")
    text_number = USPhoneNumberField(required=False, label="Mobile phone number")
    text_carrier = forms.ChoiceField(choices=TextReminder.TEXT_CARRIERS, required=False,
        label="Carrier")
    text_advance = forms.ChoiceField(choices=REMINDER_TIME_CHOICES,
        label="Send reminder how far in advance?")

    def clean(self):
        """validate form."""
        cleaned_data = self.cleaned_data
        send_email = cleaned_data.get("send_email")
        email = None
        if "email" in cleaned_data:
            email = cleaned_data.get("email")
        if send_email and (not email or len(email) == 0):
            raise forms.ValidationError("A valid email address is required.")

        send_text = cleaned_data.get("send_text")
        number = None
        if "text_number" in cleaned_data:
            number = cleaned_data.get("text_number")
        if send_text and (not number or len(number) == 0):
            raise forms.ValidationError("A valid phone number is required.")

        return cleaned_data
