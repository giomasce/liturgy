#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from database import Session, Event, Mass, Reading
from quote import canonicalise_quote, decode_quote, BadQuoteException
from scrape import scrape_file
from utils import real_itermonthdays, PrependStream
from abbreviations import ABBR_VATICAN

def check_db(loud=False):
    session = Session()

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
                print "> Reading %d: quote %s is invalid" % (reading.id, reading.quote)

        if not canonical_quote:
            if loud or 'not-canonical' not in status:
                print "> Reading %d: quote %s is not canonical" % (reading.id, reading.quote)

    session.rollback()
    session.close()

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    check_db(loud='loud' in sys.argv[1:])
