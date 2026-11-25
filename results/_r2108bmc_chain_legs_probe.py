"""r2108 bm-c: read-only probe of the five chain legs added to Tools/s6_chain_bmc.py
but not yet committed (working-tree edit from the peer session at 20:08).

Why this round is probe-only: repo_write_contention.py returned CONTENTION (rc3) --
another host (pid 98008) was writing shared faces one minute before this round began,
so per r1907/r1927 this round lands new files only and re-runs no chain leg that writes.

What it answers, for each new leg: does the script the leg names exist on disk, does its
check mode run, and does a drifting check say STALE (r1934 contract: run_leg only pays a
write when the check text says STALE / face missing; a check that prints drift without
that word is a leg that never repairs itself).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEGS = [
    ("idx_fut_carry_always_on_price", ["scripts/idx_fut_carry_always_on_price.py", "check"]),
    ("idx_fut_carry_roll_step_reversal", ["scripts/idx_fut_carry_roll_step_reversal.py", "--check"]),
    ("idx_fut_carry_capacity_lots", ["scripts/idx_fut_carry_capacity_lots.py", "check"]),
    ("idx_fut_carry_decision_face", ["scripts/idx_fut_carry_decision_face.py", "check"]),
    ("etf_book_defense_spells", ["scripts/etf_book_defense_spells.py", "check"]),
]

TIMEOUT = 90


def probe(name: str, argv: list[str]) -> dict:
    path = os.path.join(HERE, argv[0])
    row = {"leg": name, "script": argv[0], "exists": os.path.exists(path)}
    if not row["exists"]:
        row["verdict"] = "SCRIPT_MISSING"
        return row
    src = open(path, encoding="utf-8", errors="replace").read()
    row["mentions_STALE"] = "STALE" in src
    try:
        p = subprocess.run(
            [sys.executable] + argv,
            cwd=HERE,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
        )
        out = (p.stdout or "").strip().splitlines()
        err = (p.stderr or "").strip().splitlines()
        row["rc"] = p.returncode
        row["last_stdout"] = out[-1][:300] if out else ""
        row["last_stderr"] = err[-1][:300] if err else ""
        blob = "\n".join(out + err)
        row["says_STALE"] = "STALE" in blob
        if p.returncode == 0:
            row["verdict"] = "OK"
        elif p.returncode == 3:
            row["verdict"] = "DRIFT_SAYS_STALE" if row["says_STALE"] else "DRIFT_SILENT_NO_STALE"
        else:
            row["verdict"] = f"RC_{p.returncode}"
    except subprocess.TimeoutExpired:
        row["rc"] = None
        row["verdict"] = f"TIMEOUT_{TIMEOUT}s"
    return row


def main() -> int:
    rows = [probe(n, a) for n, a in LEGS]
    bad = [r for r in rows if r["verdict"] in ("SCRIPT_MISSING", "DRIFT_SILENT_NO_STALE")]
    doc = {
        "schema": "r2108bmc-chain-legs-probe/v1",
        "why": "repo_write_contention rc3 (peer host pid 98008 writing at 23:31:43) -> new files only",
        "premise": "Tools/s6_chain_bmc.py has five uncommitted legs (working-tree, 20:08)",
        "legs": rows,
        "headline": {
            "legs": len(rows),
            "ok": sum(1 for r in rows if r["verdict"] == "OK"),
            "problems": [{"leg": r["leg"], "verdict": r["verdict"]} for r in bad],
        },
    }
    out = os.path.join(HERE, "results", "_r2108bmc_chain_legs_probe.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    for r in rows:
        print(f"{r['verdict']:<20} {r['leg']:<34} {(r.get('last_stdout') or '')[:110]}")
    print(f"headline: {doc['headline']['legs']} legs, {doc['headline']['ok']} ok, "
          f"{len(bad)} problem(s) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
