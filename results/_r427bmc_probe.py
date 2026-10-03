# -*- coding: utf-8 -*-
"""_r427bmc_probe.py -- r427 fact probe (read-only, stdout only).

S0.5 legs: (1) fleet orders dir vs heartbeat ack diff (no ts filter);
(2) D-19 decisions face SHA-256 (group tree origin/main raw-blob bytes, fresh fetch);
(3) group orders.md face SHA-1 (CEO physical-items face);
(4) wave-2 judge-finalize burn poll (PID 31276) + w2_judge.json adoption check;
(5) WM red/lane + bandit next_pick; (6) live mass-trial proc scan (double-burn guard).
"""
import json
import os
import hashlib
import subprocess
import datetime

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
CREATE_NO_WINDOW = 0x08000000
GRP = r"K:\Fluxgroup\FluxGroup"


def sg(args, cwd=None):
    p = subprocess.run(["git"] + args, capture_output=True, encoding="utf-8",
                       errors="replace", creationflags=CREATE_NO_WINDOW, cwd=cwd)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest().upper()


# 1) fleet orders diff (mechanical)
ack = set(json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))["orders_ack"])
dirfiles = set(f for f in os.listdir("fleet/orders") if f.endswith(".md"))
print("ORDERS: dir=%d ack=%d unacked=%s missing_from_dir=%s"
      % (len(dirfiles), len(ack), sorted(dirfiles - ack), sorted(ack - dirfiles)))

# 2) D-19 decisions face (fresh fetch, raw-blob bytes SHA-256)
sg(["fetch", "origin"], cwd=GRP)
rc, blob = sg(["show", "origin/main:docs/decisions.md"], cwd=GRP)
if rc == 0:
    d_sha = sha_bytes(blob.encode("utf-8", "surrogateescape"))
    print("D19_SHA=%s" % d_sha)
    print("D19_MATCH=%s (expect 4167B784...)" % d_sha.startswith("4167B784"))
else:
    print("D19_FETCH_FAIL rc=%d %s" % (rc, blob[:120]))

# 3) group orders.md face SHA-1
rc, blob = sg(["show", "origin/main:docs/orders.md"], cwd=GRP)
if rc == 0:
    o_sha = hashlib.sha1(blob.encode("utf-8", "surrogateescape")).hexdigest().upper()
    print("GORDERS_SHA=%s" % o_sha)
    print("GORDERS_MATCH=%s (expect 68947C17...)" % o_sha.startswith("68947C17"))
else:
    print("GORDERS_FAIL rc=%d" % rc)

# 4) wave-2 judge-finalize burn poll
alive = False
try:
    import psutil
    try:
        pr = psutil.Process(31276)
        alive = (pr.status() != psutil.STATUS_ZOMBIE)
        ct = pr.cpu_times()
        print("BURN pid=31276 alive=%s cpu_sec=%.0f" % (alive, ct.user + ct.system))
    except psutil.NoSuchProcess:
        pass
except ImportError:
    for ln in subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Id 31276 -ErrorAction SilentlyContinue) -ne $null"],
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout.split():
        alive = "True" in ln
    print("BURN alive=%s (ps scan, no psutil)" % alive)
jj = "results/mass_trial/w2_judge.json"
if os.path.exists(jj):
    j = json.load(open(jj, encoding="utf-8"))
    print("W2_JUDGE present complete=%s cells=%s keys=%s"
          % (j.get("complete"), j.get("cells") or j.get("n_cells"), sorted(j.keys())[:16]))
else:
    print("W2_JUDGE absent (burn in flight=%s)" % alive)

# 5) WM red/lane + bandit next_pick
wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("WM: red=%s lane=%s ts=%s" % (wm.get("red"), wm.get("lane"), wm.get("ts")))
print("WM next_pick=%s" % str(wm.get("next_pick") or wm.get("bandit") or {})[:160])

# 6) live mass-trial procs (self-match excluded)
try:
    import psutil
    n = 0
    for pr in psutil.process_iter(["pid", "cmdline", "create_time"]):
        try:
            cmd = " ".join(pr.info["cmdline"] or [])
            if ("mass_trial" in cmd) and ("_r427bmc_probe" not in cmd):
                n += 1
                ct = datetime.datetime.fromtimestamp(pr.info["create_time"]).strftime("%H:%M:%S")
                print("LIVE_PROC pid=%s started=%s %s" % (pr.info["pid"], ct, cmd[:140]))
        except Exception:
            pass
    print("LIVE mass-trial procs=%d" % n)
except ImportError:
    print("LIVE scan skipped")
print("PROBE_DONE")
