#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import codecs

class Editor:

    def __init__(self):
        tempfd, self.tempname = tempfile.mkstemp(suffix='.txt')
        self.tempfile = codecs.getwriter('utf-8')(os.fdopen(tempfd, 'w'))

    def edit(self):
        self.tempfile.close()
        os.system("emacs -nw %s" % (self.tempname))
        with codecs.open(self.tempname, encoding='utf-8') as fin:
            self.edited_content = fin.readlines()

        try:
            os.unlink(self.tempname)
        except OSError:
            pass

    def confirmation_request(self, changed=True):
        if not changed:
            sys.stdout.write("Nothing was modified, ignoring...\n")
            return False
        else:
            sys.stdout.write("Confirm changes? [y/N] ")
            answer = sys.stdin.readline().strip()
            if answer != '':
                answer = answer[0]
            if answer == 'y' or answer == 'Y':
                sys.stdout.write("Changes confirmed\n")
                return True
            else:
                sys.stdout.write("Changes rejected\n")
                return False
