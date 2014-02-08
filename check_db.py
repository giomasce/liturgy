#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from database import Session, Event, Mass, Reading
from quote import canonicalise_quote, decode_quote, BadQuoteException
from scrape import scrape_file
from utils import real_itermonthdays, PrependStream
from abbreviations import ABBR_VATICAN

from sqlalchemy.orm import joinedload

def check_orphans(session, loud, delete_orphans):
    for mass in session.query(Mass).options(joinedload(Mass.event)):
        if mass.event is None:
            print "> Mass %d is orphan" % (mass.id)
            if delete_orphans:
                session.delete(mass)

    for reading in session.query(Reading).options(joinedload(Reading.mass)):
        if reading.mass is None:
            print "> Reading %d is orphan" % (reading.id)
            if delete_orphans:
                session.delete(reading)

def check_readings(session, loud):
    for reading in session.query(Reading):
        valid_quote = True
        canonical_quote = True
        status = reading.quote_status.split(' ')

        # Try to decode quote
        try:
            decode_quote(reading.quote, allow_only_chap=True, valid_abbr=ABBR_VATICAN)
        except BadQuoteException:
            valid_quote = False

        # Try to canonicalise quote
        if valid_quote and reading.quote != canonicalise_quote(reading.quote):
            canonical_quote = False

        if not valid_quote:
            if loud or 'invalid' not in status:
                print "> Reading %d in event %s: quote %s is invalid" % (reading.id, reading.mass.event.title, reading.quote)

        if not canonical_quote:
            if loud or 'not-canonical' not in status:
                print "> Reading %d in event %s: quote %s is not canonical" % (reading.id, reading.mass.event.title, reading.quote)

def check_masses(session, loud):
    for mass in session.query(Mass):
        # TODO: check readings consistency
        pass

def check_events(session, loud):
    for event in session.query(Event).options(joinedload(Event.masses)):
        status = event.status.split(' ')
        complete = True
        at_least_one = False
        for letter in ['A', 'B', 'C']:
            for digit in ['1', '2']:
                good_masses = [mass for mass in event.masses if (mass.letter == letter or mass.letter == '*') and (mass.digit == digit or mass.digit == '*')]
                if len(good_masses) == 0:
                    complete = False
                else:
                    at_least_one = True
        if at_least_one and not complete:
            if loud or 'incomplete' not in status:
                print "> Event %d with title %s: missing masses" % (event.id, event.title)

def check_db(loud=False, delete_orphans=False):
    session = Session()

    check_orphans(session, loud, delete_orphans)
    check_readings(session, loud)
    check_masses(session, loud)
    check_events(session, loud)

    session.rollback()
    session.close()

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    check_db(loud='loud' in sys.argv[1:],
             delete_orphans='delete-orphans' in sys.argv[1:])
