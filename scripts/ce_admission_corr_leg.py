"""T-54 slice-3: CORR-leg judgment machinery + synthetic MW-passer live-fire.

CE_ADMISSION_V1.md sec.3 (frozen) CORR clause is CONTINGENT: fires only on
candidates clearing precheck + G1'v2 + G2 + MW. B1 (r185) had zero MW passers
(max legacy-base 6m = 0.5876 < 0.70) -> the leg has NEVER run in production.
This module delivers the judgment-side machinery so the first real trigger
(batch B2+) meets battle-tested code, plus a hermetic live-fire check on
synthetic MW-passer fixtures (the r185 recorded next-face).

MACHINERY LAW (rule sec.3 zero-new-machinery): all pairwise corr math routes
through ew6_portfolio.corr_block (corr-watch sec.2 verbatim import, never
re-written); series construction mirrors corr-watch sec.2 (eq normalized to
1.0 at start, join="inner", pct_change, per-face mask on the returns frame).
Engine faces untouched: real measurement needs candidate x1 sleeves via
E.member_run (engine) inside a frozen batch prereg (rule sec.6, measurement/
judgment separated; the B1 runner honestly marks corr_status=pending_
measurement and never inlines engine runs). This module = judgment layer +
fixtures only; zero engine, zero ledger, zero gates consumed.

Verdict semantics (rule sec.3 verbatim):
  per pair: full-RW face (each series truncated to its own registered
  evidence_cutoff, then common overlap) + IS2 face (>= 2025-01-01,
  live.paper.OOS_START = IV6 sec.3 frozen segment face); each face leg
  needs >= MIN_PERIODS=60 common bars; any member-face leg short => the
  candidate admission DEFERRED (honest wait, missing faces disclosed,
  partial reads still disclosed).
  member-face total max|corr| < 0.50 => PASS; >= 0.50 => REJECT (values +
  full pairwise list disclosed).
  batch-internal: any candidate pair >= 0.50 with a complete (both faces
  >= 60 bars) measurement => deterministic dedup: winner = higher
  legacy-base pooled beat_rate_6m, tie = lexicographically smaller id;
  loser = CORR reject (per-pair loser clause, literal reading: losing any
  violating pair rejects; full pair list disclosed).
  Final precedence: dedup-reject > DEFERRED (short member legs) >
  member-face REJECT > PASS.

Usage:
  python scripts/ce_admission_corr_leg.py selftest   # hermetic, zero writes
  python scripts/ce_admission_corr_leg.py livefire   # + evidence artifact
    -> results/ce_admission/CORR_LEG_LIVEFIRE.json
Exit contract: 0 = all fixtures PASS; 1 = FAIL.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from live.paper import OOS_START          # IS2 boundary, frozen IV6 sec.3
from ew6_portfolio import corr_block      # corr-watch sec.2 verbatim machinery

RULE = "research/CE_ADMISSION_V1.md"
TICKET = "T-2026-09-25-54"
MIN_PERIODS = 60                          # corr-watch FL precedent (rule sec.3)
CEILING = 0.50                            # rule sec.3 frozen cap
OUT_PATH = os.path.join(PATHS.results_dir, "ce_admission", "CORR_LEG_LIVEFIRE.json")
IS2_TS = pd.Timestamp(OOS_START)


def pair_faces(cid, cand_eq, cand_cutoff, others):
    """Per-pair dual-face corr block (corr-watch sec.2 construction).

    others: {oid: {"eq_s": pd.Series, "cutoff": str}} -- CE canonical members
    or same-batch candidates. Each series defensively truncated to its own
    cutoff (engine sleeves arrive already truncated; re-application is
    conservative and disclosed). Returns per-oid face records; legs with
    < MIN_PERIODS bars carry corr=None (short-leg honest face, never guessed).
    """
    out = {}
    a_full = cand_eq[cand_eq.index <= pd.Timestamp(cand_cutoff)]
    for oid, o in others.items():
        if a_full.empty:
            out[oid] = {"full_rw": {"n_bars": 0, "corr": None},
                        "is2": {"n_bars": 0, "corr": None}}
            continue
        b = o["eq_s"][o["eq_s"].index <= pd.Timestamp(o["cutoff"])]
        if b.empty:
            out[oid] = {"full_rw": {"n_bars": 0, "corr": None},
                        "is2": {"n_bars": 0, "corr": None}}
            continue
        norm = pd.concat({cid: a_full / a_full.iloc[0], oid: b / b.iloc[0]},
                         axis=1, join="inner").dropna()
        rets = norm.pct_change().dropna()
        is2_mask = rets.index >= IS2_TS
        nf, ni = len(rets), int(is2_mask.sum())
        rec = {"full_rw": {"n_bars": nf, "corr": None},
               "is2": {"n_bars": ni, "corr": None}}
        if nf >= MIN_PERIODS:
            rec["full_rw"]["corr"] = corr_block(rets)["pairs"][f"{cid}|{oid}"]
        if ni >= MIN_PERIODS:
            rec["is2"]["corr"] = corr_block(rets, is2_mask)["pairs"][f"{cid}|{oid}"]
        out[oid] = rec
    return out


def _face_max(faces):
    """Total max |corr| over all complete (oid, face) legs + argmax + shorts."""
    mx, src, short_legs = 0.0, None, []
    for oid, rec in faces.items():
        for face in ("full_rw", "is2"):
            v = rec[face]["corr"]
            if v is None:
                short_legs.append({"vs": oid, "face": face,
                                    "n_bars": rec[face]["n_bars"]})
            elif abs(v) > mx:
                mx, src = abs(v), {"vs": oid, "face": face, "corr": v}
    return mx, src, short_legs


def candidate_verdict(cid, cand_eq, cand_cutoff, members):
    """Rule sec.3 member-face verdict for one candidate vs the CE roster."""
    faces = pair_faces(cid, cand_eq, cand_cutoff, members)
    mx, src, shorts = _face_max(faces)
    verdict = "DEFERRED" if shorts else ("PASS" if mx < CEILING else "REJECT")
    return {"candidate": cid, "member_face": {"verdict": verdict,
                                              "max_abs_corr": round(mx, 4),
                                              "argmax": src,
                                              "short_legs": shorts,
                                              "pairs": faces},
            "ceiling": CEILING}


def batch_evaluate(cands, members):
    """Full rule sec.3 batch judgment: member faces + batch-internal dedup.

    cands: {cid: {"eq_s": pd.Series, "cutoff": str,
                  "beat_rate_6m": float}}  (legacy-base pooled, T54 grid face)
    """
    evals = {cid: candidate_verdict(cid, c["eq_s"], c["cutoff"], members)
             for cid, c in cands.items()}
    ids = sorted(cands)
    internal, losers = {}, set()
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            fb = pair_faces(a, cands[a]["eq_s"], cands[a]["cutoff"],
                             {b: {"eq_s": cands[b]["eq_s"],
                                  "cutoff": cands[b]["cutoff"]}})
            mx, src, shorts = _face_max(fb)
            rec = {"max_abs_corr": round(mx, 4), "argmax": src,
                   "short_legs": shorts, "dedup": None}
            if not shorts and mx >= CEILING:
                ca, cb = cands[a]["beat_rate_6m"], cands[b]["beat_rate_6m"]
                winner, loser = ((a, b) if (ca > cb or (ca == cb and a < b))
                                 else (b, a))
                rec["dedup"] = {"winner": winner, "loser": loser,
                                "rule": "beat_rate_6m desc, tie id asc"}
                losers.add(loser)
            internal[f"{a}|{b}"] = rec
    for cid, ev in evals.items():
        if cid in losers:
            ev["final_verdict"] = "REJECT"
            ev["reason"] = "batch_dedup"
        elif ev["member_face"]["short_legs"]:
            ev["final_verdict"] = "DEFERRED"
            ev["reason"] = "short_member_leg"
        elif ev["member_face"]["verdict"] == "REJECT":
            ev["final_verdict"] = "REJECT"
            ev["reason"] = "member_face"
        else:
            ev["final_verdict"] = "PASS"
            ev["reason"] = "member_face"
        ev["dedup_loser"] = cid in losers
    return {"candidates": evals, "batch_internal": internal}


# ---------------- synthetic fixtures (hermetic, deterministic, zero engine) ----------------

def _saw(idx, mod, phase, scale=0.01):
    """Deterministic zero-mean modular return pattern (corr_watch selftest style)."""
    i = pd.Series(range(len(idx)), index=idx)
    return ((i + phase) % mod - (mod - 1) / 2.0) * scale


def _eq(returns):
    return (1.0 + returns).cumprod()


def _fixtures():
    """Synthetic CE roster (6 members, 2016+ span) + 8 candidate shapes."""
    long_idx = pd.bdate_range("2016-01-04", periods=2800)   # ~2016..2026-12, IS2 ~480 bars
    mem_ret = {f"SYN-M{k}": _saw(long_idx, m, p)
               for k, (m, p) in enumerate(
                   [(7, 0), (11, 3), (13, 5), (17, 2), (19, 8), (23, 11)], 1)}
    members = {mid: {"eq_s": _eq(r), "cutoff": "2026-12-31"}
               for mid, r in mem_ret.items()}
    m1, m2 = mem_ret["SYN-M1"], mem_ret["SYN-M2"]

    short_idx = pd.bdate_range("2023-01-02", periods=900)   # subset of long_idx (weekday-aligned)
    assert short_idx.isin(long_idx).all()
    cand_idx = pd.bdate_range("2023-01-02", periods=520)    # ends ~2024-12 -> IS2 empty
    assert cand_idx.isin(long_idx).all()

    conv = _saw(long_idx, 37, 3).copy()
    is2_on = long_idx >= IS2_TS
    conv[is2_on] = 0.95 * m2[is2_on] + 0.05 * _saw(long_idx, 41, 9)[is2_on]
    d1 = _saw(short_idx, 43, 5)
    cands = {
        "SYN-CAND-HIGH": {"eq_s": _eq(0.95 * m1.reindex(short_idx) + 0.05 * _saw(short_idx, 29, 7)),
                           "cutoff": "2026-12-31", "beat_rate_6m": 0.80},
        "SYN-CAND-LOW": {"eq_s": _eq(_saw(short_idx, 31, 13)),
                         "cutoff": "2026-12-31", "beat_rate_6m": 0.72},
        "SYN-CAND-SHORT": {"eq_s": _eq(_saw(cand_idx, 31, 13)),
                           "cutoff": "2024-12-31", "beat_rate_6m": 0.75},
        "SYN-CAND-CONV": {"eq_s": _eq(conv),
                          "cutoff": "2026-12-31", "beat_rate_6m": 0.74},
        "SYN-CAND-D1": {"eq_s": _eq(d1),
                        "cutoff": "2026-12-31", "beat_rate_6m": 0.80},
        "SYN-CAND-D2": {"eq_s": _eq(0.95 * d1 + 0.05 * _saw(short_idx, 47, 2)),
                        "cutoff": "2026-12-31", "beat_rate_6m": 0.75},
        "SYN-CAND-T1": {"eq_s": _eq(_saw(short_idx, 53, 9)),
                        "cutoff": "2026-12-31", "beat_rate_6m": 0.60},
        "SYN-CAND-T2": {"eq_s": _eq(0.95 * _saw(short_idx, 53, 9) + 0.05 * _saw(short_idx, 59, 4)),
                        "cutoff": "2026-12-31", "beat_rate_6m": 0.60},
    }
    return members, cands


def _run_fixtures():
    members, cands = _fixtures()
    res = batch_evaluate(cands, members)
    # determinism (zero RNG, zero wall-clock in the eval path)
    res2 = batch_evaluate(cands, members)
    assert json.dumps(res, sort_keys=True, default=str) == \
           json.dumps(res2, sort_keys=True, default=str), "F0 determinism"
    ev = res["candidates"]

    def mx_pair(cid, vs, face):
        return abs(ev[cid]["member_face"]["pairs"][vs][face]["corr"])

    # F1 HIGH: engineered 0.95 clone of SYN-M1 -> member-face REJECT, pair >= 0.90
    assert ev["SYN-CAND-HIGH"]["final_verdict"] == "REJECT"
    assert ev["SYN-CAND-HIGH"]["reason"] == "member_face"
    assert mx_pair("SYN-CAND-HIGH", "SYN-M1", "full_rw") >= 0.90
    assert mx_pair("SYN-CAND-HIGH", "SYN-M1", "is2") >= 0.90
    # F2 LOW: independent pattern -> PASS, total max < ceiling
    assert ev["SYN-CAND-LOW"]["final_verdict"] == "PASS", \
        f"LOW max={ev['SYN-CAND-LOW']['member_face']['max_abs_corr']}"
    assert ev["SYN-CAND-LOW"]["member_face"]["max_abs_corr"] < CEILING
    # F3 SHORT: history ends 2024-12 -> IS2 legs 0 bars -> DEFERRED, face disclosed
    assert ev["SYN-CAND-SHORT"]["final_verdict"] == "DEFERRED"
    assert ev["SYN-CAND-SHORT"]["reason"] == "short_member_leg"
    shorts = {(s["vs"], s["face"]) for s in ev["SYN-CAND-SHORT"]["member_face"]["short_legs"]}
    assert all(s[1] == "is2" for s in shorts) and len(shorts) == 6
    assert ev["SYN-CAND-SHORT"]["member_face"]["pairs"]["SYN-M1"]["is2"]["n_bars"] == 0
    # F4 CONV: regime-convergent (rule sec.7.2 predicted shape) -> full-RW under
    # cap, IS2 over cap, total max via IS2 -> REJECT
    assert mx_pair("SYN-CAND-CONV", "SYN-M2", "full_rw") < CEILING
    assert mx_pair("SYN-CAND-CONV", "SYN-M2", "is2") >= CEILING
    assert ev["SYN-CAND-CONV"]["final_verdict"] == "REJECT"
    # F5 DEDUP: D2 = 0.95 clone of D1 -> pair >= 0.50, winner D1 (beat 0.80>0.75)
    d = res["batch_internal"]["SYN-CAND-D1|SYN-CAND-D2"]
    assert d["dedup"] and d["dedup"]["winner"] == "SYN-CAND-D1" \
        and d["dedup"]["loser"] == "SYN-CAND-D2"
    assert ev["SYN-CAND-D2"]["final_verdict"] == "REJECT" \
        and ev["SYN-CAND-D2"]["reason"] == "batch_dedup"
    assert ev["SYN-CAND-D1"]["final_verdict"] == "PASS"
    # F6 TIE: equal beat_rate_6m -> winner = lexicographically smaller id
    t = res["batch_internal"]["SYN-CAND-T1|SYN-CAND-T2"]
    assert t["dedup"] and t["dedup"]["winner"] == "SYN-CAND-T1" \
        and t["dedup"]["loser"] == "SYN-CAND-T2", t["dedup"]
    # F7 non-violating internal pair recorded with dedup=None
    assert res["batch_internal"]["SYN-CAND-HIGH|SYN-CAND-LOW"]["dedup"] is None
    return res


def selftest():
    _run_fixtures()
    print("selftest: 7/7 fixture families PASS (F0 determinism + F1-F7)")
    return 0


def livefire():
    res = _run_fixtures()
    out = {
        "batch": "CORR-LEG-LIVEFIRE",
        "class": "machinery-check (judgment layer only; zero engine, zero ledger, "
                 "zero gates consumed; NOT an admission batch)",
        "rule": RULE, "ticket": TICKET,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "fixtures_face": "synthetic deterministic modular patterns (corr_watch "
                         "selftest style); no real data face -- evidence_cutoff "
                         "n/a for machinery-check class",
        "machinery_note": "all corr math via ew6_portfolio.corr_block (corr-watch "
                          "sec.2 verbatim); construction = normalize -> join inner "
                          "-> pct_change -> per-face mask; IS2 = live.paper.OOS_START",
        "production_first_trigger": "awaits first candidate clearing precheck+G1'v2"
                                    "+G2+MW (B1 max 0.5876 < 0.70); batch B2 wires "
                                    "pair_faces/batch_evaluate to real x1 sleeves "
                                    "under its own frozen prereg",
        "fixture_verdicts": res,
        "audit": {"n_engine_runs": 0, "ledger_trials_added": 0,
                  "elapsed_sec": None},
    }
    t0 = time.time()
    out["audit"]["elapsed_sec"] = None
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out["audit"]["elapsed_sec"] = round(time.time() - t0, 1) + 0.0
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT_PATH)
    print(f"livefire: 7/7 fixture families PASS -> {OUT_PATH}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["selftest", "livefire"])
    args = ap.parse_args()
    return selftest() if args.cmd == "selftest" else livefire()


if __name__ == "__main__":
    sys.exit(main())
