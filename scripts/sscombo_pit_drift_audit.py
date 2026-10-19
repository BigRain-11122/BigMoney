"""FUND-STAGESTYLE-COMBO-P1 PIT restatement-drift audit (freeze leg, zero-network).

Prereg sec.2a PIT safety law: the stage-label face a batch consumes must be
reproducible from data that existed at the label's own date. The audit is
"asof snapshot vs current re-derivation": the stored REGIME5 snapshot taken at
its own cutoff is compared against a snapshot re-derived on today's panel over
their shared date range. Any label flip is restatement drift -- a PIT hazard
that must be disclosed (or the freeze refused) rather than silently consumed.

Usage:
    python scripts/sscombo_pit_drift_audit.py run [--asof F] [--fresh F]
    python scripts/sscombo_pit_drift_audit.py selftest

Exit codes:
  0 = no drift over the shared window (freeze may cite this receipt)
  3 = drift found (freeze must not proceed undiscussed; receipt carries rows)
  2 = mechanism fault (unreadable input / shape violation), reported verbatim
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL_DIR = os.path.join(ROOT, "results", "regime5_labels")
DEFAULT_ASOF = os.path.join(LABEL_DIR, "REGIME5-2026-09-30.json")
DEFAULT_FRESH = os.path.join(LABEL_DIR, "REGIME5-2026-10-19.json")
RECEIPT = os.path.join(ROOT, "results", "_r1049bmb_sscombo_pit_drift.json")

STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")


def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    labels = doc.get("labels")
    if not isinstance(labels, list) or not labels:
        raise ValueError(f"{path}: labels empty or wrong type")
    out = {}
    prev = ""
    for row in labels:
        d = row.get("date")
        s = row.get("state")
        if not isinstance(d, str) or not isinstance(s, str):
            raise ValueError(f"{path}: malformed label row {row!r}")
        if s not in STATES:
            raise ValueError(f"{path}: unknown state {s!r} on {d}")
        if prev and d <= prev:
            raise ValueError(f"{path}: label dates not strictly ascending at {d}")
        prev = d
        out[d] = s
    return {"cutoff": doc.get("cutoff"), "labels": out, "path": path}


def audit(asof_path: str, fresh_path: str) -> dict:
    a = _load(asof_path)
    b = _load(fresh_path)
    shared = sorted(set(a["labels"]) & set(b["labels"]))
    if not shared:
        raise ValueError("no shared dates between asof and fresh label faces")
    flips = [d for d in shared if a["labels"][d] != b["labels"][d]]
    transitions: dict[str, int] = {}
    for d in flips:
        key = f"{a['labels'][d]}->{b['labels'][d]}"
        transitions[key] = transitions.get(key, 0) + 1
    return {
        "asof_file": os.path.basename(aof := asof_path),
        "asof_cutoff": a["cutoff"],
        "fresh_file": os.path.basename(fresh_path),
        "fresh_cutoff": b["cutoff"],
        "shared_days": len(shared),
        "shared_first": shared[0],
        "shared_last": shared[-1],
        "flips": len(flips),
        "flip_rate": round(len(flips) / len(shared), 6),
        "first_flips": flips[:20],
        "transitions": transitions,
        "fresh_only_days": max(0, len(b["labels"]) - len(shared)),
        "asof_only_days": max(0, len(a["labels"]) - len(shared)),
        "verdict": "NO_DRIFT" if not flips else "DRIFT",
    }


def run(asof_path: str, fresh_path: str) -> int:
    try:
        rep = audit(asof_path, fresh_path)
    except Exception as exc:  # noqa: BLE001 - mechanism fault reported verbatim
        print(f"sscombo_pit_drift rc2 mechanism-fault: {exc}")
        return 2
    rep["batch"] = "FUND-STAGESTYLE-COMBO-P1"
    rep["leg"] = "PIT restatement drift audit (asof snapshot vs current re-derivation)"
    rep["host"] = "bm-b"
    rep["round"] = "r1049"
    rep["law_ref"] = "research/FUND-STAGESTYLE-COMBO-P1.md sec.2a PIT safety law"
    os.makedirs(os.path.dirname(RECEIPT), exist_ok=True)
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    print(
        "sscombo_pit_drift verdict={v} shared={s} ({f}..{l}) flips={n} rate={r}"
        .format(v=rep["verdict"], s=rep["shared_days"], f=rep["shared_first"],
                l=rep["shared_last"], n=rep["flips"], r=rep["flip_rate"])
    )
    print(f"receipt={RECEIPT}")
    return 0 if rep["flips"] == 0 else 3


def selftest() -> int:
    import tempfile

    tmp = tempfile.mkdtemp(prefix="sscombo_pit_")
    a = os.path.join(tmp, "a.json")
    b = os.path.join(tmp, "b.json")
    c = os.path.join(tmp, "c.json")
    rows = [{"date": f"2020-01-0{i}", "state": "CHOP"} for i in range(1, 4)]
    with open(a, "w", encoding="utf-8") as fh:
        json.dump({"cutoff": "2020-01-03", "labels": rows}, fh)
    grown = rows + [{"date": "2020-01-04", "state": "BULL"}]
    with open(b, "w", encoding="utf-8") as fh:
        json.dump({"cutoff": "2020-01-04", "labels": grown}, fh)
    flipped = [dict(r) for r in rows]
    flipped[2]["state"] = "BEAR"
    with open(c, "w", encoding="utf-8") as fh:
        json.dump({"cutoff": "2020-01-03", "labels": flipped}, fh)

    legs = []
    r1 = audit(a, b)
    legs.append(("append-only growth = NO_DRIFT", r1["verdict"] == "NO_DRIFT" and r1["flips"] == 0))
    legs.append(("fresh_only_days counted", r1["fresh_only_days"] == 1))
    r2 = audit(a, c)
    legs.append(("single flip = DRIFT", r2["verdict"] == "DRIFT" and r2["flips"] == 1))
    legs.append(("transition keyed", r2["transitions"] == {"CHOP->BEAR": 1}))
    bad = os.path.join(tmp, "bad.json")
    with open(bad, "w", encoding="utf-8") as fh:
        json.dump({"labels": [{"date": "2020-01-02", "state": "CHOP"},
                              {"date": "2020-01-01", "state": "CHOP"}]}, fh)
    try:
        audit(a, bad)
        legs.append(("non-ascending rejected", False))
    except ValueError:
        legs.append(("non-ascending rejected", True))
    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print(f"[{'PASS' if v else 'FAIL'}] {name}")
    print(f"sscombo_pit_drift selftest: {ok}/{len(legs)}")
    return 0 if ok == len(legs) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="SS-COMBO PIT restatement drift audit")
    ap.add_argument("mode", choices=("run", "selftest"))
    ap.add_argument("--asof", default=DEFAULT_ASOF)
    ap.add_argument("--fresh", default=DEFAULT_FRESH)
    args = ap.parse_args()
    if args.mode == "selftest":
        return selftest()
    return run(args.asof, args.fresh)


if __name__ == "__main__":
    sys.exit(main())