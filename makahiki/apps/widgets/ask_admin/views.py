"""Views handler for ask admin page rendering."""
import json
from django.core.urlresolvers import reverse

from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from apps.managers.challenge_mgr import challenge_mgr

from apps.widgets.ask_admin.forms import FeedbackForm


def supply(request, page_name):
    """Supply view_objects for widget rendering, returns form."""
    _ = request
    _ = page_name
    form = FeedbackForm(auto_id="help_%s")
    form.url = reverse("help_index")
    return {
        "form": form,
        }


def send_feedback(request):
    """send feedback."""
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            html_message = render_to_string("email/ask_admin.html", {
                "user": request.user,
                "url": form.cleaned_data["url"],
                "question": form.cleaned_data["question"],
                })
            message = render_to_string("email/ask_admin.txt", {
                "user": request.user,
                "url": form.cleaned_data["url"],
                "question": form.cleaned_data["question"],
                })

            challenge = challenge_mgr.get_challenge()
            # Using adapted version from Django source code
            subject = u'[%s] %s asked a question' % (
                challenge.name,
                request.user.profile.name)

            if challenge.email_enabled or True:
                mail = EmailMultiAlternatives(subject, message, challenge.contact_email,
                    [challenge.contact_email, ], headers={
                    "Reply-To": request.user.email})

                mail.attach_alternative(html_message, 'text/html')
                print html_message
                mail.send()

            #print "email sent %s" % html_message
            if request.is_ajax():
                return HttpResponse(json.dumps({"success": True}),
                                    mimetype="application/json")

    raise Http404
