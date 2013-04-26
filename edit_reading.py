#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import codecs

from database import Session, Reading
from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering
from utils import PrependStream

def main():
    reading_id = int(sys.argv[1])
    session = Session()
    bible_query = BibleQuery()
    reading = session.query(Reading).filter(Reading.id == reading_id).one()

    temp, tempname = tempfile.mkstemp(suffix='.txt')
    temp = os.fdopen(temp, 'w')
    # From http://stackoverflow.com/questions/15120346/emacs-setting-comment-character-by-file-extension
    PrependStream(temp, '# ').write('-*- comment-start: "#"; -*-\n')
    temp.write('\n')
    temp.write(reading.text.encode('utf-8'))
    temp.write('\n')
    try:
        converted_quote = convert_quote_psalm_numbering(reading.quote, False)
        bible_text = bible_query.get_text(decode_quote(converted_quote, allow_only_chap=True))
    except:
        PrependStream(temp, '# ').write('Quote: %s\nCould not retrieve bible text\n' % (reading.quote.encode('utf-8')))
        print decode_quote(reading.quote, allow_only_chap=True)
        raise
    else:
        PrependStream(temp, '# ').write('Quote: %s\nConverted quote: %s\nBible text:\n\n' % (reading.quote.encode('utf-8'), converted_quote.encode('utf-8')) + bible_text.encode('utf-8'))
    temp.close()

    os.system("emacs -nw %s" % (tempname))
    with codecs.open(tempname, encoding='utf-8') as fin:
        new_text = ''
        for line in fin:
            if not line.startswith('#'):
                new_text += line
    new_text = new_text.strip() + u'\n'

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
