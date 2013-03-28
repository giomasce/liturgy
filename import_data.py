#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import cPickle as pickle

from liturgy import calc_ref_year, build_dict_lit_year
from database import Session, Mass, Reading
from quote import canonical_quote, decode_quote

def get_lit_date(date, lit_years, session):
    ref_year = calc_ref_year(date)
    if ref_year not in lit_years:
        lit_years[ref_year] = build_dict_lit_year(ref_year, session)
    return lit_years[ref_year][date]

def main():
    data = pickle.load(sys.stdin)
    lit_years = {}
    session = Session()

    for piece in data:
        date = piece['date']
        lit_date = get_lit_date(date, lit_years, session)
        event = lit_date.get_winner()[1]
        quotes = map(lambda x: [None, canonical_quote(x)], piece['quotes'] + [piece['quote_vangelo']])
        quotes[-1][0] = piece['text_vangelo']

        mass = Mass()
        mass.order = 0
        mass.event = event
        mass.digit = lit_date.digit
        mass.letter = lit_date.letter
        mass.title = None
        session.add(mass)

        order = 0
        if len(quotes) == 4:
            titles = [u'Prima lettura', u'Salmo responsoriale', u'Seconda lettura', u'Vangelo']
        elif len(quotes) == 3:
            titles = [u'Prima lettura', u'Salmo responsoriale', u'Vangelo']
        # Domenica delle Palme
        elif len(quotes) == 5:
            titles = [u'Vangelo delle Palme', u'Prima lettura', u'Salmo responsoriale', u'Seconda lettura', u'Vangelo']
        # Pasqua
        elif len(quotes) == 17:
            titles = [u'Prima lettura',
                      u'Salmo responsoriale',
                      u'Seconda lettura',
                      u'Salmo responsoriale',
                      u'Terza lettura',
                      u'Salmo responsoriale',
                      u'Quarta lettura',
                      u'Salmo responsoriale',
                      u'Quinta lettura',
                      u'Salmo responsoriale',
                      u'Sesta lettura',
                      u'Salmo responsoriale',
                      u'Settima lettura',
                      u'Salmo responsoriale',
                      u'Epistola',
                      u'Salmo responsoriale',
                      u'Vangelo']
        else:
            raise Exception('Strange number of readings (%d)' % (len(quotes)))
        for (text, quote), title in zip(quotes, titles):
            reading = Reading()
            reading.order = order
            order += 1
            reading.alt_num = 0
            reading.mass = mass
            reading.title = title
            reading.quote = quote
            reading.text = text
            reading.quote_status = 'auto'
            if text is None:
                reading.text_status = 'missing'
            else:
                reading.text_status = 'auto'
            session.add(reading)

        # Write some interesting things
        print "%s:" % (date)
        print "  Indications: %s" % (piece['indications'])
        print "  Winner: %s" % (event.title)
        print "  Quotes: %s" % (quotes)
        print

    session.commit()
    session.close()

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    main()
