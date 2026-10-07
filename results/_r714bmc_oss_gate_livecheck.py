# -*- coding: utf-8 -*-
# r714 bm-c live dry-check driver: run the OSS import gate (real carriers, zero
# overrides, zero pool write) against the three adaptation candidates currently
# queued in OSS_HARVEST_LEDGER sec-4 (G3 uptime-kuma > G2 healthchecks > B2
# easytrader). At the current scanning stage every leg that depends on
# adaptation completion must honestly REJECT -- proving the door holds
# premature enrollment while the real pool/attrition carriers are exercised.
import json, os, subprocess, sys, tempfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "Tools", "oss_import_gate.py")
OUT = os.path.join(ROOT, "results", "_r714bmc_oss_import_gate_livecheck.json")

CANDIDATES = [
    ("G3-uptime-kuma", "github.com/louislam/uptime-kuma", "MIT",
     "fleet liveness dashboard adaptation candidate (sec-4 first pick)"),
    ("G2-healthchecks", "github.com/healthchecks/healthchecks", "BSD-3",
     "dead-man cron sentinel adaptation candidate (sec-4 second pick)"),
    ("B2-easytrader", "github.com/shidenggui/easytrader", "MIT",
     "broker-client automation / paper->live bridge candidate (sec-4 third pick)"),
]

def main():
    rows, all_held = [], True
    with tempfile.TemporaryDirectory() as td:
        for name, source, permit, why in CANDIDATES:
            cand = {"id": "OSS-" + name.upper().replace("-", "-"), "ticket_ref": "dry-check (no ticket)",
                    "prereg_ref": "research/OSS_ABSENT_DRYCHECK.md FROZEN (dry-check placeholder)",
                    "runner": "scripts/oss_eng_scan.py", "lane_owner": "bm-c",
                    "priority": 1, "status": "ready", "entered_at": "2026-10-08 01:5x",
                    "source": source, "permit": permit, "adapt_status": "scanning",
                    "shards": [{"key": name + "-0of1", "status": "ready"}]}
            p = os.path.join(td, name + ".json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(cand, fh)
            r = subprocess.run([sys.executable, GATE, "--candidate", p],
                               capture_output=True, timeout=120)
            try:
                v = json.loads(r.stdout.decode("utf-8", errors="replace"))
            except Exception:
                v = {"decision": "UNPARSEABLE", "reason": r.stdout[-300:]}
            held = r.returncode == 1 and v.get("decision") == "REJECT"
            all_held &= held
            rows.append({"candidate": name, "why": why, "rc": r.returncode,
                         "decision": v.get("decision"), "held_at_scanning": held,
                         "red_legs": sorted(l["leg"] for l in v.get("legs", []) if not l["ok"])})
    out = {"ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
           "round": "r714 bm-c", "order": "O-20261007-2245 bm-c lane (enrollment-door leg)",
           "face": "live dry-check, real pool/attrition carriers, ZERO pool write",
           "expectation": "all three REJECT at scanning stage (door holds premature enrollment)",
           "all_held": all_held, "rows": rows}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for r in rows:
        print("%s rc=%d %s held=%s red=%s" % (r["candidate"], r["rc"], r["decision"],
                                              r["held_at_scanning"], r["red_legs"]))
    print("ALL-HELD" if all_held else "LEAK", OUT)
    return 0 if all_held else 1

if __name__ == "__main__":
    sys.exit(main())
