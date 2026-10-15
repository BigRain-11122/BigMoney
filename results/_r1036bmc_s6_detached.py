# -*- coding: utf-8 -*-
# r1036 bm-c: detached S6 driver relaunch (shell tool 5-min no-output auto-cancel
# face; legs idempotent so full re-run is safe). Logs to the same log file.
import subprocess
import sys

cmd = [sys.executable, 'Tools/_r1036bmc_s6.py']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     creationflags=subprocess.CREATE_NO_WINDOW)
out = b''
try:
    out = p.communicate(timeout=5)[0] or b''
except subprocess.TimeoutExpired:
    print('STILL-RUNNING pid=%d (expected for full chain; poll the log)' % p.pid)
    raise SystemExit(0)
print(out.decode('utf-8', 'replace'))
