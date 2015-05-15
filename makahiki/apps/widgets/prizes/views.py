"""Provide the view of the prizes widget."""
import datetime

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.player_mgr.models import Profile
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr import team_mgr
from apps.managers.team_mgr.models import Team
from apps.widgets.notifications.models import NoticeTemplate
from apps.widgets.prizes.models import Prize
from apps.widgets.resource_goal import resource_goal
from apps.managers.challenge_mgr.models import RoundSetting
from apps.widgets.prizes.forms import ChangePrizeRoundForm
from django.db.utils import IntegrityError


def supply(request, page_name):
    """Supply view_object content, which is the prizes for this team."""
    _ = page_name
    team = request.user.profile.team
    prizes = _get_prizes(team)
    count = len(prizes)
    return {
        "prizes": prizes,
        "range": count,
        }


def _get_prizes(team):
    """Private method to process the prizes half of the page.
       Takes the user's team and returns a dictionary to be used in the template."""

    prize_dict = {}
    today = datetime.datetime.today()
    rounds = challenge_mgr.get_all_round_info()["rounds"]

    round_name = None
    for prize in Prize.objects.all():
        if prize.round:
            if round_name != prize.round.name:
                # a new round
                round_name = prize.round.name
                prize_dict[round_name] = []

            if today < rounds[round_name]["start"]:
                # If the round happens in the future, we don't care who the leader is.
                prize.current_leader = "TBD"
            else:
                # If we are in the middle of the round, display the current leader.
                if today < rounds[round_name]["end"]:
                    prize.current_leader = prize.leader(team)
                else:
                    prize.winner = prize.leader(team)

            prize_dict[round_name].append(prize)

    return prize_dict


@never_cache
@user_passes_test(lambda u: u.is_staff, login_url="/landing")
def prize_form(request, prize_id, user_id):
    """Supply the prize form."""
    _ = request
    prize = get_object_or_404(Prize, pk=prize_id)
    prize.winner = get_object_or_404(User, pk=user_id)
    challenge = challenge_mgr.get_challenge()

    try:
        template = NoticeTemplate.objects.get(notice_type='prize-winner-receipt')
    except NoticeTemplate.DoesNotExist:
        return render_to_response('view_prizes/form.txt', {
            'raffle': False,
            'prize': prize,
            'round': prize.round.name,
            'competition_name': challenge.name,
        }, context_instance=RequestContext(request), mimetype='text/plain')

    message = template.render({
        'raffle': False,
        'prize': prize,
        'round': prize.round.name,
        'competition_name': challenge.name,
    })
    return HttpResponse(message, content_type="text", mimetype='text/html')


def prize_team_winners(request, prize_id):
    """display the winner for the individual team prize winner."""
    prize = get_object_or_404(Prize, pk=prize_id)
    teams = Team.objects.all()
    for team in teams:
        team.leader = prize.leader(team=team)
        team.prize = prize

    return render_to_response("view_prizes/team_winners.html", {
        "prize": prize,
        "prize_team_winners": teams,
    }, context_instance=RequestContext(request))


def prize_summary(request, round_name):
    """display summary of the winners."""

    round_name = round_name.replace('-', ' ').capitalize()
    individual_team_prize = Prize.objects.filter(round=RoundSetting.objects.get(name=round_name),
                         competition_type="points",
                         award_to="individual_team")
    teams = Team.objects.all()

    if individual_team_prize:
        individual_team_prize = individual_team_prize[0]
        for team in teams:
            team.leader = individual_team_prize.leader(team=team)

    team_energy_goal_prize = Prize.objects.filter(round=RoundSetting.objects.get(name=round_name),
                         competition_type="energy_goal",
                         award_to="team_overall")
    energy_team_ra = None
    if team_energy_goal_prize:
        team_energy_goal_prize = team_energy_goal_prize[0]
        energy_team_ra = Profile.objects.filter(team__name=team_energy_goal_prize.leader(),
                               is_ra=True)

    team_points_prize = Prize.objects.filter(round=RoundSetting.objects.get(name=round_name),
                                             competition_type="points",
                                             award_to="team_overall")
    point_team_ra = None
    if team_points_prize:
        team_points_prize = team_points_prize[0]
        point_team_ra = Profile.objects.filter(team__name=team_points_prize.leader(),
                                                is_ra=True)

    points_leader = score_mgr.player_points_leaders(round_name=round_name)
    if points_leader:
        points_leader = points_leader[0]
    return render_to_response("view_prizes/summary.html", {
        "team_energy_goal_prize": team_energy_goal_prize,
        "energy_team_ra": energy_team_ra,
        "goal": resource_goal.resource_goal_ranks("energy", round_name)[0]["completions"],

        "team_points_prize": team_points_prize,
        "team_point": team_mgr.team_points_leaders(round_name=round_name)[0]["points"],
        "team_participation": team_mgr.team_active_participation(
            round_name=round_name)[0].active_participation,
        "point_team_ra": point_team_ra,

        "individual_overall_prize": Prize.objects.filter(
                                    round=RoundSetting.objects.get(name=round_name),
                                                  competition_type="points",
                                                  award_to="individual_overall")[0],
        "individual_point": points_leader["points"] if points_leader else None,

        "individual_team_prize": individual_team_prize,
        "teams": teams
    }, context_instance=RequestContext(request))


@never_cache
@login_required
def bulk_round_change(request, action_type, attribute):
    """Handle change Round for selected prizes from Admin interface."""
    _ = action_type
    _ = attribute
    prize_ids = request.GET["ids"]
    prizes = []
    for pk in prize_ids.split(","):
        prizes.append(Prize.objects.get(pk=pk))

    if request.method == "POST":
        r = request.POST["round_choice"]
        for prize in prizes:
            if r != '':
                prize.round = RoundSetting.objects.get(pk=r)
            else:
                prize.round = None
            try:
                prize.save()
            except IntegrityError:
                # what should we do? Redirect to error page?
                pass

        return HttpResponseRedirect("/admin/prizes/prize")
    else:
        form = ChangePrizeRoundForm(initial={"ids": prize_ids})
        return render_to_response("admin/bulk_change.html", {
            "attribute": "Round",
            "prizes": prizes,
            "action_type": None,
            "form": form,
            }, context_instance=RequestContext(request))
