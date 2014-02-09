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

def check_readings(session, loud, fix):
    for reading in session.query(Reading):
        valid_quote = True
        canonical_quote = True
        quote_status = reading.quote_status.split(' ')
        text_status = reading.text_status.split(' ')

        # Try to decode quote
        try:
            decode_quote(reading.quote, allow_only_chap=True, valid_abbr=ABBR_VATICAN)
        except BadQuoteException:
            valid_quote = False

        # Try to canonicalise quote
        if valid_quote and reading.quote != canonicalise_quote(reading.quote):
            canonical_quote = False

        if not valid_quote:
            if loud or 'invalid' not in quote_status:
                print "> Reading %d in event %s: quote %s is invalid" % (reading.id, reading.mass.event.title, reading.quote)

        if not canonical_quote:
            if loud or 'not-canonical' not in quote_status:
                print "> Reading %d in event %s: quote %s is not canonical" % (reading.id, reading.mass.event.title, reading.quote)

        # Check if text is the empty string (should never happen)
        if reading.text == '':
            print "> Reading %d in event %s: text is the empty string" % (reading.id, reading.mass.event.title)
            if fix:
                reading.text = None

        # Ensure that text is None iff the status contains "missing"
        if (reading.text is None) != ('missing' in text_status):
            print "> Reading %d in event %s: text presence is not aligned with status" % (reading.id, reading.mass.event.title)

        # Ensure that if text is ok, then it is padded to 80 columns
        if 'ok' in text_status:
            lines = reading.text.splitlines()
            if max([len(line.strip()) for line in lines]) > 80:
                print "> Reading %d in event %s: there are long lines" % (reading.id, reading.mass.event.title)

def check_masses(session, loud):
    for mass in session.query(Mass):

        # Check that at least one between digit and letter is '*'
        if mass.digit != '*' and mass.letter != '*':
            print "> Mass %d in event %s: wrong digit or letter" % (mass.id, mass.event.title)

    # TODO: check readings consistency

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

    # TODO: check that readings with corresponding quotes in different
    # masses belonging to the same event actually have the same text

def check_db(loud=False, delete_orphans=False, fix=False):
    session = Session()

    check_orphans(session, loud, delete_orphans)
    check_readings(session, loud, fix)
    check_masses(session, loud)
    check_events(session, loud)

    #session.commit()
    session.rollback()
    session.close()

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    check_db(loud='loud' in sys.argv[1:],
             delete_orphans='delete-orphans' in sys.argv[1:],
             fix='fix' in sys.argv[1:])
