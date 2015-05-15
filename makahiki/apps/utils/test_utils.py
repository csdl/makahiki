"""Test Unitilities"""
import datetime
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from apps.managers.challenge_mgr import challenge_mgr
from apps.managers.challenge_mgr.models import RoundSetting, GameInfo, GameSetting
from apps.managers.team_mgr.models import Team, Group
from apps.widgets.prizes.models import Prize
from apps.widgets.quests.models import Quest
from apps.widgets.smartgrid.models import Event, Activity, Commitment
from apps.widgets.smartgrid_design.models import DesignerEvent, DesignerCommitment, DesignerActivity


def setup_superuser(username, password):
    """creates a superuser"""
    user = User.objects.create_user(username=username, email=username + "@test.com",
                                    password=password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    group, _ = Group.objects.get_or_create(name="testgroup")
    team, _ = Team.objects.get_or_create(name="test_team", group=group)
    profile = user.profile
    profile.team = team
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    return user


def setup_user(username, password):
    """setup test user"""
    user = User.objects.create_user(username=username, email=username + "@test.com",
                                    password=password)
    group, _ = Group.objects.get_or_create(name="testgroup")
    team, _ = Team.objects.get_or_create(name="test_team", group=group)
    profile = user.profile
    profile.team = team
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    return user


def set_competition_round():
    """set the competition round for test. current date is in round 1"""
    start = datetime.datetime.today() - datetime.timedelta(days=1)
    end = start + datetime.timedelta(days=7)
    end2 = end + datetime.timedelta(days=7)
    RoundSetting.objects.all().delete()
    RoundSetting.objects.create(name="Round 1", start=start, end=end)
    RoundSetting.objects.create(name="Round 2", start=end, end=end2)
    challenge_mgr.init()


def set_three_rounds():
    """set three rounds for this test. current date is in round 2"""
    start = datetime.datetime.today() - datetime.timedelta(days=8)
    end1 = start + datetime.timedelta(days=7)
    end2 = end1 + datetime.timedelta(days=7)
    end3 = end2 + datetime.timedelta(days=7)
    RoundSetting.objects.all().delete()
    RoundSetting.objects.create(name="Round 1", start=start, end=end1)
    RoundSetting.objects.create(name="Round 2", start=end1, end=end2)
    RoundSetting.objects.create(name="Round 3", start=end2, end=end3)
    challenge_mgr.init()


def create_activity(slug=None, unlock_condition=None):
    """create test activity"""
    if not slug:
        slug = "test-activity"
    if not unlock_condition:
        unlock_condition = "True"

    return Activity.objects.create(
        title="Test activity",
        slug=slug,
        description="Testing!",
        expected_duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        unlock_condition=unlock_condition,
        confirm_type="text",
        type="activity",
    )


def create_commitment(slug=None, unlock_condition=None):
    """create test commiment"""
    if not slug:
        slug = "test-commitment"
    if not unlock_condition:
        unlock_condition = "True"

    return Commitment.objects.create(
        title="Test commitment",
        slug=slug,
        description="Testing",
        commitment_length=5,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        unlock_condition=unlock_condition,
        type="commitment",
    )


def create_event(slug=None, unlock_condition=None):
    """create test activity"""
    if not slug:
        slug = "test-event"
    if not unlock_condition:
        unlock_condition = "True"

    return Event.objects.create(
        title="Test event",
        description="Testing!",
        slug=slug,
        expected_duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
        unlock_condition=unlock_condition,
        type="event",
    )


def create_designer_activity(slug=None, unlock_condition=None, draft=None):
    """create test activity"""
    if not slug:
        slug = "test-activity"
    if not unlock_condition:
        unlock_condition = "True"

    return DesignerActivity.objects.create(
        title="Test activity",
        slug=slug,
        draft=draft,
        description="Testing!",
        expected_duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        unlock_condition=unlock_condition,
        confirm_type="text",
        type="activity",
    )


def create_designer_commitment(slug=None, unlock_condition=None, draft=None):
    """create test commiment"""
    if not slug:
        slug = "test-commitment"
    if not unlock_condition:
        unlock_condition = "True"

    return DesignerCommitment.objects.create(
        title="Test commitment",
        slug=slug,
        draft=draft,
        description="Testing",
        commitment_length=5,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        unlock_condition=unlock_condition,
        type="commitment",
    )


def create_designer_event(slug=None, unlock_condition=None, draft=None):
    """create test activity"""
    if not slug:
        slug = "test-event"
    if not unlock_condition:
        unlock_condition = "True"

    return DesignerEvent.objects.create(
        title="Test event",
        description="Testing!",
        draft=draft,
        slug=slug,
        expected_duration=10,
        point_value=10,
        pub_date=datetime.datetime.today(),
        expire_date=datetime.datetime.today() + datetime.timedelta(days=7),
        event_date=datetime.datetime.today() + datetime.timedelta(days=1),
        unlock_condition=unlock_condition,
        type="event",
    )


def create_teams(testcase):
    """Create test groups, teams, and users."""
    testcase.groups = [Group(name="Test Group %d" % i) for i in range(0, 2)]
    _ = [d.save() for d in testcase.groups]

    testcase.group = Group(name="Test Group")
    testcase.group.save()

    testcase.teams = [Team(name=str(i), group=testcase.group) for i in range(0, 2)]
    _ = [f.save() for f in testcase.teams]
    testcase.users = [User.objects.create_user(
        "test%d" % i, "test@test.com") for i in range(0, 4)]
    # Assign users to teams.
    for index, user in enumerate(testcase.users):
        user.profile.team = testcase.teams[index % 2]
        user.profile.save()


def setup_prize(award_to, competition_type):
    """set the prize for testing"""
    image_path = os.path.join(settings.PROJECT_ROOT, "fixtures", "test_images", "test.jpg")
    image = ImageFile(open(image_path, "r"))
    prize = Prize(
        title="Super prize!",
        short_description="A test prize",
        long_description="A test prize",
        image=image,
        award_to=award_to,
        competition_type=competition_type,
        value=5,
        )
    prize.save()
    return prize


def setup_round_prize(round_name, award_to, competition_type):
    """set the prize for testing"""
    prize = Prize(
        title="Super prize!",
        short_description="A test prize",
        long_description="A test prize",
        award_to=award_to,
        round=RoundSetting.objects.get(name=round_name),
        competition_type=competition_type,
        value=5,
        )
    prize.save()
    return prize


def create_quest(completion_conditions):
    """create the test quest"""
    quest = Quest(
            name="Test quest",
            quest_slug="test_quest",
            description="test quest",
            priority=1,
            unlock_conditions="True",
            completion_conditions=completion_conditions,
            )
    quest.save()
    return quest


def enable_game(name):
    """enable a game or game mechanics."""
    GameInfo.objects.get_or_create(name=name)


def enable_quest():
    """enable quest in the page."""
    game, _ = GameInfo.objects.get_or_create(name="Quest Game Mechanics")
    GameSetting.objects.get_or_create(game=game, widget="quests")
