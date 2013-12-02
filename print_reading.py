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
    reading = session.query(Reading).filter(Reading.id == reading_id).one()
    text = reading.text
    sys.stdout.write(text)
    session.rollback()

if __name__ == '__main__':
    main()
