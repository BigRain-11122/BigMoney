# -*- coding: utf-8 -*-
"""r1208 bm-c: launch the S6 39-leg chain headless (python -u, logged)."""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, 'results', '_r1208bmc_s6_chain.log')
DETACHED = 0x00000008
NO_WINDOW = 0x08000000
out = open(LOG, 'wb')
p = subprocess.Popen([sys.executable, '-u', 'results/_r1208bmc_s6_chain.py'],
                     cwd=REPO, stdout=out, stderr=subprocess.STDOUT,
                     creationflags=DETACHED | NO_WINDOW, close_fds=True)
print('spawned pid', p.pid, '->', LOG)