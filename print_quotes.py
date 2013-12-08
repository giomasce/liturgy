#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import json

from database import Session, Mass

def main():
    mass_id = int(sys.argv[1])
    session = Session()
    mass = session.query(Mass).filter(Mass.id == mass_id).one()

    num_reading = max(map(lambda x: x.order, mass.readings)) + 1
    quotes = []
    alt_quotes = []

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
