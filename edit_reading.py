#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

from database import Session, Reading
from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering
from utils import PrependStream
from editor import Editor

def main():
    reading_id = int(sys.argv[1])
    session = Session()
    bible_query = BibleQuery()
    reading = session.query(Reading).filter(Reading.id == reading_id).one()
    text = reading.text

    editor = Editor()

    # Fix wrong quotation marks
    text = re.sub(ur'"([a-zA-ZàòùèéÒÀÙÈÉ0-9])', ur'“\1', text, count=0)
    text = re.sub(ur'([a-zA-ZàòùèéÒÀÙÈÉ0-9\.?!])"', ur'\1”', text, count=0)

    # From http://stackoverflow.com/questions/15120346/emacs-setting-comment-character-by-file-extension
    PrependStream(editor.tempfile, '# ').write(u'-*- coding: utf-8; comment-start: "#"; -*-\n')
    PrependStream(editor.tempfile, '# ').write(u'Quote: %s\n' % (reading.quote))
    editor.tempfile.write(u'\n')
    editor.tempfile.write(text)
    editor.tempfile.write(u'\n')
    try:
        converted_quote = convert_quote_psalm_numbering(reading.quote, False)
        bible_text = bible_query.get_text(decode_quote(converted_quote, allow_only_chap=True))
    except:
        PrependStream(editor.tempfile, '# ').write(u'Quote: %s\nCould not retrieve bible text\n' % (reading.quote))
        print decode_quote(reading.quote, allow_only_chap=True)
        raise
    else:
        PrependStream(editor.tempfile, '# ').write(u'Quote: %s\nConverted quote: %s\nBible text:\n\n%s' % (reading.quote, converted_quote,  bible_text))

    editor.edit()

    new_text = u''.join(filter(lambda x: not x.startswith(u'#'), editor.edited_content)).strip() + u'\n'

    if editor.confirmation_request(new_text != reading.text):
        reading.text = new_text
        session.commit()
    else:
        session.rollback()

if __name__ == '__main__':
    main()
