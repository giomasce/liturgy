#!/usr/bin/python
# -*- coding: utf-8 -*-

from psalms import masoretic_to_septuagint, septuagint_to_masoretic
from abbreviations import PSALMS_ABBR

class BadQuoteException(Exception):
    pass

def split_shards(s):
    if s is None:
        return None

    def get_type(c):
        # Digits or alphanumeric characters (found sometimes in verse
        # numbers)
        if c.isdigit() or c.isalpha():
            return 0

        # Punctuation signs
        elif c in [',', '.', ';', '-']:
            return 1

        # Bad characters
        else:
            raise Exception("Wrong char %c" % (c))

    shards = []
    shard = None
    type_ = None
    for c in s:
        new_type = get_type(c)
        if new_type != type_:
            if shard != None:
                shards.append(shard)
            shard = ''
            type_ = new_type
        shard = shard + c
    shards.append(shard)

    return shards

def my_int(s):
    """Wrap int() into the removal of all non-digit characters. The
    input '-1' is treated specially: it just returns a very high
    number, supposed to be greater than any verse number appearing in
    the Bible.

    """
    if s == '-1':
        return 1000000
    return int(str(filter(lambda x: x.isdigit(), s)))

def decode_quote(quote, allow_only_chap=False, valid_abbr=None):
    """Decode a quote. An exception is casted if and only if the quote
    is (syntactically) invalid.

    The verses corresponding to the quote are returned, as a
    list. Each element of the list is a tuple with two elements,
    indicating the beginning and ending a consecutive run of verses
    (extrema are to be included). Each element of such tuple is
    another tuple of strings in the form (book, chapter, verse). No
    attempt to decode book names or characters in chapters and verses
    is performed. No attempt to check monotonicity of numbers is
    performed.

    A verse value of '-1' indicates the last verse in the chapter.

    If allow_only_chap is True, a quote without verses indication is
    accepted, otherwise it isn't.

    If valid_abbr is not None, it is interpreted as a list of all the
    acceptable abbreviations for Bible books. The quote is checked to
    employ one of these abbreviations.

    """

    if quote is None:
        return None

    #print quote

    verses = []
    quote = canonicalise_quote(quote)
    try:
        book, quote = quote.split(' ', 1)
    except ValueError:
        raise BadQuoteException("Could not split %s" % (quote))

    if valid_abbr is not None and book not in valid_abbr:
        raise BadQuoteException("Book %s not valid" % (book))

    quote = quote.replace(' ', '')
    shards = split_shards(quote)
    shards.append('/')
    #print quote
    #print shards

    state = 'chap'
    now_num = True
    chap = None
    verse = None
    first_chap = None
    first_verse = None
    second_chap = None
    second_verse = None
    second_unknown = None
    for shard in shards:
        #print shard, state, verses

        if state == 'end':
            assert(shard == '/')
            break

        if now_num:
            if state == 'chap':
                chap = shard
            elif state == 'verse':
                verse = shard
            elif state == 'second_unknown':
                second_unknown = shard
            elif state == 'second_verse':
                second_verse = shard
            elif state == 'second_chap':
                second_chap = chap
            else:
                raise BadQuoteException('Bad syntax for quote %s' % (quote))
        else:
            if state == 'chap':
                if shard == ',':
                    state = 'verse'
                elif allow_only_chap and shard == '/':
                    verses.append(((book, chap, '1'),
                                   (book, chap, '-1')))
                    state = 'end'
                elif allow_only_chap and shard == '-':
                    first_chap = chap
                    state = 'second_chap'
                else:
                    raise BadQuoteException('Bad syntax for quote %s' % (quote))

            elif state == 'second_chap':
                verses.append(((book, first_chap, 1),
                               (book, second_chap, -1)))
                if shard == '/':
                    state = 'end'
                elif shard == ';':
                    state = 'chap'
                else:
                    raise BadQuoteException('Bad syntax for quote %s' % (quote))

            elif state == 'verse':
                if shard == '.' or shard == '/' or shard == ';':
                    verses.append(((book, chap, verse),
                                   (book, chap, verse)))
                    if shard == '/':
                        state = 'end'
                    elif shard == ';':
                        state = 'chap'
                elif shard == '-':
                    first_chap = chap
                    first_verse = verse
                    state = 'second_unknown'
                else:
                    raise BadQuoteException('Bad syntax for quote %s' % (quote))

            elif state == 'second_unknown':
                if shard == ';' or shard == '.' or shard == '/':
                    second_chap = chap
                    second_verse = second_unknown
                    verses.append(((book, first_chap, first_verse),
                                   (book, second_chap, second_verse)))
                    if shard == ';':
                        state = 'chap'
                    elif shard == '.':
                        state = 'verse'
                    else:
                        state = 'end'
                elif shard == ',':
                    first_chap = chap
                    second_chap = second_unknown
                    chap = second_unknown
                    state = 'second_verse'
                else:
                    raise BadQuoteException('Bad syntax for quote %s' % (quote))

            elif state == 'second_verse':
                if shard == ';' or shard == '/' or shard == '.':
                    verses.append(((book, first_chap, first_verse),
                                   (book, second_chap, second_verse)))
                    if shard == ';':
                        state = 'chap'
                    elif shard == '.':
                        state = 'verse'
                    else:
                        state = 'end'
                else:
                    raise BadQuoteException('Bad syntax for quote %s' % (quote))

            else:
                raise BadQuoteException('Bad syntax for quote %s' % (quote))

        now_num = not now_num

    # for chap_quote in quote.split(';'):
    #     chap_quote = chap_quote.replace(' ', '')
    #     chap, chap_quote = chap_quote.split(',', 1)
    #     for verse_quote in chap_quote.split('.'):
    #         if '-' not in verse_quote:
    #             verses.append((book, chap, verse))
    #         else:
    #             verse1, verse2 = verse_quote.split('-')
    #             verses.append((book, chap, verse1))
    #             verse1_num = int(str(filter(lambda x: x.isdigit(), verse1)))
    #             verse2_num = int(str(filter(lambda x: x.isdigit(), verse2)))
    #             for verse in xrange(verse1_num+1, verse2_num):
    #                 verses.append((book, chap, verse))
    #             verses.append((book, chap, verse2))

    return verses

def canonicalise_quote(quote):
    """Put a synactically valid quote in a canonical form, removing
    all the spaces, except the one separating the book name from the
    verses specification.

    No attempt to validate the quote is performed. The result is
    undefined for invalid quotes.

    """

    if quote is None:
        return None

    quote = quote.strip().replace(' ', '')

    # Add a space after the first letter-to-digit transition
    for i in xrange(len(quote)-1):
        if quote[i].isalpha() and quote[i+1].isdigit():
            #quote[i:i] = ' '
            quote = '%s %s' % (quote[:i+1], quote[i+1:])
            break

    return quote

def convert_quote_abbreviation(quote, abbr_from, abbr_to):
    """Convert a quote from an abbreviation convention to another. The
    quote must be in canonical form.

    """

    if quote is None:
        return None

    book, verses = quote.split(' ', 1)
    idx = abbr_from.index(book)
    return abbr_to[idx]

def convert_quote_psalm_numbering(quote, to_septuagint):
    """Convert a quote from a Psalm numbering to the other. If the
    quote is not from Psalms, it is returned untouched. It is expected
    that the quote is not too complicated (i.e., a single chapter with
    verses or a chapters interval). If there is a verses specification
    and the quote is mangled, the verses specification is lost.

    If the method is not able to perform the conversion, the untouched
    quoted is silently returned. No exceptions are casted. Thus, this
    method is appropriately used only in contexts in which it is
    possible to fail.

    """
    book, verses = quote.split(' ', 1)
    if book != PSALMS_ABBR:
        return quote

    # Warning: you're entering a wild-guessing and highly heuristic
    # area
    try:
        if ',' in verses:
            num, _ = int(verses.split(',', 1))
            chaps = num, num
        else:
            if '-' in verses:
                chaps = map(int, verses.split('-', 1))
            else:
                num = int(verses)
                chaps = num, num

        if to_septuagint:
            func = masoretic_to_septuagint
        else:
            func = septuagint_to_masoretic

        new_chaps = map(func, chaps)
        new_chaps = new_chaps[0][0], new_chaps[1][1]
        if new_chaps[0] == new_chaps[1]:
            return u"%s %d" % (PSALMS_ABBR, new_chaps[0])
        else:
            return u"%s %d-%d" % (PSALMS_ABBR, new_chaps[0], new_chaps[1])

    except:
        return quote

def quotes_intersect(q1, q2):
    """Return if the two quotes, as returned by decode_quote(), have
    intersection.

    """
    # Less then or equal comparison
    def lte(x1, x2):
        # Check that they are from the same book
        if x1[0] != x2[0]:
            return False
        # Convert to int
        y1 = (int(x1[1]), my_int(x1[2]))
        y2 = (int(x2[1]), my_int(x2[2]))
        # Compare lexicographically
        return y1 <= y2

    for el1 in q1:
        # Check that each quote mentions exactly one book
        assert el1[0][0] == el1[1][0]
        for el2 in q2:
            if el1[0] <= el2[0] <= el1[1] or el2[0] <= el1[0] <= el2[1]:
                return True
    return False

class BibleQuery:

    def __init__(self, db_filename=None):
        from pysqlite2 import dbapi2 as sqlite
        if db_filename is None:
            db_filename = 'bible.sqlite'
        self.conn = sqlite.connect(db_filename)
        self.cur = self.conn.cursor()

    def get_text(self, verses):
        # TODO - This method isn't protected from SQL injection
        # TODO - Add a mechanism to properly handle Psalms numbering
        if verses is None:
            return None

        conds = []

        for first, second in verses:
            assert(first[0] == second[0])
            first_cond = 'capitolo > %s OR (capitolo = %s AND versetto >= %d)' % (first[1], first[1], my_int(first[2]))
            second_cond = 'capitolo < %s OR (capitolo = %s AND versetto <= %d)' % (second[1], second[1], my_int(second[2]))
            cond = "libro = '%s' AND (%s) AND (%s)" % (first[0], first_cond, second_cond)
            conds.append(cond)

        query = 'SELECT testo FROM bibbia WHERE %s ORDER BY indice ASC;' % (' OR '.join(map(lambda x: '(%s)' % x, conds)))

        self.cur.execute(query)
        text = u''
        for row in self.cur:
            text = text + unicode(row[0]) + u' '

        text = text.replace(u'//', u'\n\n')
        text = text.replace(u'/', u'\n\n')
        text = text.replace(u'\u2019', u'\'')

        return text

def test_quote(quote):
    bq = BibleQuery()
    verses = decode_quote(quote)
    print "%30s: %30s --> %r" % (quote, canonicalise_quote(quote), verses)
    #print "  %s" % (bq.get_text(verses))

def test_quote_intersection(q1, q2):
    bq = BibleQuery()
    v1 = decode_quote(q1)
    v2 = decode_quote(q2)
    print "%30s - %30s --> %s" % (q1, q2, quotes_intersect(v1, v2))

if __name__ == '__main__':
    test_quote('1Gv 5,5b-13a')
    test_quote('1 Gv 5,5b-13a')
    test_quote('Lc 3, 15-16 . 21-22')
    test_quote('Mt 4, 12-17, 23   ')
    test_quote('Mt 4, 12-17, 23 ; 18,24.26-29c')
    test_quote('Nm 13,1-3a.25-14,1.26-30.34-35')

    test_quote_intersection("Gv 1,1-10", "Gv 1,1-10")
    test_quote_intersection("Gv 1,1-10", "Gv 1,10-20")
    test_quote_intersection("Gv 1,1-10", "Gv 1,15-20")
    test_quote_intersection("Gv 1,1-10", "Gn 1,15-20")
    test_quote_intersection("Gv 1,1-10.20-30", "Gv 1,15-16")
    test_quote_intersection("Gv 1,1-10.20-30", "Gv 1,15-16.25-26")
    test_quote_intersection("Gv 1,1-10.20-30", "Gv 2,15-16.25-26")
    test_quote_intersection("Gv 1,1-5,10.20-30", "Gv 2,15-16.25-26")
