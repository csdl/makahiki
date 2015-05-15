"""handles rendering commitments."""
from apps.managers.score_mgr import score_mgr

from apps.widgets.smartgrid import smartgrid
from apps.widgets.smartgrid.forms import CommitmentCommentForm
import datetime

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib import messages

from apps.widgets.smartgrid.models import  ActionMember


def add(request, commitment):
    """Commit the current user to the commitment."""
    user = request.user
    value = None

    if request.method == "GET":  # redirect to task page, only allow POST
        return  HttpResponseRedirect(
            reverse("activity_task", args=(commitment.type, commitment.slug,)))

    form = CommitmentCommentForm(request.POST, user=request.user.username)
    if not form.is_valid():
        # invalid form
        request.session["form_dict"] = form.data
        request.session["form_errors"] = form.errors

        return HttpResponseRedirect(
            reverse("activity_task",
                    args=(commitment.type, commitment.slug,)) + "?display_form=True")

    # now we have a valid form
    if smartgrid.can_complete_commitment(user, commitment):
        try:
            member = user.actionmember_set.get(action=commitment, award_date=None)
        except ObjectDoesNotExist:
            # ignore the race condition
            return HttpResponseRedirect(
                reverse("activity_task", args=(commitment.type, commitment.slug,)))

        #commitment end, award full point
        member.award_date = datetime.datetime.today()
        member.approval_status = "approved"

        if form.cleaned_data["social_email"]:
            member.social_email = form.cleaned_data["social_email"].lower()
        member.save()
        value = commitment.point_value

    elif smartgrid.can_add_commitment(user):
        # User can commit to this commitment. allow to commit to completed commitment again
        # as long as the pending does not reach max
        member = ActionMember(user=user, action=commitment)

        if form:
            member.social_email = form.cleaned_data["social_email"].lower()

        try:
            member.save()
            value = score_mgr.signup_points()

        except IntegrityError:
            messages.error = 'Sorry, but it appears that you are already participating in ' \
                             'this commitment.'
            return HttpResponseRedirect(
                reverse("activity_task", args=(commitment.type, commitment.slug,)))

    else:  # user can not add more than 5 commitment
        return  HttpResponseRedirect(
            reverse("activity_task", args=(commitment.type, commitment.slug,)))

    response = HttpResponseRedirect(
        reverse("activity_task", args=(commitment.type, commitment.slug,)))
    notification = "You just earned " + str(value) + " points."
    response.set_cookie("task_notify", notification)
    return response


def view(request, action):
    """Returns commitment info."""

    session = request.session
    form = None
    if "form_dict" in session:
        form_dict = session.pop("form_dict")
        form = CommitmentCommentForm(initial={
            "social_email": form_dict["social_email"],
        })
        form._errors = session.pop("form_errors")
    else:
        form = CommitmentCommentForm(
            initial={
                'social_email': action.member.social_email if action.member else None})

    if not action.completed or action.member.approval_status == "approved":
        form.form_title = "Make this commitment"
    else:
        form.form_title = "Complete this commitment"

    action.can_commit = smartgrid.can_add_commitment(request.user)
    return form
