#!/usr/bin/env python3

"""This script compare stdout capture at run of a txt script as well as its
equivalent pyhton script.
"""

__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@email.com"

import sys
import time
import os
from pathlib import Path
import subprocess
import io
import difflib

def execute(filename, command, outfile):
    cmd = command.split(' ') + [ str(filename) ]
    txt = ''
    stdout = open(outfile, "w", 1)
    _environ = os.environ.copy()
    _environ['SMOLDYN_NO_PROMPT'] = '1'
    try:
        subprocess.run(cmd, timeout=2, stdout=stdout, stderr=subprocess.STDOUT, env=_environ)
        time.sleep(0.1)
    except subprocess.TimeoutExpired:
        pass
    stdout.flush()
    stdout.close()

def cleanup(txt):
    return '\n'.join(filter(lambda x: len(x.strip()) > 0, txt.split('\n')))

sourcedir = Path(sys.argv[1])
pyfiles = sourcedir.glob("**/*.py")

for pyfile in pyfiles:
    txtfile = pyfile.with_suffix('.txt')
    if txtfile.exists():
        a, b = '', ''
        execute(pyfile, f"{sys.executable}", '__1')
        with open('__1', 'r') as f:
            a = f.read()
        execute(txtfile, f"{sys.executable} -m smoldyn", '__2')
        with open('__2', 'r') as f:
            b = f.read()
        a, b = cleanup(a), cleanup(b)
        s = difflib.SequenceMatcher(a=a, b=b)
        if s.ratio() < 0.8:
            print(f"{s.ratio()}: {pyfile} is very different than {txtfile}")
            sys.stdout.flush()
