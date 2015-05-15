"""handles reminders in smartgrid."""
import json
import datetime
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from apps.widgets.smartgrid import smartgrid

from apps.widgets.smartgrid.models import  EmailReminder, TextReminder
from apps.widgets.smartgrid.forms import   ReminderForm


@login_required
def reminder(request, action_type, slug):
    """Handle the send reminder request."""
    _ = action_type
    if request.is_ajax():
        if request.method == "POST":
            profile = request.user.profile
            action = smartgrid.get_action(slug=slug)
            form = ReminderForm(request.POST)
            if form.is_valid():

                # Try and retrieve the reminders.
                try:
                    email_reminder = EmailReminder.objects.get(user=request.user, action=action)
                    if form.cleaned_data["send_email"]:
                        email_reminder.email_address = form.cleaned_data["email"]
                        email_reminder.send_at = action.event.event_date - datetime.timedelta(
                            hours=int(form.cleaned_data["email_advance"])
                        )
                        email_reminder.save()

                        profile.user.email = form.cleaned_data["email"]
                        profile.user.save()
                    else:
                        # If send_email is false, the user does not want the reminder anymore.
                        email_reminder.delete()

                except EmailReminder.DoesNotExist:
                    # Create a email reminder
                    if form.cleaned_data["send_email"]:
                        EmailReminder.objects.create(
                            user=request.user,
                            action=action,
                            email_address=form.cleaned_data["email"],
                            send_at=action.event.event_date - datetime.timedelta(
                                hours=int(form.cleaned_data["email_advance"])
                            )
                        )

                        profile.user.email = form.cleaned_data["email"]
                        profile.user.save()

                try:
                    text_reminder = TextReminder.objects.get(user=request.user, action=action)
                    if form.cleaned_data["send_text"]:
                        text_reminder.text_number = form.cleaned_data["text_number"]
                        text_reminder.text_carrier = form.cleaned_data["text_carrier"]
                        text_reminder.send_at = action.event.event_date - datetime.timedelta(
                            hours=int(form.cleaned_data["text_advance"])
                        )
                        text_reminder.save()

                        profile.contact_text = form.cleaned_data["text_number"]
                        profile.contact_carrier = form.cleaned_data["text_carrier"]
                        profile.save()

                    else:
                        text_reminder.delete()

                except TextReminder.DoesNotExist:
                    if form.cleaned_data["send_text"]:
                        TextReminder.objects.create(
                            user=request.user,
                            action=action,
                            text_number=form.cleaned_data["text_number"],
                            text_carrier=form.cleaned_data["text_carrier"],
                            send_at=action.event.event_date - datetime.timedelta(
                                hours=int(form.cleaned_data["text_advance"])
                            ),
                        )

                        profile.contact_text = form.cleaned_data["text_number"]
                        profile.contact_carrier = form.cleaned_data["text_carrier"]
                        profile.save()

                return HttpResponse(json.dumps({"success": True}), mimetype="application/json")

            template = render_to_string("reminder_form.html", {
                "reminders": {"form": form},
                "action": action,
                })

            return HttpResponse(json.dumps({
                "success": False,
                "form": template,
                }), mimetype="application/json")
    raise Http404


def load_reminders(action, user):
    """Load the reminders."""
    reminders = {}
    if action.type in ("event", "excursion"):
        # Store initial reminder fields.
        reminder_init = {"email": user.email,
            "text_number": user.profile.contact_text,
            "text_carrier": user.profile.contact_carrier}
        # Retrieve an existing reminder and update it accordingly.
        try:
            email = user.emailreminder_set.get(action=action)
            reminders.update({"email": email})
            reminder_init.update({
                "email": email.email_address,
                "send_email": True,
                "email_advance": str((action.event.event_date - email.send_at).seconds / 3600)})
        except ObjectDoesNotExist:
            pass
        try:
            text = user.textreminder_set.get(action=action)
            reminders.update({"text": text})
            reminder_init.update({
                "text_number": text.text_number,
                "text_carrier": text.text_carrier,
                "send_text": True,
                "text_advance": str((action.event.event_date - text.send_at).seconds / 3600)})
        except ObjectDoesNotExist:
            pass

        reminders.update({"form": ReminderForm(initial=reminder_init)})
    return reminders
