#!/usr/bin/python
# -*- coding: utf-8 -*-

# Taken from http://en.wikipedia.org/wiki/Psalms#Numbering
PSALMS_TABLE = [
    ((1, 8), (1, 8)),
    ((9, 10), (9, 9)),
    ((11, 113), (10, 112)),
    ((114, 115), (113, 113)),
    ((116, 116), (114, 115)),
    ((117, 146), (116, 145)),
    ((147, 147), (146, 147)),
    ((148, 150), (148, 150)),
    ]

def masoretic_to_septuagint(num):
    for (a, b), (c, d) in PSALMS_TABLE:
        if a <= num and num <= b:
            if a == b or c == d:
                return c, d
            else:
                return c + (num - a), c + (num - a)

def septuagint_to_masoretic(num):
    for (c, d), (a, b) in PSALMS_TABLE:
        if a <= num and num <= b:
            if a == b or c == d:
                return c, d
            else:
                return c + (num - a), c + (num - a)
