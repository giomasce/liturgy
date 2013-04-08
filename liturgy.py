#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import calendar

from sqlalchemy import or_

from constants import *
from movable_dates import *
from utils import int_to_roman, iteryeardates, iterlityeardates
from database import Session, FixedEvent, MovableEvent, TimedEvent

def get_season_beginning(ref_year, season):
    """Returns (first_day, ref_sunday, week_num)."""
    if season == SEASON_ADVENT:
        first_day = get_advent_first(ref_year)
        ref_sunday = first_day
        week_num = 1
    elif season == SEASON_CHRISTMAS:
        first_day = get_christmas(ref_year)
        ref_sunday = get_next_sunday(first_day)
        week_num = 1
    elif season == SEASON_ORDINARY_I:
        ref_sunday = get_baptism(ref_year)
        first_day = ref_sunday + datetime.timedelta(days=1)
        week_num = 1
    elif season == SEASON_LENT:
        first_day = get_ash_day(ref_year)
        ref_sunday = get_next_sunday(first_day)
        week_num = 1
    elif season == SEASON_EASTER:
        first_day = get_easter(ref_year)
        ref_sunday = first_day
        week_num = 1
    elif season == SEASON_ORDINARY_II:
        ref_sunday = get_pentecost(ref_year)
        first_day = ref_sunday + datetime.timedelta(days=1)
        # week_num must be chosen so that the Solemnity of Christ the
        # King coincides with the 34th Sunday
        length = (get_christ_king(ref_year) - ref_sunday).days / 7
        week_num = 34 - length

    return (first_day, ref_sunday, week_num)

def calc_ref_year(date):
    return date.year if date < get_advent_first(date.year + 1) else date.year + 1

class LitDate(datetime.date):

    def __init__(self, year, month, day):
        datetime.date.__init__(self, year, month, day)
        self.ref_year = calc_ref_year(self)
        self.digit = DIGIT_MAP[self.ref_year % 2]
        self.letter = LETTER_MAP[self.ref_year % 3]
        self.season, self.week = self.get_season()
        self.psalter_week = PSALTER_WEEK_MAP[self.week % 4]
        self.slid = False

    def provide_movable_calendar(self, movable_calendar, session):
        self.session = session
        self.competitors = self._get_competitors(movable_calendar)

    @classmethod
    def from_date(cls, date, movable_calendar, session):
        ld = LitDate(date.year, date.month, date.day)
        ld.provide_movable_calendar(movable_calendar, session)
        return ld

    def to_date(self):
        return datetime.date(self.year, self.month, self.day)

    def get_season(self):
        for season in xrange(SEASON_NUM - 1, -1, -1):
            first_day, ref_sunday, week_num = get_season_beginning(self.ref_year, season)
            if self >= first_day:
                week = (self - ref_sunday).days / 7 + week_num
                # TODO - Fix this bad hack
                if season == SEASON_ORDINARY_I or season == SEASON_ORDINARY_II:
                    season = SEASON_ORDINARY
                return (season, week)

    def _get_fixed_competitors(self):
        res = []
        for event in self.session.query(FixedEvent).filter(FixedEvent.day == self.day). \
                filter(FixedEvent.month == self.month).filter(or_(FixedEvent.season == None, FixedEvent.season == self.season)):
            priority = event.priority if event.priority is not None else TYPE_TO_PRIORITY[event.type]
            res.append((priority, event))
        return res

    def _get_timed_competitors(self):
        res = []
        for event in self.session.query(TimedEvent).filter(TimedEvent.season == self.season). \
                filter(TimedEvent.week == self.week).filter(TimedEvent.weekday == self.weekday()):
            priority = event.priority if event.priority is not None else TYPE_TO_PRIORITY[event.type]
            res.append((priority, event))
        return res

    def _get_movable_competitors(self, movable_calendar):
        res = []
        if self not in movable_calendar:
            return []
        for event in movable_calendar[self]:
            priority = event.priority if event.priority is not None else TYPE_TO_PRIORITY[event.type]
            res.append((priority, event))
        return res

    def _get_competitors(self, movable_calendar):
        res = []
        res += self._get_fixed_competitors()
        res += self._get_timed_competitors()
        res += self._get_movable_competitors(movable_calendar)
        return sorted(res, key=lambda x: x[0])

    def get_winner(self):
        assert len(self.competitors) == 1 or self.competitors[0][0] != self.competitors[1][0]
        return self.competitors[0]

def compute_movable_calendar(year, session):
    movable_calendar = {}
    for event in session.query(MovableEvent):
        # See http://lybniz2.sourceforge.net/safeeval.html about the
        # security of calling eval()
        date = eval(event.calc_func,
                    {"__builtin__": None,
                     "datetime": datetime},
                    {"saint_family": get_saint_family(year),
                     "baptism": get_baptism(year),
                     "pentecost": get_pentecost(year),})
        if date not in movable_calendar:
            movable_calendar[date] = []
        movable_calendar[date].append(event)

    return movable_calendar

def build_lit_year(year, session):
    movable_calendar = compute_movable_calendar(year, session)
    lit_year = [LitDate.from_date(date, movable_calendar, session) for date in iterlityeardates(year)]
    session.close()

    # Compute sliding of solemnities
    queue = []
    for lit_date in lit_year:
        priorities = set(map(lambda x: x[0], lit_date.competitors))

        # Does this day requires sliding?
        if PRI_TRIDUUM in priorities or PRI_CHRISTMAS in priorities:
            for competitor in lit_date.competitors:
                if competitor[0] == PRI_SOLEMNITIES or competitor[0] == PRI_LOCAL_SOLEMNITIES:
                    queue.append(competitor)

        # Does this day receive sliding?
        elif len(queue) > 0 and min(priorities) >= PRI_STRONG_WEEKDAYS:
            lit_date.competitors.insert(0, queue.pop(0))
            lit_date.slid = True

    assert len(queue) == 0

    # Check that in every date there is exactly one winner
    for lit_date in lit_year:
        if not (len(lit_date.competitors) == 1 or lit_date.competitors[0][0] != lit_date.competitors[1][0]):
            print >> sys.stderr, "WARNING! Winner is not unique on day %s" % (lit_date)

    return lit_year

def build_dict_lit_year(year, session):
    return dict([(lit_date.to_date(), lit_date) for lit_date in build_lit_year(year, session)])

def print_lit_date(ld):
    print u'%s (weekday: %d, year: %d)%s' % (ld, ld.weekday(), ld.ref_year, ' *' if ld.slid else '')
    for comp in ld.competitors:
        print u'  %2d: %s' % (comp[0], comp[1].title)
    print

def print_year(year):
    session = Session()
    lit_year = build_lit_year(year, session)
    for ld in lit_year:
        print_lit_date(ld)
    session.close()

def print_date(date):
    session = Session()
    ref_year = calc_ref_year(date)
    lit_year = build_dict_lit_year(ref_year, session)
    print_lit_date(lit_year[date])
    session.close()

def test_years():
    for year in range(1900, 2100):
        build_lit_year(year)

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    if len(sys.argv) == 1:
        print_year(calc_ref_year(datetime.date.today()))
    elif len(sys.argv) == 2:
        print_year(int(sys.argv[1]))
    elif len(sys.argv) == 4:
        print_date(datetime.date(int(sys.argv[3]), int(sys.argv[2]), int(sys.argv[1])))
    #test_years()
