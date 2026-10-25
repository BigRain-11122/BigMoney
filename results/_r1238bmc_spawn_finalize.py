# -*- coding: utf-8 -*-
"""r1238 bm-c: detached (zero-console) launcher for the W328 finalize leg.

Why: the CLI tool cancels a shell command after 5 minutes with no output, and the
finalize leg writes its log only at the end (r1219 law: DETACHED + python -u, an empty
log with a live PID is NORMAL, never restart -- a restart would double-burn the ledger).

Spawns: python -u scripts/perpetual_faces_n1.py finalize --wave 328
flags : DETACHED_PROCESS | CREATE_NO_WINDOW (zero desktop window; O-20261006-2250 law)
writes: results/_r1238bmc_finalize_328.log (+ .pid)
"""
import io
import json
import os
import subprocess
import sys

DETACHED_PROCESS = 0x00000008
CREATE_NO_WINDOW = 0x08000000

log = os.path.abspath('results/_r1238bmc_finalize_328.log')
pidf = os.path.abspath('results/_r1238bmc_finalize_328.pid')
args = [sys.executable, '-u', 'scripts/perpetual_faces_n1.py', 'finalize', '--wave', '328']
env = dict(os.environ, PYTHONIOENCODING='utf-8')
with io.open(log, 'ab') as fh:
    p = subprocess.Popen(args, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW, env=env,
                         cwd=os.path.abspath('.'))
io.open(pidf, 'w', encoding='utf-8').write(str(p.pid))
print(json.dumps({'spawned': True, 'pid': p.pid, 'log': log,
                  'args': args[2:], 'flags': 'DETACHED_PROCESS|CREATE_NO_WINDOW'}, indent=1))