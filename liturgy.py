#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import calendar

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

class LitDate(datetime.date):

    def __init__(self, year, month, day):
        datetime.date.__init__(self, year, month, day)
        self.ref_year = year if self < get_advent_first(year + 1) else year + 1
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

    def get_season(self):
        for season in xrange(SEASON_NUM - 1, -1, -1):
            first_day, ref_sunday, week_num = get_season_beginning(self.ref_year, season)
            if self >= first_day:
                week = (self - ref_sunday).days / 7 + week_num
                return (season, week)

    def _get_base_competitor(self):
        is_sunday = self.weekday() == WD_SUNDAY
        if self.week > 0:
            title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[self.weekday()],
                                          int_to_roman(self.week),
                                          SEASONS_ITALIAN[self.season])

        if self.season == SEASON_ADVENT:
            if is_sunday:
                return PRI_CHRISTMAS, title
            if self < get_novena_beginning(self.ref_year):
                return PRI_WEEKDAYS, title
            return PRI_STRONG_WEEKDAYS, title

        elif self.season == SEASON_CHRISTMAS:
            if self == get_christmas(self.ref_year):
                return PRI_CHRISTMAS, u'Natale del Signore'
            if self == get_epiphany(self.ref_year):
                return PRI_CHRISTMAS, u'Epifania del Signore'
            if self == get_baptism(self.ref_year):
                return PRI_SUNDAYS, u'Battesimo del Signore'
            if is_sunday:
                return PRI_SUNDAYS, title
            if self < get_christmas_octave(self.ref_year):
                return PRI_STRONG_WEEKDAYS, u"%s dell'ottava di Natale" % (WEEKDAYS_ITALIAN[self.weekday()])
            return PRI_WEEKDAYS, title

        elif self.season == SEASON_LENT:
            if self == get_ash_day(self.ref_year):
                return PRI_CHRISTMAS, u'Mercoledì delle Ceneri'
            if self >= get_holy_thursday(self.ref_year):
                return PRI_TRIDUUM, u'%s santo' % (WEEKDAYS_ITALIAN[self.weekday()].capitalize())
            if self == get_palm_day(self.ref_year):
                return PRI_CHRISTMAS, u'Domenica delle Palme'
            if self.week == 0:
                return PRI_STRONG_WEEKDAYS, u'%s dopo le Ceneri' % (WEEKDAYS_ITALIAN[self.weekday()])
            if is_sunday:
                return PRI_CHRISTMAS, title
            if self > get_palm_day(self.ref_year):
                return PRI_CHRISTMAS, u'%s santo' % (WEEKDAYS_ITALIAN[self.weekday()].capitalize())
            return PRI_STRONG_WEEKDAYS, title

        elif self.season == SEASON_EASTER:
            if self == get_easter(self.ref_year):
                return PRI_TRIDUUM, u'Pasqua di Resurrezione'
            if self == get_ascension(self.ref_year):
                return PRI_CHRISTMAS, u'Ascensione del Signore'
            if self == get_pentecost(self.ref_year):
                return PRI_CHRISTMAS, u'Domenica di Pentecoste'
            if is_sunday:
                return PRI_CHRISTMAS, title
            if self < get_easter_octave(self.ref_year):
                return PRI_CHRISTMAS, u"%s dell'ottava di Pasqua" % (WEEKDAYS_ITALIAN[self.weekday()])
            return PRI_WEEKDAYS, title

        elif self.season == SEASON_ORDINARY_I or self.season == SEASON_ORDINARY_II:
            if self == get_christ_king(self.ref_year):
                return PRI_SUNDAYS, u"Nostro Signore Gesù Cristo Re dell'Universo"
            if is_sunday:
                return PRI_SUNDAYS, title
            return PRI_WEEKDAYS, title

    def _get_fixed_competitors(self):
        res = []
        for event in self.session.query(FixedEvent).filter(FixedEvent.day == self.day). \
                filter(FixedEvent.month == self.month):
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
        #res.append(self._get_base_competitor())
        res += self._get_fixed_competitors()
        res += self._get_timed_competitors()
        res += self._get_movable_competitors(movable_calendar)
        return sorted(res, key=lambda x: x[0])

def compute_movable_calendar(year, session):
    saint_family = get_saint_family(year)
    pentecost = get_pentecost(year)

    movable_calendar = {}
    for event in session.query(MovableEvent):
        # See http://lybniz2.sourceforge.net/safeeval.html about the
        # security of calling eval()
        date = eval(event.calc_func,
                    {"__builtin__": None,
                     "datetime": datetime},
                    {"saint_family": saint_family,
                     "pentecost": pentecost})
        if date not in movable_calendar:
            movable_calendar[date] = []
        movable_calendar[date].append(event)

    return movable_calendar

def build_lit_year(year):
    session = Session()
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

    return lit_year

def print_year(year):
    lit_year = build_lit_year(year)
    for ld in lit_year:
        print u'%s (%s, anno: %d)%s' % (ld, WEEKDAYS_ITALIAN[ld.weekday()], ld.ref_year, ' *' if ld.slid else '')
        for comp in ld.competitors:
            print u'  %2d: %s' % (comp[0], comp[1].title)
        print

def test_years():
    for year in range(1900, 2100):
        build_lit_year(year)

if __name__ == '__main__':
    import locale
    import codecs
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    print_year(int(sys.argv[1]))
    #test_years()
