#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import datetime

from database import Session, Reading
from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering, quotes_intersect, BadQuoteException
from utils import PrependStream
from editor import Editor
from liturgy import get_lit_date, SelectingMassException

def main():
    from_date = datetime.date(*map(int, sys.argv[1].split('-')))
    to_date = datetime.date(*map(int, sys.argv[2].split('-')))
    assert from_date <= to_date
    quote = decode_quote(sys.argv[3])
    #print quote

    session = Session()
    lit_years = {}
    date = from_date
    while date <= to_date:
        found = False
        session.rollback()
        lit_date = get_lit_date(date, lit_years, session)
        masses = []
        try:
            masses = lit_date.get_masses(strict=True)
        except SelectingMassException:
            pass
        for mass in masses:
            if found:
                break
            for reading in mass.readings:
                try:
                    verses = decode_quote(reading.quote)
                except BadQuoteException:
                    pass
                if quotes_intersect(quote, verses):
                    print date
                    found = True
                    break
        date += datetime.timedelta(days=1)

if __name__ == '__main__':
    main()
