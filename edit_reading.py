#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile

from database import Session, Reading

def main():
    reading_id = int(sys.argv[1])
    session = Session()
    reading = session.query(Reading).filter(Reading.id == reading_id).one()

    temp, tempname = tempfile.mkstemp()
    temp = os.fdopen(temp, 'w')
    temp.write(reading.text.encode('utf-8'))
    temp.close()

    os.system("emacs -nw %s" % (tempname))
    with open(tempname) as fin:
        new_text = fin.read().decode('utf-8')
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
