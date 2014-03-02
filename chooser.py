#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

def solve_conflict(lit_date, choices):
    if lit_date.to_date() == datetime.date(year=2014, month=6, day=28):
        assert len(choices) == 2
        if choices[0][1].title == u"S. Ireneo, vescovo e martire":
            return [choices[1], choices[0]]
        else:
            return choices

    raise NotImplementedError()
