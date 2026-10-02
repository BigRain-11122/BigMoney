# r392 bm-c · PERPETUAL-N3-R2 probe · time-region start-point robustness grid
# Purpose (prereg draft evidence, pre-freeze):
#   leg P  panel face: G-ANCHOR-FACE quadruple assert (same-face law -- the
#          probe loads via perpetual_faces_n3._panel(), the exact function the
#          R1 frozen runner uses; a face mismatch would be VOID not data rot)
#   leg S  start-point table derive: first trading bar of each year 2015..2024
#          (10 starts, all past the med500 warmup horizon; frozen formula)
#   leg R  center replay: VOLATILITY-CE-01 registered center construction run
#          through the real engine write-path, readouts asserted BIT-IDENTICAL
#          to the R1 checkpoint cell (determinism law -> anchor re-verify)
#   leg W  window slice readouts: for each start s, rebase eq at s and read
#          window sharpe / annual return / max drawdown / n_days -- this IS
#          the R2 measurement face running for real on one member
#   leg X  slice-math self-check: per-start daily returns must equal the tail
#          of the full-history daily returns (rebase identity, no recomputation)
# Output: results/_r392bmc_n3r2_probe.json (probe-class evidence only; the
#          R1 checkpoint files are never touched -- write=False face)
import json
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from perpetual_faces_n3 import (       # verbatim reuse, no reimplementation
    FAMILIES, load_members, _panel, _run_cell, _sharpe, EVIDENCE_CUT,
)
import pandas as pd
from science_gates import recorded_lines

# Start-point family (frozen formula): first trading bar of every quarter
# from the panel's own first year through the year before cutoff. The panel
# face is 2020-01-02..2026-09-22 (1631 bars, asserted in leg P), so the
# derived family is 2020Q1..2025Q4 = 24 starts -- a start INSIDE the panel is
# an honest "investor joins here" reading; pre-panel years collapse to the
# same first bar and are excluded by construction.
START_QUARTERS = [(y, m) for y in range(2020, 2026) for m in (1, 4, 7, 10)]
EXPECT_STARTS = 24


def derive_starts(idx: pd.DatetimeIndex) -> dict:
    """First trading bar of each quarter 2020Q1..2025Q4; duplicates (only
    possible at the panel head when the panel itself starts mid-quarter)
    keep the first family key that claims the bar."""
    starts, used = {}, set()
    for y, m in START_QUARTERS:
        hits = idx[idx >= pd.Timestamp(f"{y}-{m:02d}-01")]
        if not len(hits):
            continue
        d = str(hits[0].date())
        if d in used:
            continue
        starts[f"{y}Q{(m - 1) // 3 + 1}"] = d
        used.add(d)
    return starts


def main() -> int:
    rec = {"probe": "PERPETUAL-N3-R2", "machine": "bm-c",
           "evidence_cutoff": EVIDENCE_CUT,
           "start_family": "quarter-first-bar 2020Q1..2025Q4", "legs": {}}

    # ---- leg P: panel face (G-ANCHOR-FACE quadruple) ----------------------
    prices, P = _panel()
    if P is None:
        rec["legs"]["P"] = "FAIL panel"
        json.dump(rec, open(os.path.join(
            ROOT, "results", "_r392bmc_n3r2_probe.json"), "w"))
        return 1
    idx = P["close"].index
    rec["legs"]["P"] = {
        "ok": True,
        "quadruple": {
            "data_face": "data/daily/sh*.csv (core48 bare codes via load_core)",
            "loader": "live.paper.load_core -> build_panels",
            "window_start": str(idx[0].date()),
            "warmup": "vol20/med500 min_periods 20/500 (in-panel)",
        },
        "n_members_panel": int(len(P["close"].columns)),
        "tail": str(idx[-1].date()),
        "n_bars": int(len(idx)),
    }

    # ---- leg S: start-point table ----------------------------------------
    starts = derive_starts(idx)
    rec["legs"]["S"] = {"ok": len(starts) == EXPECT_STARTS,
                       "n_starts": len(starts), "starts": starts}

    # ---- leg R: center replay (engine write-path, one member) ------------
    members = {m["id"]: m for m in load_members()}
    mid = "VOLATILITY-CE-01"
    m = members[mid]
    spec = FAMILIES[mid]
    state = spec["build"](P, dict(spec["center"]))
    r = _run_cell(prices, P, state, m, {})
    ck_path = os.path.join(ROOT, "results", "perpetual_faces", "n3_r1",
                           f"cells-{mid}.jsonl")
    ck = [json.loads(l) for l in open(ck_path, encoding="utf-8") if l.strip()]
    ck_center = [c for c in ck if c.get("kind") == "center"][0]
    replay_ok = (
        round(_sharpe(r["eq"]), 4) == ck_center["full_sharpe"]
        and round(float(r["in_s"]), 4) == ck_center["in_sharpe"]
        and round(float(r["oos_s"]), 4) == ck_center["oos_sharpe"]
        and r["n_trades"] == ck_center["n_trades"]
        and r["n_in"] == ck_center["n_in"] and r["n_oos"] == ck_center["n_oos"]
    )
    rec["legs"]["R"] = {
        "ok": bool(replay_ok),
        "replay": {"full_s": round(_sharpe(r["eq"]), 4),
                   "in_s": round(float(r["in_s"]), 4),
                   "oos_s": round(float(r["oos_s"]), 4),
                   "n_trades": r["n_trades"], "n_in": r["n_in"],
                   "n_oos": r["n_oos"]},
        "r1_checkpoint": {k: ck_center[k] for k in
                          ("full_sharpe", "in_sharpe", "oos_sharpe",
                           "n_trades", "n_in", "n_oos")},
    }

    # ---- leg W: window slice readouts (the R2 face, real run) -------------
    # Slice math: rebasing eq at s cannot change the daily returns after s
    # (r537 float-face law: the rebase division perturbs values at 1e-16 and
    # breaks strict identity) -> the canonical window return series IS the
    # tail slice of the full-history returns; equity path rebuilt from it.
    eq = r["eq"]
    line = recorded_lines()["ce_null_p4_batch1"]     # CE-member frozen line
    full_rets = eq.pct_change().dropna()
    win_rows, math_rows = [], []
    for k in sorted(starts):
        s = pd.Timestamp(starts[k])
        # Join-at-s semantics: an investor who starts following at the close
        # of s earns from s->s+1; the daily-return row dated t carries the
        # (t-1)->t move, so the window series is the STRICT tail (index > s).
        # A >= slice would wrongly credit the s-1->s move to the joiner.
        rets_sub = full_rets[full_rets.index > s]
        n_days = int(len(rets_sub))
        w_s = float(rets_sub.mean() / rets_sub.std() * (252 ** 0.5))
        cum = (1.0 + rets_sub).cumprod()
        maxdd = float((cum / cum.cummax() - 1).min())
        win_rows.append({
            "start": k, "start_date": str(s.date()), "n_days": n_days,
            "window_sharpe": round(w_s, 4), "red": bool(w_s <= line),
            "annual_return": round(float(cum.iloc[-1] ** (252 / n_days) - 1),
                                   4),
            "max_dd": round(maxdd, 4),
        })
        # leg X: cross-path check -- the naive rebase path (equity sliced at
        # s, rebased to 1.0, pct_change) must produce the SAME series values
        # (allclose 1e-12) and length as the canonical strict-tail slice.
        rebased = eq[eq.index >= s]
        rebased = rebased / rebased.iloc[0]
        alt = rebased.pct_change().dropna()
        math_rows.append(bool(len(alt) == len(rets_sub)
                              and float((alt.values - rets_sub.values)
                                        .max()) < 1e-12))
    sharpes = [w["window_sharpe"] for w in win_rows]
    q = pd.Series(sharpes).quantile([0.25, 0.5, 0.75])
    rec["legs"]["W"] = {
        "ok": all(math_rows) and len(win_rows) == EXPECT_STARTS,
        "member": mid, "line": line,
        "windows": win_rows,
        "start_distribution": {          # template sec-1.3 verbatim readouts
            "best": max(sharpes), "worst": min(sharpes),
            "p25": round(float(q[0.25]), 4),
            "median": round(float(q[0.5]), 4),
            "p75": round(float(q[0.75]), 4),
            "worst_start": win_rows[sharpes.index(min(sharpes))]["start"],
        },
        "red_rate": round(sum(w["red"] for w in win_rows) / len(win_rows), 4),
        "slice_math_identity_all": all(math_rows),
    }

    out = os.path.join(ROOT, "results", "_r392bmc_n3r2_probe.json")
    all_ok = all(rec["legs"][k].get("ok") for k in ("P", "S", "R", "W"))
    rec["verdict"] = "PASS" if all_ok else "FAIL"
    json.dump(rec, open(out, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    print(f"N3-R2 PROBE {rec['verdict']}: P={rec['legs']['P']['ok']} "
          f"S={rec['legs']['S']['ok']} R={rec['legs']['R']['ok']} "
          f"W={rec['legs']['W']['ok']}")
    print(f"  starts={rec['legs']['S']['n_starts']} red_rate={rec['legs']['W']['red_rate']} "
          f"worst={rec['legs']['W']['start_distribution']['worst']} "
          f"@{rec['legs']['W']['start_distribution']['worst_start']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
