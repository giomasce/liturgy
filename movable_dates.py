#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

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
    return datetime.date(year - 1, 12, 17)

def get_christmas(year):
    return datetime.date(year - 1, 12, 25)

def get_saint_family(year):
    christmas = get_christmas(year)
    saint_family = get_next_sunday(christmas)
    if saint_family >= get_christmas_octave(year):
        saint_family = datetime.date(year - 1, 12, 30)
    return saint_family

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
    return get_advent_first(year + 1) - datetime.timedelta(days=7)
