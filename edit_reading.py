#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import codecs

from database import Session, Reading
from quote import BibleQuery, decode_quote
from utils import PrependStream

def main():
    reading_id = int(sys.argv[1])
    session = Session()
    bible_query = BibleQuery()
    reading = session.query(Reading).filter(Reading.id == reading_id).one()

    temp, tempname = tempfile.mkstemp()
    temp = os.fdopen(temp, 'w')
    temp.write(reading.text.encode('utf-8'))
    try:
        bible_text = bible_query.get_text(decode_quote(reading.quote, allow_only_chap=True))
    except:
        PrependStream(temp, '# ').write('\nQuote: %s\nCould not retrieve bible text\n' % (reading.quote.encode('utf-8')))
        print decode_quote(reading.quote, allow_only_chap=True)
        raise
    else:
        PrependStream(temp, '# ').write('\nQuote: %s\nBible text:\n' % (reading.quote.encode('utf-8')) + bible_text.encode('utf-8'))
    temp.close()

    os.system("emacs -nw %s" % (tempname))
    with codecs.open(tempname, encoding='utf-8') as fin:
        new_text = ''
        for line in fin:
            if not line.startswith('#'):
                new_text += line

    if new_text == reading.text:
        sys.stdout.write("Text wasn't modified, ignoring...\n")
    else:
        sys.stdout.write("Confirm changes? [y/N] ")
        answer = sys.stdin.readline().strip()
        if answer == 'y' or answer == 'Y':
            sys.stdout.write("Changes confirmed\n")
            reading.text = new_text
            session.commit()
        else:
            sys.stdout.write("Changes rejected\n")
            session.rollback()

    try:
        os.unlink(tempname)
    except OSError:
        pass

if __name__ == '__main__':
    main()
