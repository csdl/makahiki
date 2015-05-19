#!/usr/bin/python

"""
Invocation:  scripts/initialize_instance .py -t|--type[=] default|demo|test
                                             -r|--heroku[=] <heroku_app>
                                             -d|--docker

Use this script to create an instance with different types of configuration:

[default]: includes the basic configuration. The admin needs to create
           the settings for rounds, resources, resource goals, teams and
           users, prizes, etc. Uses internal authentication.

[test]   : includes all of "default" configuration, with more test users
           and data. Uses CAS authentication.

if -r or --heroku is specified, it will initialize the instance in the specified
heroku app.

Performs the following:
  * installation of any modules in requirements.txt
  * re-create the database and database user
  * Synchronize and migrates the database schemas.
  * Collects and copies the static and media files to the specific location.
  * Loads the default or test configuration of data.
"""

import getopt
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep)
from apps.utils import script_utils


def main(argv):
    """main function."""

    instance_type = None
    heroku_app = None
    manage_py = script_utils.manage_py_command()
    manage_command = "python " + manage_py
    fixture_path = "fixtures"

    try:
        opts, args = getopt.getopt(argv, "t:r:dh", ["type=", "heroku=", "docker", "help"])
    except getopt.GetoptError:
        script_utils.exit_with_help(__doc__)

    if not opts:
        script_utils.exit_with_help(__doc__)

    for opt in opts:
        if opt[0] == "-h" or opt[0] == "--help":
            script_utils.exit_with_help(__doc__)
        if opt[0] == "-t" or opt[0] == "--type":
            instance_type = opt[1]
        if opt[0] == "-d" or opt[0] == "--docker":
            is_docker = True
            fixture_path = os.path.join("makahiki", fixture_path)
        if opt[0] == "-r" or opt[0] == "--heroku":
            heroku_app = opt[1]
            manage_command = "heroku run --app %s python makahiki/manage.py" % heroku_app

    if not instance_type in ("default", "demo", "test", "uh12"):
        script_utils.exit_with_help(__doc__)

    _ = args

    if not is_docker:
        if not heroku_app:
            script_utils.install_requirements()
        else:
            script_utils.create_heroku_app(heroku_app)
            script_utils.push_to_heroku(heroku_app)

        script_utils.reset_db(heroku_app)

    script_utils.syncdb(manage_command)

    script_utils.copy_static_media(heroku_app)

    script_utils.load_data(manage_command, instance_type, fixture_path)


if __name__ == '__main__':
    main(sys.argv[1:])
