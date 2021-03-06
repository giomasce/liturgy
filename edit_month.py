#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime
import json
import traceback

from sqlalchemy.orm.session import object_session

from liturgy import get_lit_date, print_lit_date
from database import Session, Reading, from_dict, session_has_pending_commit
from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering
from utils import PrependStream, real_itermonthdays
from editor import Editor

def edit_month(year, month, single_day=None):
    session = Session()
    bible_query = BibleQuery()
    lit_years = {}

    editor = Editor()

    # From http://stackoverflow.com/questions/15120346/emacs-setting-comment-character-by-file-extension
    PrependStream(editor.tempfile, '# ').write(u'-*- coding: utf-8; comment-start: "#"; -*-\n')
    editor.tempfile.write(u'\n')

    def push_day(day):
        date = datetime.date(year, month, day)
        lit_date = get_lit_date(date, lit_years, session)
        events = map(lambda x: x[1], lit_date.competitors)
        print_lit_date(lit_date, PrependStream(editor.tempfile, u'# '), with_id=True)
        editor.tempfile.write(u'\n')
        editor.tempfile.write(json.dumps(map(lambda x: x.as_dict(), events), ensure_ascii=False, indent=2, sort_keys=True) + u'\n')
        editor.tempfile.write(u'---===---\n')
        editor.tempfile.write(u'\n')

    if single_day is not None:
        push_day(single_day)
    else:
        for day in real_itermonthdays(year, month):
            push_day(day)

    editor.edit()

    while True:
        lines = filter(lambda x: not x.startswith(u'#'), editor.edited_content)
        buf = u''

        try:
            for line in lines:
                if line.strip() == u'---===---':
                    data = json.loads(buf)
                    for piece in data:
                        from_dict(piece, session)
                    buf = u''
                else:
                    buf += line
            session.flush()

        except:
            traceback.print_exc()
            sys.stdout.write("Error while parsing new content. Re-edit? [Y/n] ")
            answer = sys.stdin.readline().strip()
            if answer != '':
                answer = answer[0]
            if answer == 'n' or answer == 'N':
                sys.stdout.write("Aborting\n")
                sys.exit(0)
            else:
                sys.stdout.write("Re-editing...\n")
                session.rollback()
                edited_content = editor.edited_content
                editor = Editor()
                editor.tempfile.write("".join(edited_content))
                editor.edit()

        else:
            break

    if editor.confirmation_request(session_has_pending_commit(session)):
        #reading.text = new_text
        session.commit()
    else:
        session.rollback()

if __name__ == '__main__':
    edit_month(*map(int, sys.argv[1:]))
