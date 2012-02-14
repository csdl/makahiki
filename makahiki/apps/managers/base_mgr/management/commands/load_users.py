from django.core import management
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from managers.team_mgr.models import Team
from django.db.utils import IntegrityError

class Command(management.base.BaseCommand):
    help = 'load and create the users from a csv file containing lounge, name, and email, if the second argument is RA, the csv file is the RA list, consists of name, email, lounge.'

    lastname = None
    firstname = None
    username = None
    email = None
    lounge = None
    is_ra = False

    def handle(self, *args, **options):
        """
        Load and create the users from a csv file containing lounge, name, and email
        """
        if len(args) == 0:
            self.stdout.write("the csv file name missing.\n")
            return

        filename = args[0]
        try:
            infile = open(filename)
        except IOError:
            self.stdout.write(
                "Can not open the file: %s , Aborting.\n" % (filename))
            return

        if len(args) > 1:
            if args[1] == 'RA':
                self.is_ra = True
            else:
                self.stdout.write("the second argument can only be RA.\n")
                return

        error_count = 0
        load_count = 0
        for line in infile:
            if not self.parse_ok(line):
                error_count += 1
            else:
                self.create_user()
                load_count += 1

        infile.close()
        print "---- total loaded: %d , errors: %d" % (load_count, error_count)

    def parse_ok(self, line):
        items = line.split(":")

        if self.is_ra:
            names = items[0].split(",")
            self.lastname = names[0].strip().capitalize()
            self.firstname = names[1].strip().capitalize()
            self.username = items[1].strip()
            self.email = self.username + "@hawaii.edu"

            lounge_items = items[2].split()
            self.lounge = get_lounge(lounge_items[0].strip(),
                lounge_items[1].strip().zfill(4)[:2])
        else:
            lounge_items = items[0].split()

            self.lounge = get_lounge(lounge_items[2], lounge_items[3])

            self.firstname = items[1].strip().capitalize()
            middlename = items[2].strip().capitalize()
            if middlename:
                self.firstname += " " + middlename

            self.lastname = items[3].strip().capitalize()
            self.email = items[4].strip()
            self.username = self.email.split("@")[0]

        print "%s,%s,%s,%s,%s" % (
            self.lounge, self.firstname, self.lastname, self.email,
            self.username)

        if not self.email.endswith("@hawaii.edu"):
            print "==== ERROR ==== non-hawaii edu email: %s" % (self.email)
            return False
        else:
            return True

        def get_lounge(dorm, team):
            return get_dorm(dorm) + '-' + get_team(team)

        def get_dorm(dorm):
            return {
                'LE': 'Lehua',
                'MO': 'Mokihana',
                'IL': 'Ilima',
                'LO': 'Lokelani'}[dorm]

        def get_team(team):
            return {
                '03': 'A',
                '04': 'A',
                '05': 'B',
                '06': 'B',
                '07': 'C',
                '08': 'C',
                '09': 'D',
                '10': 'D',
                '11': 'E',
                '12': 'E'}[team]

    def create_user(self):
        try:
            user = User.objects.get(username=self.username)
            user.delete()
        except ObjectDoesNotExist:
            pass

        user = User.objects.create_user(self.username, self.email)
        user.first_name = self.firstname
        user.last_name = self.lastname
        user.save()

        profile = user.get_profile()
        profile.first_name = self.firstname
        profile.last_name = self.lastname
        profile.name = self.firstname + " " + self.lastname[:1] + "."
        profile.team = Team.objects.get(name=self.lounge)
        try:
            profile.save()
        except IntegrityError:
            profile.name = self.firstname + " " + self.lastname
            profile.save() 