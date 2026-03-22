"""Runtime hook to suppress console output in frozen exe."""

import sys
import os

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
