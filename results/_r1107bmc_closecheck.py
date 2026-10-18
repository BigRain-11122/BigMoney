# -*- coding: utf-8 -*-
# r1107 closeout pre-checks: attrition guard scan (machine hearts + health freshness),
# ORD/DEC tail dual-scan (expect ord 57d1f5de / dec 8706acd8 hold), claw hooks presence.
import io, json, os, hashlib, subprocess, time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)
now = time.time()
print("== attrition guard scan (4 files) ==")
for f in ["fleet/machines/bm-a.json", "fleet/machines/bm-b.json",
          "fleet/machines/bm-c.json", "fleet/machine-health.json"]:
    p = os.path.join(REPO, f)
    age_h = (now - os.path.getmtime(p)) / 3600.0
    d = json.load(io.open(p, encoding="utf-8"))
    if isinstance(d, list):
        hb = None
        ts = (d[-1].get("ts") or d[-1].get("clock_read") or "") if d else ""
        fresh = age_h < 8.0
    else:
        hb = d.get("heartbeat_epoch_utc")
        ts = d.get("clock_read") or d.get("ts") or ""
        fresh = isinstance(hb, int) and (now - hb) < 8 * 3600
    print("  %-32s age=%5.2fh hb=%s clock=%s fresh8h=%s" % (f, age_h, hb, str(ts)[:19], fresh))

print("== ORD/DEC tail dual-scan ==")
def tail_sha(path, n=1):
    t = io.open(path, encoding="utf-8", newline="").read()
    lines = [l for l in t.split("\n") if l.strip()]
    tail = "\n".join(lines[-n:])
    return hashlib.sha256(tail.encode("utf-8")).hexdigest()[:8], lines[-1][:120]
s_ord, ord_line = tail_sha("docs/orders.md")
s_dec, dec_line = tail_sha("docs/decisions.md")
print("  ord tail sha16[:8]=%s  expect 57d1f5de  hold=%s" % (s_ord, s_ord == "57d1f5de"))
print("  ord tail line: %r" % ord_line)
print("  dec tail sha16[:8]=%s  expect 8706acd8  hold=%s" % (s_dec, s_dec == "8706acd8"))
print("  dec tail line: %r" % dec_line)

print("== claw hooks ==")
for h in ["pre-commit", "pre-push"]:
    p = os.path.join(REPO, ".git", "hooks", h)
    if os.path.exists(p):
        b = io.open(p, "rb").read()
        crn = b.replace(b"\r\n", b"\n")
        print("  %-10s present %dB CR-normalized %dB" % (h, len(b), len(crn)))
    else:
        print("  %-10s MISSING" % h)
# canon comparison if claw canon exists
for cand in ["Tools/pre_commit_claw.py", "Tools/pre_push_claw.py", ".git/hooks/pre-commit.canon"]:
    print("  canon candidate %s exists=%s" % (cand, os.path.exists(os.path.join(REPO, cand))))

print("== scheduled tasks (loop/watchdog) ==")
r = subprocess.run(["schtasks", "/Query", "/TN", "Bigmoney-IterationLoop", "/XML"],
                   capture_output=True)
xml = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""
import re as _re
logon = _re.search(r"<LogonType>(\w+)</LogonType>", xml)
state_rc = subprocess.run(["schtasks", "/Query", "/TN", "Bigmoney-IterationLoop"],
                          capture_output=True).stdout.decode("gbk", "replace")
print("  IterationLoop LogonType=%s (S4U=1 law)" % (logon.group(1) if logon else "?"))
for l in state_rc.splitlines():
    if "Bigmoney-IterationLoop" in l or "Running" in l or "就绪" in l or "Ready" in l:
        print("  " + l.strip()[:120])
r2 = subprocess.run(["schtasks", "/Query", "/TN", "Bigmoney-LoopWatchdog", "/XML"],
                    capture_output=True)
xml2 = r2.stdout.decode("utf-8", "replace") if r2.returncode == 0 else ""
logon2 = _re.search(r"<LogonType>(\w+)</LogonType>", xml2)
print("  LoopWatchdog LogonType=%s (S4U=1 law)" % (logon2.group(1) if logon2 else "?"))
print("  LoopWatchdog present=%s" % (r2.returncode == 0))
