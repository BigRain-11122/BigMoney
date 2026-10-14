# -*- coding: utf-8 -*-
# _r997bmc_ignite_wave15.py -- detached ignite via Popen (PS Start-Process quoting-pit workaround)
import os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SCRIPT = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc_v3_wave15_r997.py"
BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
out = open(os.path.join(BMC, "wave15_r997.out.log"), "ab")
err = open(os.path.join(BMC, "wave15_r997.err.log"), "ab")
p = subprocess.Popen([sys.executable, SCRIPT], stdout=out, stderr=err,
                      cwd=BMC, creationflags=0x08000000)
print("IGNITED PID", p.pid)
