# -*- coding: utf-8 -*-
# r1240 bm-c: detach the W329 finalize (python -u, no console) per r1186/r1219 law.
import subprocess
import sys

DETACHED = 0x00000008
NO_WINDOW = 0x08000000
log = open('results/_r1240bmc_w329_finalize.log', 'wb')
p = subprocess.Popen([sys.executable, '-u', 'scripts/perpetual_faces_n1.py', 'finalize',
                      '--wave', '329'],
                     stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                     creationflags=DETACHED | NO_WINDOW, cwd='.')
print('PID', p.pid)