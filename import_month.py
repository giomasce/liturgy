#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import cPickle as pickle
import yaml
import json
import datetime

from liturgy import calc_ref_year, build_dict_lit_year, print_lit_date, get_lit_date
from database import Session, Mass, Reading
from quote import canonicalise_quote, decode_quote
from scrape import scrape_file
from utils import real_itermonthdays, PrependStream
from abbreviations import ABBR_VATICAN

def import_from_scrape(year, month):
    lit_years = {}
    session = Session()

    for day in real_itermonthdays(year, month):
        date = datetime.date(year, month, day)
        print >> sys.stderr, "Importing %s..." % (date)
        lit_date = get_lit_date(date, lit_years, session)
        event = lit_date.get_winner()[1]
        with open(os.path.join('scrape', '%04d-%02d-%02d.html' % (year, month, day))) as fhtml:
            quotes = scrape_file(fhtml)

        if u'auto' not in event.status.split(u' '):
            event.status += u' auto'

        mass = Mass()
        mass.order = 0
        mass.event = event
        mass.digit = lit_date.digit
        mass.letter = lit_date.letter
        mass.title = None
        mass.status = u'auto'
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

        for (quote, text), title in zip(quotes, titles):
            reading = Reading()
            reading.order = order
            order += 1
            reading.alt_num = 0
            reading.mass = mass
            reading.title = title
            reading.quote = canonicalise_quote(quote)
            reading.text = text
            try:
                decode_quote(quote, allow_only_chap=True, valid_abbr=ABBR_VATICAN)
            except:
                reading.quote_status = u'auto invalid'
            else:
                reading.quote_status = u'auto'
            if text is None:
                reading.text_status = u'missing'
            else:
                reading.text_status = u'auto'
            session.add(reading)

        session.flush()

        # Write some interesting things
        #print '#'
        #print_lit_date(lit_date, PrependStream(sys.stdout, '# '))
        #print
        #print json.dumps(event.as_dict(), encoding='utf-8', ensure_ascii=False, indent=2, sort_keys=True)
        #print

    session.commit()
    session.close()

# def import_from_pickle():
#     data = pickle.load(sys.stdin)
#     lit_years = {}
#     session = Session()

#     for piece in data:
#         date = piece['date']
#         lit_date = get_lit_date(date, lit_years, session)
#         event = lit_date.get_winner()[1]
#         quotes = map(lambda x: [None, canonicalise_quote(x)], piece['quotes'] + [piece['quote_vangelo']])
#         quotes[-1][0] = piece['text_vangelo']

#         mass = Mass()
#         mass.order = 0
#         mass.event = event
#         mass.digit = lit_date.digit
#         mass.letter = lit_date.letter
#         mass.title = None
#         mass.status = u'auto'
#         session.add(mass)

#         order = 0
#         if len(quotes) == 4:
#             titles = [u'Prima lettura', u'Salmo responsoriale', u'Seconda lettura', u'Vangelo']
#         elif len(quotes) == 3:
#             titles = [u'Prima lettura', u'Salmo responsoriale', u'Vangelo']
#         # Domenica delle Palme
#         elif len(quotes) == 5:
#             titles = [u'Vangelo delle Palme', u'Prima lettura', u'Salmo responsoriale', u'Seconda lettura', u'Vangelo']
#         # Pasqua
#         elif len(quotes) == 17:
#             titles = [u'Prima lettura',
#                       u'Salmo responsoriale',
#                       u'Seconda lettura',
#                       u'Salmo responsoriale',
#                       u'Terza lettura',
#                       u'Salmo responsoriale',
#                       u'Quarta lettura',
#                       u'Salmo responsoriale',
#                       u'Quinta lettura',
#                       u'Salmo responsoriale',
#                       u'Sesta lettura',
#                       u'Salmo responsoriale',
#                       u'Settima lettura',
#                       u'Salmo responsoriale',
#                       u'Epistola',
#                       u'Salmo responsoriale',
#                       u'Vangelo']
#         else:
#             raise Exception('Strange number of readings (%d)' % (len(quotes)))

#         for (text, quote), title in zip(quotes, titles):
#             reading = Reading()
#             reading.order = order
#             order += 1
#             reading.alt_num = 0
#             reading.mass = mass
#             reading.title = title
#             reading.quote = quote
#             reading.text = text
#             try:
#                 decode_quote(quote, allow_only_chap=True, valid_abbr=ABBR_VATICAN)
#             except:
#                 reading.quote_status = u'auto (invalid)'
#             else:
#                 reading.quote_status = u'auto'
#             if text is None:
#                 reading.text_status = u'missing'
#             else:
#                 reading.text_status = u'auto'
#             session.add(reading)

#         session.flush()

#         # Write some interesting things
#         print "#%s:" % (date)
#         print "#  Indications: %s" % (piece['indications'])
#         print "#  Winner: %s" % (event.title)
#         print
#         print json.dumps(event.as_dict(), encoding='utf-8', ensure_ascii=False, indent=2, sort_keys=True)
#         print

#     #session.commit()
#     session.close()

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    #import_from_pickle()
    import_from_scrape(*map(int, sys.argv[1:]))
