#!/usr/bin/python
# -*- coding: utf-8 -*-

TYPE_SOLEMNITY = 0
TYPE_LORD_FEAST = 1
TYPE_FEAST = 2
TYPE_MEMORY = 3
TYPE_OPTIONAL_MEMORY = 4

DIGIT_MAP = {0: 2, 1: 1}
LETTER_MAP = {0: 'C', 1: 'A', 2: 'B'}
PSALTER_WEEK_MAP = {0: 4, 1: 1, 2: 2, 3: 3}

SEASON_ADVENT = 0
SEASON_CHRISTMAS = 1
SEASON_ORDINARY = 2
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
