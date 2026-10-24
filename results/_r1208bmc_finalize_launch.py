# -*- coding: utf-8 -*-
"""r1208 bm-c: launch the W314 finalize headless (python -u, logged) and return.
DETACHED_PROCESS + CREATE_NO_WINDOW: zero console flash (U060 zero-window law)."""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, 'results', '_r1208bmc_finalize.log')
out = open(LOG, 'wb')
DETACHED = 0x00000008
NO_WINDOW = 0x08000000
p = subprocess.Popen([sys.executable, '-u', 'scripts/perpetual_faces_n1.py',
                      'finalize', '--wave', '314'],
                     cwd=REPO, stdout=out, stderr=subprocess.STDOUT,
                     creationflags=DETACHED | NO_WINDOW, close_fds=True)
print('spawned pid', p.pid, '->', LOG)