#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
import json

from sqlalchemy.orm.session import object_session

from liturgy import get_lit_date, print_lit_date
from database import Session, Reading
from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering
from utils import PrependStream, real_itermonthdays
from editor import Editor

def edit_month(year, month):
    session = Session()
    bible_query = BibleQuery()
    lit_years = {}

    editor = Editor()

    # From http://stackoverflow.com/questions/15120346/emacs-setting-comment-character-by-file-extension
    PrependStream(editor.tempfile, '# ').write(u'-*- comment-start: "#"; -*-\n')
    editor.tempfile.write(u'\n')

    for day in real_itermonthdays(year, month):
        date = datetime.date(year, month, day)
        lit_date = get_lit_date(date, lit_years, session)
        event = lit_date.get_winner()[1]
        print_lit_date(lit_date, PrependStream(editor.tempfile, u'# '), with_id=True)
        editor.tempfile.write(u'\n')
        editor.tempfile.write(json.dumps(event.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + u'\n')
        editor.tempfile.write(u'\n')

    editor.edit()

    #new_text = u''.join(filter(lambda x: not x.startswith(u'#'), editor.edited_content)).strip() + u'\n'

    if editor.confirmation_request():
        #reading.text = new_text
        session.commit()
    else:
        session.rollback()

if __name__ == '__main__':
    year, month = map(int, sys.argv[1:])
    edit_month(year, month)
