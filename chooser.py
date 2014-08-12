#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

CONFLICTS = {
    datetime.date(year=2014, month=6, day=28): [u"Cuore Immacolato della beata Vergine Maria",
                                                u"S. Ireneo, vescovo e martire"],
    datetime.date(year=2015, month=6, day=13): [u"Cuore Immacolato della beata Vergine Maria",
                                                u"S. Antonio da Padova, sacerdote e dottore della Chiesa"]
}

def reorder_choices(choices, ordered_titles):
    assert len(choices) == len(ordered_titles)
    assert len(set(ordered_titles)) == len(ordered_titles)
    assert len(choices) == len(set([x[1] for x in choices]))
    as_dict = dict([(x[1].title, (x[0], x[1])) for x in choices])
    return [as_dict[x] for x in ordered_titles]

def solve_conflict(lit_date, choices):
    return reorder_choices(choices, CONFLICTS[lit_date.to_date()])

    raise NotImplementedError()
