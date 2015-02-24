#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import htmlentitydefs
import calendar
import urllib2
import shutil
from BeautifulSoup import BeautifulSoup as BS
from BeautifulSoup import BeautifulStoneSoup as BSS

import utils

# Abbreviations on Silvestrini's website are in Vatican style

##
# Removes HTML or XML character references and entities from a text string.
# Taken from http://effbot.org/zone/re-sub.htm#unescape-html
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def my_generator(piece):
    for thing in piece.childGenerator():
        if 'name' in thing.__dict__ and thing.name == 'p':
            for thing2 in my_generator(thing):
                yield thing2
        else:
            yield thing

def interpret_div(div, h3_title, terminator, skip_heading=False):
    quote = None
    text = None
    for thing in my_generator(div):
        if 'name' in thing.__dict__:
            if thing.name == 'h3':
                if thing.text.upper().startswith(h3_title):
                    text = ''
            elif thing.name == 'em':
                if quote is None:
                    quote = thing.text
            elif thing.name == 'br':
                if text is not None and text != '':
                    text += '\n\n'
            elif thing.name in ['strong', 'div']:
                pass
            else:
                assert False, "Unkown tag %s" % (thing.name)
        else:
            if terminator is not None and thing.strip().startswith(terminator):
                break
            elif text is not None and thing.strip() != '':
                if text == '' and skip_heading and thing.strip().startswith('Da'):
                    pass
                else:
                    text += thing.strip()

    return quote, text

def scrape_file(fhtml):
    text = fhtml.read()
    soup = BS(text, convertEntities=BSS.HTML_ENTITIES)

    div_prima = soup.find('div', id='div_prima_lettura')
    div_salmo = soup.find('div', id='div_salmo')
    div_seconda = soup.find('div', id='div_seconda_lettura')
    div_vangelo = soup.find('div', id='div_vangelo')

    res = []
    res.append(interpret_div(div_prima, 'PRIMA LETTURA', 'C: Parola di Dio', skip_heading=True))
    res.append(interpret_div(div_salmo, 'SALMO RESPONSORIALE', None))
    second = interpret_div(div_seconda, 'SECONDA LETTURA', 'C: Parola di Dio', skip_heading=True)
    if second != (None, None):
        res.append(second)
    res.append(interpret_div(div_vangelo, 'VANGELO', 'C: Parola del Signore'))

    # Some substitutions for known bugs in the input files
    text_substs = [(u'\x96', u'-'),
                   (u'\u2019', u'\''),
                   (u'\xa0', u' '),        # Non breaking space
                   (u'\x87', u'‡'),
                   (u'á', u'à')]
    quote_substs = [(u'Sal.', u'Sal '),
                    (u'–', u'-')]
    for i in xrange(len(res)):
        quote, text = res[i]
        if quote is not None:
            for tag, value in quote_substs:
                quote = quote.replace(tag, value)
        if text is not None:
            for tag, value in text_substs:
                text = text.replace(tag, value)
            # Strip extremal whitespaces, leaving only a newline at the end
            text = text.strip() + "\n"
        res[i] = quote, text

    return res

DOWNLOAD_TEMPLATE = 'http://liturgia.silvestrini.org/letture/%04d-%02d-%02d.html'

def download_month(year, month):
    try:
        os.mkdir('scrape')
    except OSError:
        pass
    os.chdir('scrape')
    for day in utils.real_itermonthdays(year, month):
        if day == 0:
            continue

        filename = '%04d-%02d-%02d.html' % (year, month, day)

        # Skip already downloaded files
        if os.path.exists(filename):
            continue

        url = DOWNLOAD_TEMPLATE % (year, month, day)
        res = urllib2.urlopen(url)
        assert res is not None

        # First retrieve the whole page, then save it
        data = res.read()

        with open(filename, 'w') as fout:
            fout.write(data)

        print >> sys.stderr, "Created file %s" % filename

if __name__ == '__main__':
    #with open('test/2013-01-01.html') as fhtml:
    #    scrape_file(fhtml)
    download_month(*map(int, sys.argv[1:]))
