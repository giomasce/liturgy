#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

from database import Session, Reading

def main():
    reading_id = int(sys.argv[1])
    session = Session()
    reading = session.query(Reading).filter(Reading.id == reading_id).one()
    text = reading.text
    sys.stdout.write(text)
    session.rollback()

if __name__ == '__main__':
    main()
