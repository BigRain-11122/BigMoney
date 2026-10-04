# -*- coding: utf-8 -*-
"""r499 bm-c: slim S3 probes -> file (r446 probe-to-file law)."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = []

def say(m):
    OUT.append(str(m))

try:
    wm = json.load(open(ROOT + r"\results\watermark_red.json", encoding="utf-8"))
    say("WATERMARK red=%s verdict=%s" % (wm.get("red"), json.dumps(wm.get("verdict"), ensure_ascii=False)[:400] if isinstance(wm.get("verdict"), dict) else wm.get("verdict")))
    for k in ("next_pick", "ts", "generated_at"):
        if k in wm:
            say("WATERMARK %s=%s" % (k, str(wm[k])[:200]))
except Exception as ex:
    say("WATERMARK READ FAIL: %r" % (ex,))

r = subprocess.run(["python", "Tools/saturation_engine.py", "status"],
                   capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
say("SATENGINE rc=%d" % r.returncode)
txt = r.stdout.decode("utf-8", "replace")
for ln in txt.splitlines():
    if any(k in ln for k in ("verdict", "queue", "burning", "live", "ignited", "engine", "tick", "pid", "RAM", "ram", "state")):
        say("SAT: " + ln.strip()[:200])
if r.returncode != 0:
    say("SAT STDERR: " + r.stderr.decode("utf-8", "replace")[:300])

# W3 judge custody (r487 verify probe, verdict tri-state per r497 fix)
r2 = subprocess.run(["python", "results/_r487bmc_w3_judge_verify.py"],
                    capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
say("W3VERIFY rc=%d" % r2.returncode)
say("W3: " + r2.stdout.decode("utf-8", "replace")[:600])
if r2.returncode != 0:
    say("W3 STDERR: " + r2.stderr.decode("utf-8", "replace")[:300])

with open(ROOT + r"\results\_r499bmc_s3probe.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(OUT) + "\n")
print("DONE lines=%d" % len(OUT))
