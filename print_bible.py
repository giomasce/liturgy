#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

from quote import BibleQuery, decode_quote, convert_quote_psalm_numbering
from utils import PrependStream

def main():
    bible_query = BibleQuery()
    quote = " ".join(sys.argv[1:])
    converted_quote = convert_quote_psalm_numbering(quote, False)
    text = bible_query.get_text(decode_quote(converted_quote, allow_only_chap=True))
    PrependStream(sys.stdout, '    ').write('"' + text.strip() + '"')
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()
