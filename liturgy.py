#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import calendar

from general_calendar import *
from utils import int_to_roman, iteryeardates

def get_prev_sunday(date):
    return date - datetime.timedelta(days=date.weekday() + 1)

def get_next_sunday(date):
    return date + datetime.timedelta(days=7 - (date.weekday() + 1) % 7)

def get_advent_first(year):
    christmas = get_christmas(year)
    fourth = get_prev_sunday(christmas)
    first = fourth - datetime.timedelta(days=3 * 7)
    return first

def get_novena_beginning(year):
    return datetime.date(year, 12, 17)

def get_christmas(year):
    return datetime.date(year, 12, 25)

def get_christmas_octave(year):
    return datetime.date(year, 1, 1)

def get_epiphany(year):
    return datetime.date(year, 1, 6)

def get_baptism(year):
    epiphany = get_epiphany(year)
    return get_next_sunday(epiphany)

def get_ash_day(year):
    return get_easter(year) - datetime.timedelta(days=46)

def get_palm_day(year):
    return get_easter(year) - datetime.timedelta(days=7)

def get_holy_thursday(year):
    return get_easter(year) - datetime.timedelta(days=3)

# Taken from http://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
def get_easter(year):
    "Returns Easter as a date object."
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1    
    return datetime.date(year, month, day)

def get_easter_octave(year):
    return get_easter(year) + datetime.timedelta(days=7)

def get_ascension(year):
    return get_easter(year) + datetime.timedelta(days=42)

def get_pentecost(year):
    return get_easter(year) + datetime.timedelta(days=49)

def get_christ_king(year):
    return get_advent_first(year) - datetime.timedelta(days=7)

DIGIT_MAP = {0: 2, 1: 1}
LETTER_MAP = {0: 'C', 1: 'A', 2: 'B'}
PSALTER_WEEK_MAP = {0: 4, 1: 1, 2: 2, 3: 3}

SEASON_ADVENT = 0
SEASON_CHRISTMAS = 1
SEASON_ORDINARY_I = 2
SEASON_LENT = 3
SEASON_EASTER = 4
SEASON_ORDINARY_II = 5
SEASON_NUM = 6

WD_MONDAY = 0
WD_TUESDAY = 1
WD_WEDNESDAY = 2
WD_THURSDAY = 3
WD_FRIDAY = 4
WD_SATURDAY = 5
WD_SUNDAY = 6

WEEKDAYS_ITALIAN = {
    WD_MONDAY: u'lunedì',
    WD_TUESDAY: u'martedì',
    WD_WEDNESDAY: u'mercoledì',
    WD_THURSDAY: u'giovedì',
    WD_FRIDAY: u'venerdì',
    WD_SATURDAY: u'sabato',
    WD_SUNDAY: u'domenica',
}

SEASONS_ITALIAN = {
    SEASON_ADVENT: 'tempo di avvento',
    SEASON_CHRISTMAS: 'tempo di Natale',
    SEASON_ORDINARY_I: 'tempo ordinario',
    SEASON_LENT: 'tempo di quaresima',
    SEASON_EASTER: 'tempo di Pasqua',
    SEASON_ORDINARY_II: 'tempo ordinario',
}

BASE_TITLE_ITALIAN = '%s della %s settimana del %s'

def get_season_beginning(ref_year, season):
    """Returns (first_day, ref_sunday, week_num)."""
    if season == SEASON_ADVENT:
        first_day = get_advent_first(ref_year - 1)
        ref_sunday = first_day
        week_num = 1
    elif season == SEASON_CHRISTMAS:
        first_day = get_christmas(ref_year - 1)
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

PRI_TRIDUUM = 1
PRI_CHRISTMAS = 2
PRI_SOLEMNITIES = 3
PRI_LOCAL_SOLEMNITIES = 4
PRI_LORD_FEASTS = 5
PRI_SUNDAYS = 6
PRI_OTHER_FEASTS = 7
PRI_LOCAL_FEASTS = 8
PRI_STRONG_WEEKDAYS = 9
PRI_MEMORIES = 10
PRI_LOCAL_MEMORIES = 11
PRI_OPTIONAL_MEMORIES = 12
PRI_WEEKDAYS = 13
PRI_UNCHOSEN_OPT_MEM = 14

TYPE_TO_PRIORITY = {
    TYPE_SOLEMNITY: PRI_SOLEMNITIES,
    TYPE_LORD_FEAST: PRI_LORD_FEASTS,
    TYPE_FEAST: PRI_OTHER_FEASTS,
    TYPE_MEMORY: PRI_MEMORIES,
    TYPE_OPTIONAL_MEMORY: PRI_UNCHOSEN_OPT_MEM,
}

class LitDate(datetime.date):

    def __init__(self, year, month, day):
        datetime.date.__init__(self, year, month, day)
        self.ref_year = year if self < get_advent_first(year) else year + 1
        self.digit = DIGIT_MAP[self.ref_year % 2]
        self.letter = LETTER_MAP[self.ref_year % 3]
        self.season, self.week = self.get_season()
        self.psalter_week = PSALTER_WEEK_MAP[self.week % 4]

    @classmethod
    def from_date(cls, date):
        return LitDate(date.year, date.month, date.day)

    def get_season(self):
        for season in xrange(SEASON_NUM-1, -1, -1):
            first_day, ref_sunday, week_num = get_season_beginning(self.ref_year, season)
            if self >= first_day:
                week = (self - ref_sunday).days / 7 + week_num
                return (season, week)

    def get_base_priority(self):
        is_sunday = self.weekday() == WD_SUNDAY

        if self.season == SEASON_ADVENT:
            if is_sunday:
                return PRI_CHRISTMAS
            if self < get_novena_beginning(self.ref_year - 1):
                return PRI_WEEKDAYS
            return PRI_STRONG_WEEKDAYS

        elif self.season == SEASON_CHRISTMAS:
            if self == get_christmas(self.ref_year - 1):
                return PRI_CHRISTMAS
            if self == get_epiphany(self.ref_year):
                return PRI_CHRISTMAS
            if is_sunday:
                return PRI_SUNDAYS
            if self < get_christmas_octave(self.ref_year):
                return PRI_STRONG_WEEKDAYS
            return PRI_WEEKDAYS

        elif self.season == SEASON_LENT:
            if self == get_ash_day(self.ref_year):
                return PRI_CHRISTMAS
            if self >= get_holy_thursday(self.ref_year):
                return PRI_TRIDUUM
            if is_sunday:
                return PRI_CHRISTMAS
            if self > get_palm_day(self.ref_year):
                return PRI_CHRISTMAS
            return PRI_STRONG_WEEKDAYS

        elif self.season == SEASON_EASTER:
            if self == get_easter(self.ref_year):
                return PRI_TRIDUUM
            if self == get_ascension(self.ref_year):
                return PRI_CHRISTMAS
            if self == get_pentecost(self.ref_year):
                return PRI_CHRISTMAS
            if is_sunday:
                return PRI_CHRISTMAS
            if self < get_easter_octave(self.ref_year):
                return PRI_CHRISTMAS
            return PRI_WEEKDAYS

        elif self.season == SEASON_ORDINARY_I or self.season == SEASON_ORDINARY_II:
            if is_sunday:
                return PRI_SUNDAYS
            return PRI_WEEKDAYS

    def get_base_competitor(self):
        title = BASE_TITLE_ITALIAN % (WEEKDAYS_ITALIAN[self.weekday()],
                                      int_to_roman(self.week),
                                      SEASONS_ITALIAN[self.season])
        return (self.get_base_priority(), title)

    def get_calendar_competitors(self):
        res = []
        if (self.month, self.day) not in GENERAL_CALENDAR:
            return []
        for title, type_ in GENERAL_CALENDAR[(self.month, self.day)]:
            priority = TYPE_TO_PRIORITY[type_]
            res.append((priority, title))
        return res

    def get_competitors(self):
        res = []
        res.append(self.get_base_competitor())
        res += self.get_calendar_competitors()
        return res

if __name__ == '__main__':
    for date in iteryeardates(2013):
        ld = LitDate.from_date(date)
        print date, sorted(ld.get_competitors())
    #print LitDate(2013, 4, 22).get_competitors()
    #print LitDate(2013, 12, 25).get_competitors()
