# -*- coding: utf-8 -*-
"""r767 bm-c S1 facts probe: smoke test summary + orphan face probe + SAT
engine liveness + idle verdict + FleetLink listener health + intraday marks
lane row count + post_review open-row verdict counts. Compact JSON ->
results/_r767bmc_s1_facts.json. Pattern credit: r766 round S1 legs (smoke
49/49 + SAT rc0 + orphan probe + idle NOT-GREEN --worked + FleetLink 200 +
marks lane + post_review 45Y/0N/5W) as documented in
logs/iteration-loop/round_reports-bm-c.md r766 line."""
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PY = sys.executable
CNW = 0x08000000  # CREATE_NO_WINDOW defense-in-depth
facts = {"round": 767, "now": datetime.datetime.now().astimezone().isoformat(
    timespec="seconds")}
facts["python"] = sys.version.split()[0]
facts["python_exe"] = sys.executable


def run(args):
    p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


# S1 smoke test
rc, out, err = run(["-m", "smoke_test"])
m = re.search(r"Summary:\s*(\d+)/(\d+) PASS, (\d+) FAIL", out)
facts["smoke"] = {"rc": rc,
                  "summary": (m.group(0) if m else out.strip().splitlines()[-1]),
                  "pass": int(m.group(1)) if m else -1,
                  "total": int(m.group(2)) if m else -1,
                  "fail": int(m.group(3)) if m else -1}

# round-zero orphan face probe (read-only canon)
rc, out, err = run(["Tools/orphan_face_probe.py"])
try:
    facts["orphan"] = json.loads(out.strip().splitlines()[-1])
except Exception:
    facts["orphan"] = {"parse_error": out[-300:], "rc": rc}

# SAT engine liveness (bm-c instance face)
rc, out, err = run(["Tools/saturation_engine.py", "status"])
facts["sat"] = {"rc": rc, "alive": rc == 0, "head": out[:180]}

# idle trigger verdict (loop-round bookkeeping face)
ip = os.path.join(ROOT, "results", "idle_trigger.bm-c.json")
try:
    it = json.load(open(ip, encoding="utf-8"))
    facts["idle"] = {k: it.get(k) for k in
                     ("green_idle", "ram_free_pct", "vram_free_gb",
                      "idle_rounds", "agenda_starved", "two_read_red")}
    facts["idle"]["ts"] = it.get("ts")
except Exception as e:
    facts["idle"] = {"error": str(e)}

# FleetLink standing self-cert (listener health endpoint)
try:
    with urllib.request.urlopen("http://127.0.0.1:8790/health", timeout=5) as r:
        body = r.read().decode("utf-8", "replace")[:120]
        facts["fleetlink"] = {"code": r.status, "body": body}
except Exception as e:
    facts["fleetlink"] = {"error": str(e)[:200]}

# intraday marks lane (bm-a host lane, watch-only)
mp = os.path.join(ROOT, "results", "paper", "marks", "marks-20261008.jsonl")
if os.path.exists(mp):
    lines = open(mp, encoding="utf-8").read().splitlines()
    rows = [ln for ln in lines if ln.strip()]
    tail_ts = ""
    for ln in reversed(rows):
        try:
            tail_ts = json.loads(ln).get("ts", "")
            if tail_ts:
                break
        except Exception:
            continue
    facts["marks"] = {"rows": len(rows), "tail_ts": tail_ts,
                      "mtime": datetime.datetime.fromtimestamp(
                          os.path.getmtime(mp)).astimezone().isoformat(
                          timespec="seconds")}
else:
    facts["marks"] = {"rows": 0, "missing": True}

# post_review ledger: LATEST row per claim id (append-per-check ledger:
# every claim is re-reviewed every round -- counting raw rows would
# multiply-count historical verdicts; r765 canon = 45Y/0N/5W per-claim)
pp = os.path.join(ROOT, "results", "post_review.jsonl")
latest = {}
try:
    with open(pp, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except Exception:
                continue
            rid = row.get("id", "?")
            rts = row.get("ts", "")
            if rid not in latest or rts > latest[rid].get("ts", ""):
                latest[rid] = row
except Exception as e:
    facts["post_review_error"] = str(e)
counts = {"YES": 0, "NO": 0, "WAIT": 0, "IDLE": 0}
no_ids = []
for rid, row in latest.items():
    v = row.get("verdict", "IDLE")
    if v not in counts:
        v = "IDLE"
    counts[v] += 1
    if v == "NO":
        no_ids.append(rid)
facts["post_review"] = {"claims": len(latest), "yes": counts["YES"],
                        "no": counts["NO"], "wait": counts["WAIT"],
                        "idle": counts["IDLE"], "no_ids": no_ids[:5]}

out = os.path.join(ROOT, "results", "_r767bmc_s1_facts.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print(json.dumps(facts, indent=1, ensure_ascii=False))
