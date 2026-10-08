# -*- coding: utf-8 -*-
"""r904 bm-a: S7 quartet self-check (loop task pin / watchdog / claws)."""
import io
import subprocess


def sched(name):
    out = subprocess.run(["schtasks", "/query", "/tn", name, "/fo", "csv",
                          "/v"], capture_output=True).stdout
    txt = out.decode("gbk", errors="replace")
    line = [l for l in txt.splitlines() if name in l]
    return line[0] if line else "MISSING"


def norm(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read() \
            .replace("\r\n", "\n")
    except OSError:
        return "MISSING"


print("LOOP:", "present" if "Bigmoney-IterationLoop" in sched(
    "Bigmoney-IterationLoop") else "MISSING")
nxt = sched("Bigmoney-IterationLoop")
for field in nxt.split('","'):
    if "Next Run" in field or "\u4e0b\u6b21\u8fd0\u884c" in field:
        pass
print("WATCHDOG:", "present" if "Bigmoney-LoopWatchdog" in sched(
    "Bigmoney-LoopWatchdog") else "MISSING")
pc = norm(r".git\hooks\pre-commit") == norm(r"Tools\git-hooks\pre-commit")
pp = norm(r".git\hooks\pre-push") == norm(r"Tools\git-hooks\pre-push")
print("PRECOMIT_CLAW_MATCH:", pc)
print("PREPUSH_CLAW_MATCH:", pp)
print("quartet:", "GREEN" if (pc and pp) else "RED")
