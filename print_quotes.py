#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import json
import datetime

from database import Session, Mass
from liturgy import get_lit_date
from utils import PrependStream

def main():
    session = Session()

    if len(sys.argv[1:]) == 1:
        mass_id = int(sys.argv[1])
        masses = [session.query(Mass).filter(Mass.id == mass_id).one()]
    elif len(sys.argv[1:]) == 3:
        year, month, day = map(int, sys.argv[1:])
        lit_years = {}
        lit_date = get_lit_date(datetime.date(year, month, day), lit_years, session)
        masses = lit_date.get_masses(strict=True)
    else:
        print >> sys.stderr, "Wrong number of arguments"
        sys.exit(1)

    fout = PrependStream(sys.stdout, '# ')

    for mass in sorted(masses, key=lambda x: x.order):
        num_reading = max(map(lambda x: x.order, mass.readings)) + 1
        quotes = []
        alt_quotes = []

        print >> fout, "Mass #%d (%s) in event %s - ID: %d" % (mass.order, mass.title, mass.event.title, mass.id)
        for reading in sorted(mass.readings, key=lambda x: (x.order, x.alt_num)):
            print >> fout, "  Lettura #%d.%d (%s): %s - ID: %d" % (reading.order, reading.alt_num, reading.title, reading.quote, reading.id)

        for i in xrange(num_reading):
            [reading] = filter(lambda x: x.order == i and x.alt_num == 0, mass.readings)
            if reading.only_on_sunday:
                alt_quotes[0].append(reading.quote)
                continue
            quotes.append(reading.quote)
            alt_quotes.append(map(lambda x: x.quote, sorted(filter(lambda x: x.order == i and x.alt_num > 0, mass.readings), key=lambda x: x.alt_num)))

        sys.stdout.write("citazioni: %s\n" % (json.dumps(quotes)))
        sys.stdout.write("citazioni_alt: %s\n" % (json.dumps(alt_quotes)))

    session.rollback()

if __name__ == '__main__':
    main()
