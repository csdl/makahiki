"""Handle rendering of the raffle widget."""
import datetime
import random
from django.db.models.aggregates import Count

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.template.context import RequestContext

from apps.managers.challenge_mgr import  challenge_mgr
from apps.widgets.notifications.models import NoticeTemplate, UserNotification
from apps.widgets.raffle.models import  RafflePrize, RaffleTicket, POINTS_PER_TICKET
from apps.widgets.raffle.forms import ChangeRoundForm
from apps.managers.challenge_mgr.models import RoundSetting


def supply(request, page_name):
    """Supply the view_objects contents, which provides all raffle data."""
    _ = page_name
    user = request.user
    today = datetime.datetime.today()
    current_round_info = challenge_mgr.get_round_info()
    if not current_round_info:
        # no in any round
        return {"today": today}

    deadline = current_round_info["end"]

    # Get the user's tickets.
    total_tickets = RaffleTicket.total_tickets(user)

    user_tickets = RaffleTicket.objects.filter(user=user).select_related("raffle_prize")
    allocated_tickets = user_tickets.count()
    available_tickets = total_tickets - allocated_tickets

    prizes = None
    if today < deadline:
        # Get the prizes for the raffle.
        prizes = RafflePrize.objects.filter(
            round__name=current_round_info["name"]).annotate(
            total_tickets=Count("raffleticket")).order_by("-value")

        for prize in prizes:
            prize.user_tickets = 0
            for ticket in user_tickets:
                if ticket.raffle_prize == prize:
                    prize.user_tickets += 1

    return {
        "round_name": current_round_info["name"],
        "deadline": deadline,
        "today": today,
        "points_per_ticket": POINTS_PER_TICKET,
        "tickets": {
            "available": available_tickets,
            "total": total_tickets,
            "allocated": allocated_tickets,
            },
        "prizes": prizes,
        }


@login_required
def add_ticket(request, prize_id):
    """Adds a user's raffle ticket to the prize."""
    if request.method == "POST":
        prize = get_object_or_404(RafflePrize, id=prize_id)
        user = request.user
        current_round_info = challenge_mgr.get_round_info()
        deadline = current_round_info["end"]
        in_deadline = datetime.datetime.today() <= deadline

        if RaffleTicket.available_tickets(user) > 0 and in_deadline:
            prize.add_ticket(user)
            return HttpResponseRedirect(reverse("win_index"))
        elif not in_deadline:
            messages.error(request, "The raffle for this round is over.")
            return HttpResponseRedirect(reverse("win_index"))
        else:
            messages.error(request, "Sorry, but you do not have any more tickets.")
            return HttpResponseRedirect(reverse("win_index"))

    raise Http404


@login_required
def remove_ticket(request, prize_id):
    """Removes a user's raffle ticket from the prize."""
    if request.method == "POST":
        prize = get_object_or_404(RafflePrize, id=prize_id)
        if prize.allocated_tickets(request.user) > 0:
            prize.remove_ticket(request.user)
            return HttpResponseRedirect(reverse("win_index"))

        else:
            messages.error(request, "Sorry, but you do not have any tickets for this prize.")
            return HttpResponseRedirect(reverse("win_index"))

    raise Http404


@never_cache
@user_passes_test(lambda u: u.is_staff, login_url="/landing")
def raffle_form(request, prize_id):
    """Supply the raffle form."""
    _ = request
    prize = get_object_or_404(RafflePrize, pk=prize_id)
    challenge = challenge_mgr.get_challenge()

    try:
        template = NoticeTemplate.objects.get(notice_type='raffle-winner-receipt')
    except NoticeTemplate.DoesNotExist:
        return render_to_response('view_prizes/form.txt', {
        'raffle': True,
        'prize': prize,
        'round': prize.round,
        'competition_name': challenge.competition_name,
        }, context_instance=RequestContext(request), mimetype='text/plain')

    message = template.render({
        'raffle': True,
        'prize': prize,
        'round': prize.round,
        'competition_name': challenge.competition_name,
    })

    return HttpResponse(message, content_type="text", mimetype='text/html')


def raffle_prize_list(request):
    """Generates the raffle prize list and renders to page."""
    raffle_prizes = RafflePrize.objects.all().order_by('round__name')
    return render_to_response("raffle_prize_list.html", {
        "raffle_list": raffle_prizes
        }, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_staff, login_url="/landing")
def notify_winner(request):
    """Sends an email to the user notifying them that they are a winner."""
    _ = request

    round_name = challenge_mgr.get_round_name()
    prizes = RafflePrize.objects.filter(round__name=round_name)
    for prize in prizes:
        if prize.winner:
            # Notify winner using the template.
            template = NoticeTemplate.objects.get(notice_type='raffle-winner')
            message = template.render({'PRIZE': prize})
            UserNotification.create_info_notification(prize.winner, message, True, prize)

    return HttpResponseRedirect("/admin/raffle/raffleprize/")


@user_passes_test(lambda u: u.is_staff, login_url="/landing")
def pick_winner(request):
    """Picks the raffle game winners for the raffle deadline that has passed."""
    _ = request
    round_name = challenge_mgr.get_round_name()
    prizes = RafflePrize.objects.filter(round__name=round_name)
    for prize in prizes:
        if not prize.winner:
            # Randomly order the tickets and then pick a random ticket.
            tickets = prize.raffleticket_set.order_by("?").all()
            if tickets.count():
                ticket = random.randint(0, tickets.count() - 1)
                user = tickets[ticket].user
                prize.winner = user
                prize.save()
    return HttpResponseRedirect("/admin/raffle/raffleprize/")


def prize_summary(request, round_name):
    """display summary of the winners."""

    round_name = round_name.replace('-', ' ').capitalize()

    return render_to_response("summary.html", {
        "raffles": RafflePrize.objects.filter(round__name=round_name).order_by("value", "title")
    }, context_instance=RequestContext(request))


@never_cache
@login_required
def bulk_round_change(request, action_type, attribute):
    """Handle change Round for selected Raffle Prizes from the admin interface."""
# Not sure we need the prize_type and attribute parameters.
    _ = action_type
    _ = attribute
    raffle_ids = request.GET["ids"]
    raffles = []
    for pk in raffle_ids.split(","):
        raffles.append(RafflePrize.objects.get(pk=pk))

    if request.method == "POST":
        r = request.POST["round_choice"]
        for raffle_prize in raffles:
            if r != '':
                raffle_prize.round = RoundSetting.objects.get(pk=r)
            else:
                raffle_prize.round = None
            raffle_prize.save()

        return HttpResponseRedirect("/admin/raffle/raffleprize/")
    else:
        form = ChangeRoundForm(initial={"ids": raffle_ids})
        return render_to_response("admin/bulk_change.html", {
            "attribute": "Round",
            "action_type": None,
            "form": form,
            "raffle_prizes": raffles,
            }, context_instance=RequestContext(request))
