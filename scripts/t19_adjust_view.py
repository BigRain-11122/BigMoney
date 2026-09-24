"""T-2026-09-24-19 consolidation-break governance, stage-3 (adjusted view).

O-20260924-1612 (CEO-prompted unblock order) names stage-3 must-deliver-today;
O-20260924-1325 keeps option-a guard as the APPROVED consumption face and the
stage-2a paper flag on the T-20 relay timing (unchanged). This stage delivers
the ADDITIVE adjusted-view asset only -- raw panel stays authoritative for
frozen anchors (D2 lockbox, zero rewrite):

  build   -> data/consolidation/adjust_factors.json
             per-event back-adjustment factor (price-implied: close_k/prev_close_k
             from raw bars; day-k true market return is absorbed -> 0 by
             construction; official ratios stay a stage-2b evidence slot) +
             per-symbol break-day lists = the option-a guard consumption face
             (flag/drop evaluation rows; boundary face included per O-1325).
         -> data/consolidation/adjusted_view/<sym>.parquet (affected syms only)
             back-adjusted OHLCV(A): prices strictly before each break scaled by
             the cumulative factor, volume by its inverse (amount invariance),
             amount untouched; adds adj_factor + cons_break columns.
  gates   -> results/t19_adjust_view_gates.json
             GA break-day continuity (adj return == 0, verified from written
             files),              GB untouched segments (post-last-break rows value-exact raw after
             float64 volume normalization + every non-break return preserved), GC amount invariance (rel 1e-9),
             GD registry reconciliation (factor vs pct_observed/implied ratio,
             stated tolerances), GE coverage (19/19 syms, event dates in index),
             GF determinism (gate-side recompute bit-identical to written JSON).
  status  -> read-only face summary.
  selftest-> offline synthetic checks (factor math / cumulative product /
             amount invariance / boundary note / reconcile tolerances).

Consumption law (O-1325): evaluation/paper default = option-a guard via the
break lists here; the adjusted view serves the deep-axis clean re-run
(O-1612 item 1) and the future option-b adjudication after stage-2c numbers.
All 21 events are >= 2021-04-12, i.e. inside the T-18 deep window too
(2013-06-17 start) -> the factor series applies to the deep panel by date
join without touching Money02 (zero writes there).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.science_gates import cutoff_meta

REG_PATH = os.path.join(_REPO, "data", "consolidation", "registry.json")
FACTORS_PATH = os.path.join(_REPO, "data", "consolidation", "adjust_factors.json")
VIEW_DIR = os.path.join(_REPO, "data", "consolidation", "adjusted_view")
GATES_PATH = os.path.join(_REPO, "results", "t19_adjust_view_gates.json")

TOL_GA = 1e-12          # break-day adjusted return must be ~0 by construction
TOL_RET = 1e-12         # non-break return preservation
TOL_AMT = 1e-9           # amount-invariance relative tolerance
TOL_PCT = 5e-7           # registry pct_observed is rounded to 6dp
TOL_RATIO = 1e-6         # registry implied_ratio_approx is rounded to 6dp

GUARD_NOTE = ("option-a guard consumption face (O-1325 approved): flag/drop "
              "evaluation rows whose holding crosses a break day; boundary "
              "face included -- entry < break == exit_on_break also exposes "
              "phantom P&L (8/10 rows per exposure audit)")


def _load_registry() -> dict:
    reg = json.load(open(REG_PATH, encoding="utf-8-sig"))
    assert reg["counts"]["events"] == 21 and reg["counts"]["symbols"] == 19, \
        reg["counts"]
    return reg


def _events_by_sym(reg: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for e in reg["events"]:
        out.setdefault(e["sym"], []).append(e)
    for evs in out.values():
        evs.sort(key=lambda e: e["date"])
    return out


def _factor_frame(df: pd.DataFrame, evs: list[dict]) -> pd.DataFrame:
    """Cumulative back-adjustment factor per row: prod(f_k : break_k > row).

    Ascending event loop: rows strictly before each break accumulate that
    break's factor; the break row itself and later rows do not.
    """
    fac = pd.Series(1.0, index=df.index)
    brk = pd.Series(False, index=df.index)
    for e in evs:
        d = pd.Timestamp(e["date"])
        m = df.index < d
        fac[m] = fac[m] * e["factor"]
        if d in brk.index:
            brk[d] = True
    return pd.DataFrame({"adj_factor": fac, "cons_break": brk})


def _adjust(df: pd.DataFrame, ff: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    f = ff["adj_factor"]
    for col in ("open", "high", "low", "close"):
        out[col] = out[col] * f
    out["volume"] = out["volume"] / f          # amount invariance
    # amount untouched: as-traded currency, not rescaled by back-adjustment
    out["adj_factor"] = f
    out["cons_break"] = ff["cons_break"]
    return out


def _reconcile(ev: dict, df: pd.DataFrame) -> dict:
    """Derive the exact price-implied factor from raw bars + registry checks."""
    d = pd.Timestamp(ev["date"])
    pos = df.index.get_loc(d)
    prev_close = float(df.iloc[pos - 1]["close"])
    close = float(df.iloc[pos]["close"])
    factor = close / prev_close
    dp_pct = abs(factor - 1.0 - float(ev["pct_observed"]))
    dp_ratio = abs(1.0 / factor - float(ev["implied_ratio_approx"]))
    if dp_pct > TOL_PCT or dp_ratio > TOL_RATIO:
        raise AssertionError(
            f"registry reconciliation FAIL {ev['sym']}@{ev['date']}: "
            f"dp_pct={dp_pct:.3e} dp_ratio={dp_ratio:.3e}")
    return {
        "sym": ev["sym"], "date": ev["date"],
        "prev_date": str(df.index[pos - 1].date()),
        "prev_close": prev_close, "close": close,
        "factor": factor,
        "registry_pct_observed": ev["pct_observed"],
        "registry_implied_ratio_approx": ev["implied_ratio_approx"],
        "amplitude_class": ev["amplitude_class"],
        "reconcile_dp_pct": dp_pct, "reconcile_dp_ratio": dp_ratio,
        "ratio_source": "price_implied (official announcement pending "
                        "stage-2b; marginal-class events may reclassify)",
        "day_k_real_return": "absorbed into factor (== 0 by construction)",
    }


def build() -> int:
    import live.paper as LP                    # read-only face import
    reg = _load_registry()
    by_sym = _events_by_sym(reg)
    prices = LP.load_core()
    missing = [s for s in by_sym if s not in prices]
    assert not missing, f"registry syms absent from core face: {missing}"

    events_out, symbols_out = [], {}
    os.makedirs(VIEW_DIR, exist_ok=True)
    for sym, evs in sorted(by_sym.items()):
        df = prices[sym]
        recs = [_reconcile(e, df) for e in evs]
        events_out.extend(recs)
        ff = _factor_frame(df, [dict(e, factor=r["factor"])
                                for e, r in zip(evs, recs)])
        adj = _adjust(df, ff)
        path = os.path.join(VIEW_DIR, f"{sym}.parquet")
        adj.to_parquet(path)
        n_aff = int((adj["adj_factor"] != 1.0).sum())
        symbols_out[sym] = {
            "events": [r["date"] for r in recs],
            "factors": [r["factor"] for r in recs],
            "rows_total": int(len(adj)),
            "rows_affected": n_aff,
            "adjusted_view": f"data/consolidation/adjusted_view/{sym}.parquet",
        }
        print(f"[t19-adj] {sym}: events={len(recs)} rows_affected={n_aff} "
              f"-> {os.path.basename(path)}")

    cutoff = str(max(prices[s].index.max() for s in by_sym).date())
    first_ev = min(e["date"] for e in events_out)
    last_ev = max(e["date"] for e in events_out)
    out = {
        **cutoff_meta(cutoff),
        "registry": "consolidation_adjustment_factors",
        "schema_version": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "ticket": "T-2026-09-24-19",
        "stage": 3,
        "delivery": "O-20260924-1612 must-deliver-today (GF gate: "
                    "data/consolidation/adjust* + ticket note marker)",
        "panel_source": "data/daily/*.csv via live.paper.load_core "
                        "(raw face authoritative; D2 lockbox, zero rewrite)",
        "method": "price-implied back-adjustment: factor_k = close_k/prev_close_k; "
                  "history strictly before each break scaled by the cumulative "
                  "product, volume by its inverse (amount invariance), amount "
                  "untouched; day-k true market return absorbed (0 by "
                  "construction) pending stage-2b official ratios",
        "guard_consumption": GUARD_NOTE,
        "counts": {"events": len(events_out), "symbols": len(symbols_out),
                   "first_event": first_ev, "last_event": last_ev,
                   "deep_axis_applicability":
                       "all events >= 2021-04-12 > deep panel start "
                       "2013-06-17 -> factor series applies to the T-18 deep "
                       "panel by date join (zero Money02 writes)"},
        "events": events_out,
        "symbols": symbols_out,
        "governance": {
            "option_a": "approved (O-1325): registry break lists consumed as "
                        "evaluation/paper exclusion-marking mask",
            "option_b": "consumption adjudication deferred to post-stage-2c "
                        "per O-1325; this asset is the additive landing plane",
            "stage_2a": "paper forward-protection flag holds on the T-20 "
                        "relay timing (O-1325 explicit; bm-a lane active in "
                        "live/paper.py per MSG-20260924-1608)",
        },
    }
    with open(FACTORS_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[t19-adj] factors written: {FACTORS_PATH} "
          f"(events={len(events_out)}, syms={len(symbols_out)}, "
          f"evidence_cutoff={cutoff})")
    return 0


def _vals_eq(a: pd.Series, b: pd.Series) -> bool:
    """Value-exact comparison after float64 upcast (int64 volume in the raw
    face normalizes to float64 in the adjusted face; values < 2^53 upcast
    exactly). NaN pairs count as equal."""
    if len(a) != len(b):
        return False
    af = a.astype("float64").to_numpy()
    bf = b.astype("float64").to_numpy()
    both_nan = pd.isna(af) & pd.isna(bf)
    return bool(((af == bf) | both_nan).all())


def _gate_results(reg: dict, prices: dict) -> dict:
    fac = json.load(open(FACTORS_PATH, encoding="utf-8-sig"))
    by_sym = _events_by_sym(reg)
    rows = {"GA": [], "GB": [], "GC": [], "GD": [], "GE": [], "GF": []}

    # GF determinism basis: gate-side recompute vs written JSON (exact floats)
    written = {(e["sym"], e["date"]): e["factor"] for e in fac["events"]}

    for sym, evs in sorted(by_sym.items()):
        raw = prices[sym]
        adj = pd.read_parquet(os.path.join(VIEW_DIR, f"{sym}.parquet"))
        ev_ix = [pd.Timestamp(e["date"]) for e in evs]
        # GE coverage: sym in face, event dates present, break rows marked only
        dates_ok = all(d in raw.index for d in ev_ix)
        marks_ok = all(bool(adj.at[d, "cons_break"]) for d in ev_ix)
        others = adj.index[~adj.index.isin(ev_ix)]
        rows["GE"].append(sym in prices and dates_ok and marks_ok
                          and not bool(adj.loc[others, "cons_break"].any()))
        # GD registry reconciliation / GF written-JSON bit-identity
        for e, w in zip(evs, [written[(sym, x["date"])] for x in evs]):
            pos = raw.index.get_loc(pd.Timestamp(e["date"]))
            f = float(raw.iloc[pos]["close"]) / float(raw.iloc[pos - 1]["close"])
            rows["GF"].append(abs(f - w) == 0.0)
            rows["GD"].append(
                abs(f - 1.0 - float(e["pct_observed"])) <= TOL_PCT
                and abs(1.0 / f - float(e["implied_ratio_approx"])) <= TOL_RATIO)
        # GA continuity at each break, verified from written files
        for d in ev_ix:
            i = adj.index.get_loc(d)
            r = float(adj.iloc[i]["close"]) / float(adj.iloc[i - 1]["close"]) - 1.0
            rows["GA"].append(abs(r) <= TOL_GA)
        # GB untouched segments: post-last-break rows value-exact vs raw
        # (adjusted face normalizes volume to float64 via inverse-factor
        # arithmetic; post-break values stay exact); every non-break return
        # preserved (NaN closes skipped, counted honestly)
        last = ev_ix[-1]
        post = adj[adj.index > last]
        praw = raw[raw.index > last]
        gb_post = all(_vals_eq(post[c], praw[c]) for c in
                      ("open", "high", "low", "close", "volume", "amount"))
        rows["GB"].append(gb_post)
        gb_ret, nan_skip = True, 0
        for i in range(1, len(adj)):
            if adj.index[i] in ev_ix:
                continue
            c_a, c_p = float(raw.iloc[i]["close"]), float(raw.iloc[i - 1]["close"])
            if c_a != c_a or c_p != c_p:            # NaN close pair: skip+count
                nan_skip += 1
                continue
            ra = float(adj.iloc[i]["close"]) / float(adj.iloc[i - 1]["close"]) - 1.0
            rr = c_a / c_p - 1.0
            if abs(ra - rr) > TOL_RET:
                gb_ret = False
                break
        rows["GB"].append(gb_ret)
        rows["_GB_nan_skipped"] = rows.get("_GB_nan_skipped", 0) + nan_skip
        # GC amount invariance (adj_close*adj_volume vs raw, NaN-aware)
        acv = adj["close"] * adj["volume"]
        rcv = raw["close"] * raw["volume"]
        tol = TOL_AMT * rcv.abs().clip(lower=1.0)
        diff_ok = ((acv - rcv).abs() <= tol) | (acv.isna() & rcv.isna())
        rows["GC"].append(bool(diff_ok.all()) and adj["amount"].equals(raw["amount"]))
    rows["_GB_nan_skipped"] = rows.get("_GB_nan_skipped", 0)
    gates = {k: bool(rows[k]) and all(rows[k]) for k in
             ("GA", "GB", "GC", "GD", "GE", "GF")}
    gates["_counts"] = {k: len(rows[k]) for k in
                        ("GA", "GB", "GC", "GD", "GE", "GF")}
    gates["_GB_nan_skipped"] = rows["_GB_nan_skipped"]
    return gates


def gates() -> int:
    reg = _load_registry()
    print("[t19-adj] gates: loading raw face ...")
    import live.paper as LP                    # read-only face import
    prices = LP.load_core()
    g = _gate_results(reg, prices)
    ok = all(g[k] for k in ("GA", "GB", "GC", "GD", "GE", "GF"))
    fac = json.load(open(FACTORS_PATH, encoding="utf-8-sig"))
    out = {
        **cutoff_meta(fac["evidence_cutoff"]),
        "batch": "t19_adjust_view_gates",
        "ticket": "T-2026-09-24-19",
        "stage": 3,
        "deliverable": "adjusted-view asset verification (written files)",
        "tolerances": {"GA_break_ret": TOL_GA, "GB_ret_preserved": TOL_RET,
                       "GB_post_segment": "value-exact after float64 upcast "
                                          "(adjusted face volume dtype "
                                          "normalization, disclosed)",
                       "GC_amount_rel": TOL_AMT, "GD_pct": TOL_PCT,
                       "GD_ratio": TOL_RATIO},
        "gates": g,
        "ledger_trials_added": 0,
        "audit": "data-face verification, zero engine runs",
        "verdict": "PASS" if ok else "FAIL",
    }
    with open(GATES_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for k in ("GA", "GB", "GC", "GD", "GE", "GF"):
        print(f"  [t19-adj] {k}: {'PASS' if g[k] else 'FAIL'}")
    print(f"[t19-adj] gates verdict: {out['verdict']} -> {GATES_PATH}")
    return 0 if ok else 1


def status() -> int:
    fac = json.load(open(FACTORS_PATH, encoding="utf-8-sig"))
    files = sorted(os.listdir(VIEW_DIR)) if os.path.isdir(VIEW_DIR) else []
    print(f"[t19-adj] stage={fac['stage']} events={fac['counts']['events']} "
          f"symbols={fac['counts']['symbols']} "
          f"evidence_cutoff={fac['evidence_cutoff']}")
    print(f"[t19-adj] adjusted_view files: {len(files)} "
          f"({files[0] if files else '-'} .. {files[-1] if files else '-'})")
    print(f"[t19-adj] consumption: {fac['guard_consumption'][:100]} ...")
    return 0


def selftest() -> bool:
    ok = True

    def _chk(name, cond):
        nonlocal ok
        print(f"  [t19-adj] {name}: {'PASS' if cond else 'FAIL'}")
        ok = ok and bool(cond)

    # S1 single-break factor math: [10 -> 5] == -50% break, history halves
    days = pd.bdate_range("2026-01-05", periods=3)
    df = pd.DataFrame({"open": [10.0, 10.0, 5.0], "high": [10.0, 10.0, 5.0],
                       "low": [10.0, 10.0, 5.0], "close": [10.0, 10.0, 5.0],
                       "volume": [100.0, 100.0, 100.0],
                       "amount": [1000.0, 1000.0, 500.0]}, index=days)
    evs = [{"sym": "X", "date": str(days[2].date()), "factor": 0.5}]
    ff = _factor_frame(df, evs)
    adj = _adjust(df, ff)
    _chk("S1 break-day adj return == 0",
         abs(adj.iloc[2]["close"] / adj.iloc[1]["close"] - 1.0) <= TOL_GA)
    _chk("S1 history scaled (row0 close 10 -> 5)",
         abs(float(adj.iloc[0]["close"]) - 5.0) <= TOL_GA)
    # S2 two breaks: [10, 5, 10] -> fully continuous adjusted series
    days2 = pd.bdate_range("2026-01-05", periods=3)
    df2 = pd.DataFrame({"open": [10.0, 5.0, 10.0], "high": [10.0, 5.0, 10.0],
                        "low": [10.0, 5.0, 10.0], "close": [10.0, 5.0, 10.0],
                        "volume": [100.0, 100.0, 100.0],
                        "amount": [1000.0, 500.0, 1000.0]}, index=days2)
    evs2 = [{"sym": "X", "date": str(days2[1].date()), "factor": 0.5},
            {"sym": "X", "date": str(days2[2].date()), "factor": 2.0}]
    ff2 = _factor_frame(df2, evs2)
    adj2 = _adjust(df2, ff2)
    _chk("S2 cumulative: row0 factor 1.0 (0.5*2.0)",
         abs(float(adj2.iloc[0]["adj_factor"]) - 1.0) <= TOL_GA)
    _chk("S2 continuity both breaks",
         abs(adj2.iloc[1]["close"] / adj2.iloc[0]["close"] - 1.0) <= TOL_GA
         and abs(adj2.iloc[2]["close"] / adj2.iloc[1]["close"] - 1.0) <= TOL_GA)
    _chk("S2 cons_break marks exactly the two event days",
         bool(adj2.iloc[1]["cons_break"]) and bool(adj2.iloc[2]["cons_break"])
         and not bool(adj2.iloc[0]["cons_break"]))
    # S3 amount invariance: adj_close*adj_volume == close*volume
    lhs = (adj2["close"] * adj2["volume"]).abs()
    rhs = (df2["close"] * df2["volume"]).abs()
    _chk("S3 amount invariance", bool((lhs - rhs).abs().max() <= TOL_AMT))
    # S4 guard note carries the boundary face (O-1325 s5 correction)
    _chk("S4 boundary face in guard note", "boundary" in GUARD_NOTE)
    # S5 reconcile tolerance law: 6dp-rounded registry pct fits TOL_PCT
    pct_full = -0.510322
    pct_reg = round(pct_full, 6)
    _chk("S5 rounded pct within TOL_PCT",
         abs((1.0 + pct_full) - (1.0 + pct_reg)) <= TOL_PCT)
    print(f"  [t19-adj] selftest {'PASS' if ok else 'FAIL'}")
    return ok


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return 0 if selftest() else 1
    if argv and argv[0] == "build":
        return build()
    if argv and argv[0] == "gates":
        return gates()
    if argv and argv[0] == "status":
        return status()
    if argv and argv[0] == "all":
        rc = build()
        return rc or gates()
    print("usage: t19_adjust_view.py [build|gates|status|all|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
