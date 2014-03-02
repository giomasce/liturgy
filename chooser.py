#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

def solve_conflict(lit_date, choices):
    if lit_date.to_date() == datetime.date(year=2014, month=6, day=28):
        [ret] = [c for c in choices if c[1].title == u"S. Ireneo, vescovo e martire"]
        return ret

    raise NotImplementedError()
