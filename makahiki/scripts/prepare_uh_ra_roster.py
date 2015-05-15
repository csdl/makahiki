#!/usr/bin/python

"""
Invocation:  scripts/prepare_uh_roster.py infile outfile
"""

import csv
import sys


def main(args):
    """
    prepare the csv file from UH roster
    """
    if len(args) != 2:
        print "usage: prepare_uh_ra_roster infile outfile."
        return

    try:
        infile = open(args[0])
    except IOError:
        print "Can not open the file: %s , Aborting.\n" % args[0]
        return

    try:
        outfile = open(args[1], "wb")
    except IOError:
        print "Can not open the file: %s , Aborting.\n" % args[1]
        return

    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    row = 0
    for items in reader:
        row += 1
        if row == 1:
            # skip the first row
            continue

        # roster format:
        # "lastname, firstname",LO-358,email
        # First Last, Ilima 333, email
        names = items[0].strip().split(" ")
        lastname = names[1].strip().capitalize()
        firstname = names[0].strip().capitalize()
        email = items[2].strip()
        if not email.endswith("@hawaii.edu"):
            print "==== ERROR ==== non-hawaii edu email: %s" % email
            sys.exit(1)

        building_room = items[1].strip().split(" ")
        # LO-358
        building = building_room[0]
        room = building_room[1]

        team = get_team(building, room)

        username = email.split("@")[0]

        # output format: team, firstname, lastname, email, username, password[, RA]
        writer.writerow([team, firstname, lastname, email, username, '', 'RA'])
        # output the room number as the optional properties file
        #writer.writerow([username, 'room=%s;' % room])

    infile.close()
    outfile.close()


def get_team(building, room):
    """return the lounge name from the building and room info."""

    """
    if building == 'LE':
        building = 'Lehua'
    elif building == 'MO':
        building = 'Mokihana'
    elif building == 'IL':
        building = 'Ilima'
    elif building == 'LO':
        building = 'Lokelani'
    """

    floor = room.zfill(4)[:2]
    if floor == '03' or floor == '04':
        floor = 'A'
    elif floor == '05' or floor == '06':
        floor = 'B'
    elif floor == '07' or floor == '08':
        floor = 'C'
    elif floor == '09' or floor == '10':
        floor = 'D'
    elif floor == '11' or floor == '12':
        floor = 'E'

    return building + '-' + floor


if __name__ == '__main__':
    main(sys.argv[1:])
