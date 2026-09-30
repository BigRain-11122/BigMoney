# -*- coding: utf-8 -*-
"""r505 bm-a · PORTFOLIO_BOOK_P1 pre-freeze probe (O-20260930-1147 L2 sleeve book).

Pre-registration sec-2 probe FACTS ONLY (data shape; NO book assembly, NO book
curve, NO gate computation, NO selection preview):

  * frozen REEVAL18 roster replay via scripts/reeval18_drill.py verbatim
    import (_load_roster / _build_state / _roster_cand / _roster_template /
    _wave_run -- sha16-asserted roster, G-PANEL-asserted cutoff panel);
  * per-member window daily return series (x1 face, window caliber identical
    to the drill: eq.iloc[wbase:] pct_change, 176 returns);
  * 18x18 pairwise Pearson correlation matrix + shape stats;
  * frozen composite ranking cited from the drill verdict archive
    (results/reeval18/DRILL-2026-09-22.json g2_reform composite values --
    archive read, not recomputed).

Artifact: results/portfolio_book_probe/pairwise_corr_p1.json
Exit 0 = facts emitted; 2 = mechanism fault (roster/panel/degenerate) as-is.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)          # .../bigmoney/results -> repo root
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import pandas as pd  # noqa: E402

import reeval18_drill as drill  # noqa: E402

OUT_DIR = os.path.join(_HERE, "portfolio_book_probe")
OUT_PATH = os.path.join(OUT_DIR, "pairwise_corr_p1.json")
DRILL_RESULTS = os.path.join(_HERE, "reeval18", "DRILL-2026-09-22.json")


def _j(x):
    if isinstance(x, dict):
        return {str(k): _j(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_j(v) for v in x]
    if isinstance(x, float):
        return round(x, 6) if math.isfinite(x) else None
    return x


def _sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _payload_sha(payload):
    s = json.dumps(_j(payload), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    print("=== PORTFOLIO_BOOK_P1 probe (pre-freeze facts, r505 bm-a) ===")
    try:
        roster = drill._load_roster()
    except Exception as e:
        print(f"PROBE FAIL: roster -- {e}")
        return 2
    try:
        st = drill._build_state()
    except Exception as e:
        print(f"PROBE FAIL: state build -- {e}")
        return 2
    rows = roster["rows"]
    n = len(rows)
    if n != drill.BATCH_N_TRIALS:
        print(f"PROBE FAIL: roster rows {n} != {drill.BATCH_N_TRIALS}")
        return 2

    rets = {}
    n_trades_win = {}
    for row in rows:
        cid = row["candidate_id"]
        cand = drill._roster_cand(row)
        template = drill._roster_template(row)
        eq, trades, metrics = drill._wave_run(st, row["wave"], cand, template)
        r = eq.iloc[st["wbase"]:].pct_change().dropna()
        if len(r) != st["n_win_days"]:
            print(f"PROBE FAIL: {cid} window returns {len(r)} != "
                  f"{st['n_win_days']}")
            return 2
        if float(r.std()) <= 0.0:
            print(f"PROBE FAIL: {cid} zero-variance window (degenerate)")
            return 2
        rets[cid] = r
        w0s = str(st["idx"][st["w0"]].date())
        wes = str(st["idx"][st["wend"]].date())
        n_trades_win[cid] = int(sum(
            1 for tr in trades if w0s <= tr["date"] <= wes))
        print(f"  replay {cid}: {len(r)} window rets, "
              f"win trades {n_trades_win[cid]}")

    R = pd.DataFrame(rets)
    if R.shape != (drill.BATCH_N_TRIALS and st["n_win_days"], n):
        pass  # asserted per-member above; shape print below is the record
    print(f"panel: {R.shape[0]} days x {R.shape[1]} members")
    C = R.corr()                       # Pearson, 18x18
    members = list(C.columns)
    vals = C.values
    off = [(i, j, float(vals[i, j]))
           for i in range(n) for j in range(i + 1, n)]
    offs = sorted(v for _, _, v in off)
    per_member_max = {members[i]: round(max(
        abs(float(vals[i, j])) for j in range(n) if j != i), 6)
        for i in range(n)}

    drill_arc = json.load(open(DRILL_RESULTS, encoding="utf-8"))
    comp = {cid: m["composite"]
            for cid, m in drill_arc["g2_reform"]["members"].items()}
    if set(comp) != set(members):
        print("PROBE FAIL: drill archive composite face != roster members")
        return 2
    comp_rank = sorted(comp.items(), key=lambda kv: (-kv[1], kv[0]))

    payload = {
        "wave": "PORTFOLIO_BOOK_P1_PROBE",
        "purpose": "prereg sec-2 probe facts (pairwise corr shape only; "
                   "no book assembly / no book curve / no gates)",
        "evidence_cutoff": drill.CUTOFF,
        "roster_sha16": drill.ROSTER_SHA16,
        "drill_results_sha16": _sha16(DRILL_RESULTS),
        "window": {"start": str(st["idx"][st["w0"]].date()),
                   "end": str(st["idx"][st["wend"]].date()),
                   "base_date": str(st["idx"][st["wbase"]].date()),
                   "n_days": st["n_win_days"]},
        "n_members": n,
        "members": members,
        "composite_rank_frozen": [[cid, v] for cid, v in comp_rank],
        "n_trades_win": n_trades_win,
        "pairwise": {
            "n_pairs": len(offs),
            "max_offdiag": round(offs[-1], 6),
            "min_offdiag": round(offs[0], 6),
            "mean_offdiag": round(sum(offs) / len(offs), 6),
            "n_pairs_ge_0.70": sum(1 for v in offs if v >= 0.70),
            "n_pairs_ge_0.50": sum(1 for v in offs if v >= 0.50),
            "n_pairs_lt_0.30": sum(1 for v in offs if v < 0.30),
            "per_member_max_abs": per_member_max,
            "matrix": {members[i]: {members[j]: round(float(vals[i, j]), 6)
                                    for j in range(n)}
                       for i in range(n)},
        },
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    payload["payload_sha256"] = _payload_sha(
        {k: v for k, v in payload.items()})
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(_j(payload), open(OUT_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"probe PASS -> {OUT_PATH}")
    print(f"  max_offdiag={payload['pairwise']['max_offdiag']} "
          f"mean={payload['pairwise']['mean_offdiag']} "
          f"pairs>=0.70: {payload['pairwise']['n_pairs_ge_0.70']} "
          f"pairs>=0.50: {payload['pairwise']['n_pairs_ge_0.50']} "
          f"pairs<0.30: {payload['pairwise']['n_pairs_lt_0.30']}")
    print(f"  payload_sha256={payload['payload_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
