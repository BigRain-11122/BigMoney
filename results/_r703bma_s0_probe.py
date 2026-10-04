# r703 bm-a S0 probe: loop task status + predecessor liveness triage
# Laws: R49 (schtasks as source of truth), pit-encoding (schtasks output GBK dual-form decode)
import subprocess, sys

def q(args):
    r = subprocess.run(["schtasks"] + args, capture_output=True)
    raw = r.stdout
    for enc in ("gbk", "utf-16"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("gbk", errors="replace")

print("== Bigmoney-IterationLoop ==")
t = q(["/query", "/tn", "Bigmoney-IterationLoop", "/fo", "LIST", "/v"])
for line in t.splitlines():
    s = line.strip()
    if any(k in s for k in ("状态", "Status", "上次运行时间", "Last Run Time", "下次运行时间", "Next Run Time", "任务运行时间", "上次结果", "Last Result", "要运行的任务")):
        print(s)
print("== watchdog ==")
t2 = q(["/query", "/tn", "Bigmoney-LoopWatchdog", "/fo", "LIST", "/v"])
for line in t2.splitlines():
    s = line.strip()
    if any(k in s for k in ("状态", "Status", "上次运行时间", "Last Run Time", "下次运行时间", "Next Run Time", "上次结果", "Last Result")):
        print(s)
