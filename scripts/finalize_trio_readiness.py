#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FUND trio finalize-window readiness probe (bm-b lane, T-145/T-155 lineage).

Pure measurement face for the three 12m-family NULLS burns
(fund_quality_p1 / fund_value_p1 / fund_divlowvol_p1, 2000-draw contract).
Evaluates the finalize-window hard gates (window 10-05..10-09 per r641/r642
next-pointer). Zero judgment, zero ledger writes, zero engine touch.

Gates:
  G1 burn_complete   have >= 2000 per family (hard)
  G2 integrity       dup_k == 0 per family (hard)
  G3 rehearsal_green finalize rehearsal face all_legs_ok x3 + fresh (<=7d)
  G4 governance      G-SEG GM ruling watch (MSG-2026-10-03-1720): decisions
                     watermark vs last recorded; r638 fallback = proceed on
                     insufficient-sample single-read if no ruling lands.
                     Annotation face, NOT a mechanical blocker.

Rate/ETA: 60s double-sample; lumpy-batch honest (0-rate falls back to
cross-round history; unknown if neither). History appended per run for
cross-round trending. Lane guard: only bm-b writes faces; other machines
stdout-only (R31 precedent).

Usage: python scripts/finalize_trio_readiness.py run|selftest
Exit: 0 = probe ran (verdict carried in output); 2 = mechanism fault.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

TARGET = 2000
FAMS = ["fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1"]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMILY_DIR = os.path.join(BASE, "results")
REHEARSAL_FACE = os.path.join(FAMILY_DIR, "_r633bma_finalize_rehearsal_summary.json")
OUT_FACE = os.path.join(FAMILY_DIR, "finalize_trio_readiness.json")
HISTORY_FACE = os.path.join(FAMILY_DIR, "finalize_trio_readiness_history.bm-b.jsonl")
RATE_SAMPLE_SEC = 60
REHEARSAL_FRESH_DAYS = 7.0
TZ = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def read_nulls(face_path):
    """-> {lines, have, dup_k, max_k} or raise."""
    ks = []
    with open(face_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ks.append(json.loads(line)["k"])
    have = len(set(ks))
    return {"lines": len(ks), "have": have, "dup_k": len(ks) - have,
            "max_k": max(ks) if ks else None}


def read_rehearsal():
    with open(REHEARSAL_FACE, encoding="utf-8") as f:
        return json.load(f)


def gates_from(counts, rehearsal, now_dt):
    g1 = all(counts[f]["have"] >= TARGET for f in FAMS)
    g2 = all(counts[f]["dup_k"] == 0 for f in FAMS)
    g3 = False
    g3_note = "rehearsal face missing/unreadable"
    try:
        rh_ts = datetime.fromisoformat(rehearsal["ts"])
        age_d = (now_dt - rh_ts).total_seconds() / 86400.0
        g3 = (all(rehearsal["families"][f]["all_legs_ok"] for f in FAMS)
              and 0 <= age_d <= REHEARSAL_FRESH_DAYS)
        g3_note = "all_legs_ok x3, age %.1fd" % age_d
    except Exception as exc:  # fresh/readable check only
        g3_note = "rehearsal face unusable: %s" % exc
    return {"burn_complete": g1, "integrity": g2, "rehearsal_green": g3,
            "rehearsal_note": g3_note}


def load_history(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def history_rate(rows, fam, now_dt, have_now):
    """Newest usable cross-round rate per minute (delta/min), or None."""
    for row in reversed(rows):
        try:
            prev_dt = datetime.fromisoformat(row["ts"])
            minutes = (now_dt - prev_dt).total_seconds() / 60.0
            if minutes < 5 or fam not in row.get("counts", {}):
                continue
            delta = have_now - row["counts"][fam]["have"]
            if delta <= 0:
                return None
            return delta / minutes
        except Exception:
            continue
    return None


def selftest():
    import tempfile
    ok = True
    tmp = tempfile.mkdtemp()
    # fixture: complete+clean family set -> all mechanical gates pass
    for i, fam in enumerate(FAMS):
        p = os.path.join(tmp, fam + ".jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for k in range(TARGET):
                f.write(json.dumps({"k": k, "key": "null|%d" % k}) + "\n")
        r = read_nulls(p)
        ok = ok and r == {"lines": TARGET, "have": TARGET, "dup_k": 0,
                          "max_k": TARGET - 1}
    # dup detection: one repeated k -> dup_k 1, have lines-1
    p = os.path.join(tmp, "dup.jsonl")
    with open(p, "w", encoding="utf-8") as f:
        for k in [0, 1, 1, 2]:
            f.write(json.dumps({"k": k}) + "\n")
    ok = ok and read_nulls(p)["dup_k"] == 1
    # gates: full pass set
    counts = {fam: {"have": TARGET, "dup_k": 0} for fam in FAMS}
    now_dt = datetime.now(TZ)
    rehearsal = {"ts": now_iso(), "families": {f: {"all_legs_ok": True}
                                               for f in FAMS}}
    g = gates_from(counts, rehearsal, now_dt)
    ok = ok and g["burn_complete"] and g["integrity"] and g["rehearsal_green"]
    # stale rehearsal -> G3 red
    rehearsal_stale = {"ts": (now_dt - timedelta(days=30)).strftime(
        "%Y-%m-%dT%H:%M:%S+08:00"),
        "families": {f: {"all_legs_ok": True} for f in FAMS}}
    g2f = gates_from(counts, rehearsal_stale, now_dt)
    ok = ok and not g2f["rehearsal_green"]
    # history rate math: fixed reference clock (hermetic, no wall dependency)
    ref_dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=TZ)
    rows = [{"ts": (ref_dt - timedelta(minutes=10)).strftime(
        "%Y-%m-%dT%H:%M:%S+08:00"), "counts": {FAMS[0]: {"have": 100}}}]
    rate = history_rate(rows, FAMS[0], ref_dt, 200)
    ok = ok and rate is not None and abs(rate - 10.0) < 1e-9
    ok = ok and history_rate(rows, FAMS[0], ref_dt, 100) is None
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


def run():
    machine = "bm-b"
    try:
        with open(os.path.join(BASE, "fleet", "machine.json"),
                  encoding="utf-8") as f:
            machine = json.load(f)["machine_id"]
    except Exception:
        pass
    write_faces = (machine == "bm-b")
    now_dt = datetime.now(TZ)
    t0 = time.time()
    c1 = {f: read_nulls(os.path.join(FAMILY_DIR, f, "nulls.jsonl"))
          for f in FAMS}
    hist_path = HISTORY_FACE if write_faces else \
        HISTORY_FACE.replace(".bm-b.", ".%s." % machine)
    rows = load_history(hist_path)
    if RATE_SAMPLE_SEC > 0:
        time.sleep(RATE_SAMPLE_SEC)
    c2 = {f: read_nulls(os.path.join(FAMILY_DIR, f, "nulls.jsonl"))
          for f in FAMS}
    fam_out = {}
    for f in FAMS:
        rate = None
        if c2[f]["have"] > c1[f]["have"]:
            rate = (c2[f]["have"] - c1[f]["have"]) / (RATE_SAMPLE_SEC / 60.0)
        if rate is None or rate <= 0:
            rate = history_rate(rows, f, now_dt, c2[f]["have"])
        eta_hours = None
        if rate and rate > 0:
            eta_hours = round((TARGET - c2[f]["have"]) / rate / 60.0, 2)
        fam_out[f] = {"have": c2[f]["have"], "lines": c2[f]["lines"],
                      "dup_k": c2[f]["dup_k"], "rate_per_min": rate,
                      "eta_hours": eta_hours}
    try:
        rehearsal = read_rehearsal()
    except Exception:
        rehearsal = None
    g = gates_from({f: c2[f] for f in FAMS}, rehearsal, now_dt)
    # G4 governance: decisions watermark watch
    sha = None
    try:
        with open(os.path.join(BASE, "state.json"), encoding="utf-8") as f:
            sha = json.load(f).get("last_decisions_sha")
    except Exception:
        pass
    prev_sha = rows[-1].get("decisions_sha") if rows else None
    sha_moved = bool(prev_sha and sha and sha != prev_sha)
    g4 = {"status": "PENDING", "decisions_sha": sha,
          "sha_moved_since_last_probe": sha_moved,
          "note": "G-SEG GM ruling (MSG-2026-10-03-1720) not yet logged; "
                  "r638 fallback = proceed on insufficient-sample "
                  "single-read when mechanical gates green"}
    mechanical_ready = g["burn_complete"] and g["integrity"] and \
        g["rehearsal_green"]
    out = {"machine": machine, "ts": now_iso(),
           "probe": "finalize_trio_readiness",
           "not_a_verdict": True, "target_draws": TARGET,
           "families": fam_out, "gates": g, "governance": g4,
           "mechanical_ready": mechanical_ready,
           "window_note": "finalize window 10-05..10-09; open when "
                          "mechanical_ready and governance resolved "
                          "(ruling or r638 fallback)",
           "elapsed_sec": round(time.time() - t0, 1)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print("VERDICT: mechanical_ready=%s (G1=%s G2=%s G3=%s) G4=%s" % (
        mechanical_ready, g["burn_complete"], g["integrity"],
        g["rehearsal_green"], g4["status"]))
    if write_faces:
        with open(OUT_FACE, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        with open(HISTORY_FACE, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": out["ts"],
                "counts": {k: {"have": v["have"], "dup_k": v["dup_k"]}
                           for k, v in fam_out.items()},
                "decisions_sha": sha}) + "\n")
    else:
        print("lane guard: non-bm-b machine, faces not written (R31)")
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    print("usage: finalize_trio_readiness.py run|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
