# -*- coding: utf-8 -*-
# r1107 closeout pre-checks part 2: claw hooks + scheduled tasks (quad green).
import io, os, re, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)
print("== claw hooks ==")
for h in ["pre-commit", "pre-push"]:
    p = os.path.join(REPO, ".git", "hooks", h)
    if os.path.exists(p):
        b = io.open(p, "rb").read()
        crn = b.replace(b"\r\n", b"\n")
        print("  %-10s present %dB CR-normalized %dB identical=%s" % (h, len(b), len(crn), len(b) == len(crn)))
    else:
        print("  %-10s MISSING" % h)

print("== scheduled tasks ==")
for task in ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog"]:
    r = subprocess.run(["schtasks", "/Query", "/TN", task, "/XML"], capture_output=True)
    if r.returncode != 0:
        print("  %s QUERY FAIL rc=%d" % (task, r.returncode))
        continue
    xml = r.stdout.decode("utf-8", "replace")
    logon = re.search(r"<LogonType>(\w+)</LogonType>", xml)
    interval = re.search(r"<Interval>([^<]+)</Interval>", xml)
    print("  %s present LogonType=%s interval=%s" % (task, logon.group(1) if logon else "?", interval.group(1) if interval else "?"))
    q = subprocess.run(["schtasks", "/Query", "/TN", task], capture=True).stdout if False else subprocess.run(["schtasks", "/Query", "/TN", task], capture_output=True).stdout
    for l in q.decode("gbk", "replace").splitlines():
        if task in l:
            print("    status line: %r" % l.strip()[:130])
