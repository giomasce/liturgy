#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import calendar

def get_prev_sunday(date):
    return date - datetime.timedelta(days=date.weekday() + 1)

def get_next_sunday(date):
    return date + date.timedelta(days=7 - (date.weekday() + 1) % 7)

def get_christmas(year):
    return datetime.date(year, 12, 25)

def get_advent_first(year):
    christmas = get_christmas(year)
    fourth = get_prev_sunday(christmas)
    first = fourth - datetime.timedelta(days=3 * 7)
    return first

def get_baptism(year):
    epiphany = datetime.date(year, 1, 6)
    return get_next_sunday(epiphany)

def get_ash_day(year):
    return get_easter(year) - datetime.timedelta(days=46)

def get_palm_day(year):
    return get_easter(year) - datetime.timedelta(days=7)

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

def get_pentecost(year):
    return get_easter(year) + datetime.timedelta(days=49)

def get_christ_king(year):
    return get_advent_first(year) - datetime.timedelta(days=7)

DIGIT_MAP = {0: 2, 1: 1}
LETTER_MAP = {0: 'C', 1: 'A', 2: 'B'}

SEASON_ADVENT = 0
SEASON_CHRISTMAS = 1
SEASON_ORDINARY_I = 2
SEASON_LENT = 3
SEASON_HOLY_WEEK = 4
SEASON_EASTER = 5
SEASON_ORDINARY_II = 6
SEASON_NUM = 7

def get_season_beginning(ref_year, season):
    """Returns (first_day, ref_sunday, week_num)."""
    if season == SEASON_ADVENT:
        first_day = get_advent_first(ref_year - 1)
        ref_sunday = first_day
        week_num = 1
    elif season == SEASON_CHRISTMAS:
        first_day = get_christmas(ref_year - 1)
        ref_sunday = get_prev_sunday(first_day)
        week_num = 1
    elif season == SEASON_ORDINARY_I:
        ref_sunday = get_baptism(ref_year)
        first_day = ref_sunday + datetime.timedelta(days=1)
        week_num = 1
    elif season == SEASON_LENT:
        first_day = get_ash_day(ref_year)
        ref_sunday = get_next_sunday(first_day)
        week_num = 1
    elif season == SEASON_HOLY_WEEK:
        first_day = get_palm_day(ref_year)
        ref_sunday = first_day
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
        self.ref_year = year if self < get_advent_first(year) else year + 1
        self.digit = DIGIT_MAP[self.ref_year % 2]
        self.letter = LETTER_MAP[self.ref_year % 3]
        self.season, self.week = self.get_season()

    def get_season(self):
        for season in xrange(SEASON_NUM-1, -1, -1):
            first_day, ref_sunday, week_num = get_season_beginning(self.ref_year, season)
            if self >= first_day:
                week = (self - ref_sunday).days / 7 + week_num
                return (season, week)
