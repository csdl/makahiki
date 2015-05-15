"""The manager for managing players."""
import csv

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from apps.managers.player_mgr.models import Profile
from apps.managers.score_mgr import score_mgr
from apps.managers.team_mgr.models import Team


def get_active_player(username):
    """return User object if the player is active, otherwise, return None"""
    try:
        username = username.lower()
        user = User.objects.get(username=username)
        return user if user.is_active else None
    except ObjectDoesNotExist:
        return None


def players(num_results=None):
    """Get some numbers of players."""

    results = Profile.objects.all()
    if num_results:
        results = results[:num_results]
    return results


def points_leader(round_name=None, place=1):
    """Returns the points leader (the first place) out of all users, as a Profile object."""
    entry = score_mgr.player_points_leader(round_name=round_name, place=place)
    if entry:
        return entry
    else:
        entries = Profile.objects.all()
        if len(entries) >= place:
            return entries[place - 1]
        else:
            return None


def points_leaders(num_results=None, round_name=None):
    """Returns the points leaders out of all users, as a dictionary object
    with profile__name and points.
    """
    entries = score_mgr.player_points_leaders(num_results=num_results, round_name=round_name)
    if entries:
        return entries
    else:
        results = Profile.objects.all().extra(
            select={'profile__name': 'name', 'points': 0}).values(
            'profile__name', 'points')
        if num_results:
            results = results[:num_results]
        return results


def username_is_lowercase(username):
    """Check that user names do not include uppercase letter characters."""
    username_input = username
    username_lower = username.lower()
    username_lowercase = False
    if username_input == username_lower:
        username_lowercase = True
    else:
        username_lowercase = False
    return username_lowercase


def create_player(username, password, email, firstname, lastname, team_name, is_ra):
    """Create a player with the assigned team"""
    try:
        user = User.objects.get(username=username)
        user.delete()
        print "Existing user '%s' deleted." % username
    except ObjectDoesNotExist:
        pass

    # Change uppercase letters to lowercase
    username_input = username
    username_lower = username.lower()
    invalid_username_message = "Username \"%s\" is invalid: usernames must not use uppercase \
    letters. User will be created with username \"%s\" instead." % (username_input, username_lower)
    if username_is_lowercase(username_input) == False:
        username = username_lower
        # Print warning message to console (not visible to the web UI)
        print invalid_username_message
    # Create user
    user = User.objects.create_user(username, email, password)
    user.first_name = firstname
    user.last_name = lastname
    user.save()

    profile = user.profile
    profile.is_ra = is_ra

    try:
        profile.team = Team.objects.get(name=team_name)
    except ObjectDoesNotExist:
        print "Can not find team '%s', set the team of the player '%s' to None." % \
              (team_name, profile.name)

    if user.first_name and user.last_name:
        firstname = user.first_name.capitalize()
        lastname = user.last_name.capitalize()
        profile.name = "%s %s." % (firstname, lastname[:1])
        if Profile.objects.filter(name=profile.name).exclude(user=user).exists():
            profile.name = firstname + " " + lastname

    profile.save()


def bulk_create_players(infile):
    """bulk create players from a csv file. Returns the number of user created."""

    load_count = 0
    reader = csv.reader(infile)
    for items in reader:
        team = items[0].strip()

        firstname = items[1].strip().capitalize()
        lastname = items[2].strip().capitalize()

        email = items[3].strip()
        username = items[4].strip()
        password = items[5].strip()

        if len(items) == 7:
            is_ra = True if items[6].strip().lower() == "ra" else False
        else:
            is_ra = False

        #print "%s,%s,%s,%s,%s,%s" % (team, firstname, lastname, email, username, is_ra)
        create_player(username, password, email, firstname, lastname, team, is_ra)

        load_count += 1
    return load_count


def bulk_load_player_properties(infile):
    """bulk load player profile properties from a csv file. Returns the number of
    properties loaded."""

    load_count = 0
    reader = csv.reader(infile)
    for items in reader:
        username = items[0].strip()
        properties = items[1].strip()

        p = Profile.objects.get(user__username=username)
        p.properties = properties
        p.save()

        load_count += 1
    return load_count


def reset_user(user):
    """Resets the given user by deleting them and then restoring them. """
    username = user.username
    email = user.email
    is_staff = user.is_staff
    is_superuser = user.is_superuser

    profile = user.profile
    d_name = profile.name
    team = profile.team

    # Delete the user and create a new one.
    user.delete()
    new_user = User.objects.create_user(username=username, email=email,
                                        password="")
    new_user.is_staff = is_staff
    new_user.is_superuser = is_superuser
    new_user.save()

    profile = new_user.profile
    profile.name = d_name
    profile.team = team

    profile.save()


def get_user_by_email(email):
    """Return the user from given email"""
    email = email.lower()
    try:
        return User.objects.get(email=email)
    except ObjectDoesNotExist:
        return None
