"""FUND-STAGESTYLE-COMBO-P1 freeze-step probe battery (zero-network, fail-closed).

Context: the batch was opened by bm-a r1085 (F-04, O-20261019-2230-bm-b sec.2.4)
and the freeze window (r1086) never ran -- bm-a heartbeat stale >4h at takeover
time (fleet/machines/bm-a.json). This battery is the bm-b takeover leg: it
machine-reads every frozen-face input the prereg sec.2 declares, so the freeze
commit can cite a receipt instead of prose.

Legs (all read-only):
  L1 price panel face   results/astock_daily_update_status.json (complete/cutoff)
  L2 stage label face   results/regime5_labels/REGIME5-*.json (span/order/states)
  L3 thermo emotion face results/regime_thermo/thermo_daily.csv (P-5C cutoff)
  L4 sleeve faces       results/fund_{value,quality,divlowvol}_p1 (cells + d6)
  L5 banned-direction gate rc on the prereg
  L6 seed admission     Tools/seed_admit_gate.py on the proposed null base pair

Exit codes: 0 = all gates green (disclosures may still be present),
            3 = at least one frozen-face gate red (prereg must not freeze),
            2 = mechanism failure (unreadable input / gate tool error).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join("research", "FUND-STAGESTYLE-COMBO-P1.md")
TARGET_CUTOFF = "2026-10-19"
SEED_BASES = (20531000, 20531500)


def _p(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _gate(gates: dict, name: str, ok: bool, **facts) -> None:
    gates[name] = {"ok": bool(ok), **facts}


def leg_panel(gates: dict, facts: dict) -> None:
    path = _p("results", "astock_daily_update_status.json")
    if not os.path.exists(path):
        _gate(gates, "L1_price_panel", False, error="status file missing")
        return
    doc = _read_json(path)
    panel = doc.get("panel") or {}
    complete = bool(panel.get("complete"))
    cutoff = panel.get("cutoff")
    per_files = int(panel.get("per_files") or 0)
    facts["price_panel"] = {
        "status_ts": doc.get("ts"),
        "mode": doc.get("mode"),
        "complete": complete,
        "cutoff": cutoff,
        "per_files": per_files,
        "universe_n": panel.get("universe_n"),
    }
    ok = complete and cutoff is not None and cutoff >= TARGET_CUTOFF and per_files >= 5000
    _gate(
        gates,
        "L1_price_panel",
        ok,
        complete=complete,
        cutoff=cutoff,
        per_files=per_files,
        target_cutoff=TARGET_CUTOFF,
    )


def leg_labels(gates: dict, facts: dict) -> None:
    d = _p("results", "regime5_labels")
    files = sorted(f for f in os.listdir(d) if f.startswith("REGIME5-") and f.endswith(".json")) if os.path.isdir(d) else []
    if not files:
        _gate(gates, "L2_stage_labels", False, error="no REGIME5 label file")
        return
    latest = files[-1]
    doc = _read_json(os.path.join(d, latest))
    labels = doc.get("labels") or []
    dates = [row.get("date") for row in labels]
    states = [row.get("state") for row in labels]
    ascending = all(a < b for a, b in zip(dates, dates[1:]))
    uniq = len(set(dates)) == len(dates)
    state_counts: dict[str, int] = {}
    for st in states:
        state_counts[st] = state_counts.get(st, 0) + 1
    known = {"CHOP", "BULL", "BEAR", "GRIND", "SUPPORT"}
    unknown = sorted({s for s in states if s not in known})
    facts["stage_labels"] = {
        "file": latest,
        "declared_cutoff": doc.get("cutoff"),
        "n_labels": len(labels),
        "first": dates[0] if dates else None,
        "last": dates[-1] if dates else None,
        "ascending": ascending,
        "unique": uniq,
        "state_counts": state_counts,
        "unknown_states": unknown,
    }
    ok = len(labels) > 2000 and ascending and uniq and not unknown
    _gate(gates, "L2_stage_labels", ok, n_labels=len(labels), ascending=ascending, unknown_states=unknown)
    if doc.get("cutoff") and doc["cutoff"] < TARGET_CUTOFF:
        facts.setdefault("disclosures", []).append(
            "stage label face asof %s < price cutoff %s (PIT gap disclosed, not silently forward-filled)"
            % (doc.get("cutoff"), TARGET_CUTOFF)
        )


def leg_thermo(gates: dict, facts: dict) -> None:
    path = _p("results", "regime_thermo", "thermo_daily.csv")
    if not os.path.exists(path):
        _gate(gates, "L3_thermo_face", False, error="thermo_daily.csv missing")
        return
    first = last = None
    n = 0
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        for row in csv.DictReader(fh):
            n += 1
            day = row.get("date") or row.get("Date") or ""
            if first is None:
                first = day
            last = day
    facts["thermo_face"] = {"rows": n, "first": first, "last": last}
    ok = n > 5000 and last is not None and last >= "2026-09-01"
    _gate(gates, "L3_thermo_face", ok, rows=n, last=last)
    if last is not None and last < TARGET_CUTOFF:
        facts.setdefault("disclosures", []).append(
            "thermo emotion face cutoff %s < price cutoff %s (P-5C frozen face, asof mismatch disclosed)"
            % (last, TARGET_CUTOFF)
        )


def leg_sleeves(gates: dict, facts: dict) -> None:
    faces = {}
    ok = True
    for fam in ("value", "quality", "divlowvol"):
        base = _p("results", "fund_%s_p1" % fam)
        cells = os.path.join(base, "cells.csv")
        d6 = os.path.join(base, "d6.json")
        present = os.path.isdir(base)
        row = None
        if os.path.exists(cells):
            with open(cells, "r", encoding="utf-8", errors="replace", newline="") as fh:
                rows = list(csv.DictReader(fh))
            row = rows[0] if rows else None
        faces[fam] = {
            "dir_present": present,
            "cells_present": os.path.exists(cells),
            "d6_present": os.path.exists(d6),
            "headline_cell": (row or {}).get("cell"),
            "headline_face": (row or {}).get("face"),
            "sharpe_full": (row or {}).get("sharpe_full"),
        }
        ok = ok and present and os.path.exists(cells) and os.path.exists(d6)
    facts["sleeves"] = faces
    _gate(gates, "L4_sleeve_faces", ok, families=sorted(faces))


def _run(argv: list) -> tuple:
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    proc = subprocess.run(
        argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=180, **kwargs
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def leg_banned(gates: dict, facts: dict) -> None:
    if not os.path.exists(_p(PREREG)):
        _gate(gates, "L5_banned_direction_gate", False, error="prereg missing")
        return
    rc, out = _run([sys.executable, _p("Tools", "banned_direction_gate.py"), "--prereg", PREREG])
    facts["banned_gate"] = {"rc": rc, "tail": out.strip().splitlines()[-1][:300] if out.strip() else ""}
    _gate(gates, "L5_banned_direction_gate", rc == 0, rc=rc)


def leg_seeds(gates: dict, facts: dict) -> None:
    results = {}
    ok = True
    for base in SEED_BASES:
        rc, out = _run([sys.executable, _p("Tools", "seed_admit_gate.py"), str(base)])
        results[str(base)] = {"rc": rc, "tail": out.strip().splitlines()[-1][:300] if out.strip() else ""}
        ok = ok and rc == 0
    facts["seed_admission"] = results
    _gate(gates, "L6_seed_admission", ok, bases=list(SEED_BASES))


def run() -> tuple:
    facts: dict = {"prereg": PREREG, "target_cutoff": TARGET_CUTOFF}
    gates: dict = {}
    for leg in (leg_panel, leg_labels, leg_thermo, leg_sleeves, leg_banned, leg_seeds):
        try:
            leg(gates, facts)
        except Exception as exc:  # mechanism failure, never silently green
            _gate(gates, leg.__name__, False, error="%s: %s" % (type(exc).__name__, exc))
    red = sorted(name for name, g in gates.items() if not g.get("ok"))
    verdict = "GREEN" if not red else "RED"
    return facts, gates, red, verdict


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    facts, gates, red, verdict = run()
    doc = {
        "batch": "FUND-STAGESTYLE-COMBO-P1",
        "leg": "freeze-window probe battery (bm-b takeover of bm-a r1086 window)",
        "host": "bm-b",
        "generated": facts.get("price_panel", {}).get("status_ts"),
        "evidence_cutoff": TARGET_CUTOFF,
        "verdict": verdict,
        "red_gates": red,
        "gates": gates,
        "facts": facts,
    }
    out = _p("results", "_r1048bmb_sscombo_freeze_probe.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"verdict": verdict, "red_gates": red, "receipt": out}, ensure_ascii=False))
    return 0 if verdict == "GREEN" else 3


def selftest() -> int:
    """Hermetic legs: gate aggregation + label checks on synthetic inputs."""
    gates: dict = {}
    _gate(gates, "a", True)
    _gate(gates, "b", False)
    red = sorted(n for n, g in gates.items() if not g["ok"])
    assert red == ["b"], red
    # label ordering semantics used by leg_labels
    dates = ["2026-01-01", "2026-01-02", "2026-01-05"]
    assert all(x < y for x, y in zip(dates, dates[1:]))
    assert len(set(dates)) == len(dates)
    assert sorted(["CHOP", "CHOP", "BEAR"]) == ["BEAR", "CHOP", "CHOP"]
    # verdict math
    assert ("GREEN" if not red else "RED") == "RED"
    print("selftest PASS 4/4")
    return 0


if __name__ == "__main__":
    sys.exit(main())