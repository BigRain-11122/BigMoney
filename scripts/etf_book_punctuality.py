"""How much is punctuality worth? Delay tolerance of the bond-free ETF book.

Why this face exists
--------------------
Every published face of this book assumes the sheet is executed at the open of the very
bar it was decided on. The operator is a human (or a person forwarding a sheet): the real
failure mode is not "slightly worse prices", it is "I placed it on Thursday instead of
Tuesday", or "I skipped this month's sheet". No published number answers that question,
so nobody knows whether the discipline the sheets demand is worth anything.

What it measures
----------------
Two axes, both priced against the same control that must reproduce the published runs:

* lag      -- decide on bar d, execute at the open of bar d+N (N = 0,1,2,3,5,10). The
             book between the decision and the fill is the previous book (nobody sells in
             advance), the sizing overlay is still read at the decision bar because the
             sheet has to print a size.
* cadence  -- the operator only acts on every second sheet (rebalance 40 instead of 20),
             i.e. half the sheets never reach the market.

The control arm (lag 0, cadence 20) is asserted equal to `etf_robust_pf.open_to_open_equity`
to 1e-12 on the equity curve before any number is printed; if that leg breaks, the whole
table is meaningless and the script refuses to write a face.

Money is reported on a stated capital, because "CAGR -0.42pp" is not a decision.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R

IS_END = "2023-12-31"
CAPITAL_CNY = 1_000_000.0
LAGS = (0, 1, 2, 3, 5, 10)
CADENCES = (20, 40)
ARMS = (("nobond_base", None), ("nobond_vt08", 0.08))


def replay(close, openp, amt, score, rebal, n_hold, cost, vol_target=None,
           lag=0, vol_window=60, phase=0):
    """Mirror of etf_robust_pf.open_to_open_equity with one addition: a decision taken on
    bar d is filled at the open of bar d+lag. lag=0, phase=0 is bit-identical to the engine.

    phase shifts the rebalance grid by that many bars (0..rebal-1). It exists because a
    single decision sequence is one path, not a law: any delay verdict has to survive
    moving the grid, otherwise it is just where this particular grid happened to land."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(R.START)]
    rets = op.pct_change()
    equity, held, daily, turns = 1.0, {}, [], []
    pending, pending_at, executed_late = None, None, 0

    def book_vol(book, upto):
        if not book:
            return np.nan
        window = rets.loc[:upto].tail(vol_window)[list(book)]
        if window.shape[0] < 20:
            return np.nan
        w = np.array([book[k] for k in window.columns])
        cov = window.cov().to_numpy()
        return float(np.sqrt(w @ cov @ w) * np.sqrt(252))

    def trade(w):
        nonlocal equity, held
        turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
        equity *= (1.0 - cost * turn)
        turns.append(turn)
        held = w

    for i in range(len(dates) - 1):
        d = dates[i]
        if pending is not None and i == pending_at:
            trade(pending)
            executed_late += 1
            pending, pending_at = None, None
        if (i - phase) % rebal == 0 and i >= phase:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                scale = 1.0
                if vol_target:
                    v = book_vol(w, d)
                    if np.isfinite(v) and v > 0:
                        scale = float(max(0.0, min(1.0, vol_target / v)))
                w = {k: v * scale for k, v in w.items()}
                if lag == 0:
                    trade(w)
                else:
                    pending, pending_at = w, i + lag
        nxt = dates[i + 1]
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))
    ser = pd.Series(dict(daily)).sort_index()
    return ser, (float(np.mean(turns)) if turns else 0.0), executed_late


def build(universe_kind="nobond"):
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], sc, n_flip, cls


def stat_block(ser, label):
    m = A.stats2(ser, label)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    return m


def run(out_path=None):
    close, openp, amt, sc, n_flip, cls = build()
    rows, control_legs = [], []

    for arm, vt in ARMS:
        # control: engine itself, then our replay at lag 0 / cadence 20 must match it
        ref, ref_turn = R.open_to_open_equity(close, openp, amt, sc, 20, 5, 0.0010, vol_target=vt)
        mine, mine_turn, _ = replay(close, openp, amt, sc, 20, 5, 0.0010, vol_target=vt, lag=0)
        joined = pd.concat([ref.rename("ref"), mine.rename("mine")], axis=1).dropna()
        gap = float((joined["ref"] - joined["mine"]).abs().max()) if len(joined) else float("inf")
        turn_gap = abs(ref_turn - mine_turn)
        control_legs.append({"arm": arm, "bars": int(len(joined)),
                             "max_abs_level_gap": gap, "turnover_gap": turn_gap,
                             "reproduces_engine": gap <= 1e-12 and turn_gap <= 1e-12})
        if not (gap <= 1e-12 and turn_gap <= 1e-12):
            raise SystemExit("CONTROL_FAIL: replay(lag=0) does not reproduce the engine for %s "
                             "(gap=%r) -- refusing to publish a delay table" % (arm, gap))
        control = stat_block(ref, arm + "_control")
        rows.append({"arm": arm, "vol_target": vt, "axis": "control", "lag": 0,
                     "cadence": 20, "runs_late": 0, **control})

        for lag in LAGS:
            if lag == 0:
                continue
            ser, turn, late = replay(close, openp, amt, sc, 20, 5, 0.0010,
                                     vol_target=vt, lag=lag)
            rows.append({"arm": arm, "vol_target": vt, "axis": "lag", "lag": lag,
                         "cadence": 20, "runs_late": late, "turnover": round(turn, 4),
                         **stat_block(ser, "%s_lag%d" % (arm, lag))})

        for cad in CADENCES:
            if cad == 20:
                continue
            ser, turn, late = replay(close, openp, amt, sc, cad, 5, 0.0010,
                                     vol_target=vt, lag=0)
            rows.append({"arm": arm, "vol_target": vt, "axis": "cadence", "lag": 0,
                         "cadence": cad, "runs_late": 0, "turnover": round(turn, 4),
                         **stat_block(ser, "%s_cad%d" % (arm, cad))})

    # money answer: each delay line priced against its own control on the stated capital
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["arm"], []).append(r)
    money = []
    for arm, rs in by_arm.items():
        ctl = next(r for r in rs if r["axis"] == "control")
        for r in rs:
            if r["axis"] == "control":
                continue
            dcagr = r["cagr"] - ctl["cagr"]
            money.append({"arm": arm, "axis": r["axis"], "lag": r["lag"],
                          "cadence": r["cadence"],
                          "dcagr_pp_vs_control": round(dcagr * 100, 2),
                          "cny_per_year_vs_control": round(dcagr * CAPITAL_CNY, 0),
                          "dsharpe": round(r["sharpe"] - ctl["sharpe"], 3),
                          "dmaxdd_pp": round((r["maxdd"] - ctl["maxdd"]) * 100, 2)})

    # path test: the same scenarios on 5 decision phases. A verdict that only holds where
    # this grid happens to land is not a verdict (r1325 lineage).
    scenarios = [("lag", lag, 20) for lag in LAGS if lag] + [("cadence", 0, 40)]
    phases = []
    for arm, vt in ARMS:
        ctl_phase = {}
        for ph in range(5):
            ctl_phase[ph] = stat_block(
                replay(close, openp, amt, sc, 20, 5, 0.0010, vol_target=vt,
                       lag=0, phase=ph)[0], "%s_ctl_ph%d" % (arm, ph))["cagr"]
        for axis, lag, cad in scenarios:
            cells = []
            for ph in range(5):
                ser = replay(close, openp, amt, sc, cad, 5, 0.0010, vol_target=vt,
                             lag=lag, phase=ph)[0]
                cagr = stat_block(ser, "%s_%s%d_ph%d" % (arm, axis, lag or cad, ph))["cagr"]
                cells.append(round((cagr - ctl_phase[ph]) * 100, 2))
            cells_sorted = sorted(cells)
            med = round(float(np.median(cells)), 2)
            phases.append({
                "arm": arm, "axis": axis, "lag": lag, "cadence": cad,
                "per_phase_dcagr_pp": cells,
                "median_dcagr_pp": med,
                "worst_dcagr_pp": cells_sorted[0],
                "best_dcagr_pp": cells_sorted[-1],
                "share_phases_losing": round(sum(1 for c in cells if c < 0) / len(cells), 2),
                "median_cny_per_year": round(med / 100.0 * CAPITAL_CNY, 0),
                # a verdict needs the effect to beat its own phase noise
                "verdict": ("LATENESS_COSTS" if med < 0 and
                            sum(1 for c in cells if c < 0) / len(cells) >= 0.8 and
                            abs(med) > 0.5 * (cells_sorted[-1] - cells_sorted[0]) else
                            "NOT_MEASURABLE"),
            })

    # what the discipline is worth: full tolerance curve per arm
    tol = []
    for arm, rs in by_arm.items():
        curve = sorted([(r["lag"], r["cagr"]) for r in rs if r["axis"] == "lag"] +
                       [(0, next(r["cagr"] for r in rs if r["axis"] == "control"))])
        tol.append({"arm": arm,
                    "curve_lag_to_cagr": [[a, round(float(b), 4)] for a, b in curve],
                    "monotone": all(curve[k][1] >= curve[k + 1][1] - 1e-9
                                    for k in range(len(curve) - 1))})

    # one sentence, built from the phase cells so it cannot drift from them
    def _cell(arm, axis, lag):
        return next(p for p in phases if p["arm"] == arm and p["axis"] == axis
                    and (p["lag"] == lag if axis == "lag" else p["cadence"] == 40))

    sentences = []
    for arm, _vt in ARMS:
        one = _cell(arm, "lag", 1)
        skip = _cell(arm, "cadence", 0)
        sentences.append(
            "On %s, filling each sheet one open late gives back %.2fpp a year "
            "(%s CNY on %s; %d/5 decision grids agree, range %.2f..%.2fpp); "
            "acting on every second sheet gives back %.2fpp (%s CNY)."
            % (arm, abs(one["median_dcagr_pp"]),
               "{:,.0f}".format(abs(one["median_cny_per_year"])),
               "{:,.0f}".format(CAPITAL_CNY), sum(1 for c in one["per_phase_dcagr_pp"]
                                                  if c < 0),
               one["worst_dcagr_pp"], one["best_dcagr_pp"],
               abs(skip["median_dcagr_pp"]),
               "{:,.0f}".format(abs(skip["median_cny_per_year"]))))

    payload = {
        "face": "etf_book_punctuality",
        "question": "How much of the book's return survives if the sheet is filled late, "
                    "or if a sheet is simply skipped?",
        "evidence_cutoff": str(close.index[-1].date()),
        "capital_cny": CAPITAL_CNY,
        "config": {"rebal": 20, "n_hold": 5, "cost_per_edge": 0.0010,
                   "vol_window": 60, "is_end": IS_END, "universe": "bond-free",
                   "phases": 5},
        "panel": {"symbols": int(close.shape[1]), "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date()), "flips_repaired": int(n_flip)},
        "control_legs": control_legs,
        "rows": rows,
        "money_vs_control": money,
        "phases": phases,
        "tolerance": tol,
        "headline": sentences,
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1, ensure_ascii=False)
        print("wrote", out_path)
    return payload


def _fixture(n=600):
    """3-name panel: A ramps +0.1%/bar the whole way, B and C flat, score always A>B>C.
    Long enough that the eligibility history gate (E.MIN_HIST) actually opens."""
    idx = pd.bdate_range("2020-01-01", periods=n)
    a = 1.0 + 0.001 * np.arange(n)
    close = pd.DataFrame({"A": a, "B": np.ones(n), "C": np.ones(n)}, index=idx)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(1e9, index=idx, columns=close.columns)
    score = pd.DataFrame({"A": 3.0, "B": 2.0, "C": 1.0}, index=idx)
    return close, openp, amt, score, idx


def selftest():
    """Hermetic: a synthetic panel where the answer is known by construction."""
    legs = []
    close, openp, amt, score, idx = _fixture()

    s0, t0, late0 = replay(close, openp, amt, score, 20, 1, 0.0, lag=0)
    r0 = s0.pct_change().dropna()
    legs.append(("lag0_never_fills_late", late0 == 0))
    legs.append(("lag0_actually_trades", float(r0.abs().sum()) > 0.01))

    s1, t1, late1 = replay(close, openp, amt, score, 20, 1, 0.0, lag=1)
    legs.append(("lag1_fills_late", late1 >= 10))
    # the delayed book must not be identical to the punctual one on a rising panel
    legs.append(("lag1_differs_from_lag0", abs(float(s1.iloc[-1]) - float(s0.iloc[-1])) > 1e-9))

    # on a ramp, holding A from bar k onward = a straight-line ratio to A itself:
    # the only thing the delay changes is WHERE the curve joins the ramp.
    ratio = s0 / (close["A"].loc[s0.index] / close["A"].loc[s0.index[0]])
    legs.append(("lag0_tracks_the_held_name_exactly",
                 float(ratio.iloc[-20:].std()) < 1e-5 and float(ratio.iloc[-1]) < 1.0))
    r1 = s1.pct_change().dropna()
    first0 = int(np.argmax(r0.abs().to_numpy() > 0))
    first1 = int(np.argmax(r1.abs().to_numpy() > 0))
    legs.append(("lag1_joins_the_ramp_one_bar_later", first1 == first0 + 1))

    flat = pd.DataFrame({c: np.ones(len(idx)) for c in ("A", "B", "C")}, index=idx)
    fl = flat.shift(1).fillna(1.0)
    f0, _, _ = replay(flat, fl, amt, score, 20, 1, 0.0, lag=0)
    f3, _, _ = replay(flat, fl, amt, score, 20, 1, 0.0, lag=3)
    legs.append(("flat_panel_is_flat_at_any_lag",
                 abs(float(f3.iloc[-1]) - 1.0) < 1e-12 and abs(float(f0.iloc[-1]) - 1.0) < 1e-12))

    s40, t40, _ = replay(close, openp, amt, score, 40, 1, 0.0, lag=0)
    legs.append(("cadence_40_is_still_the_same_book_here",
                 abs(float(s40.iloc[-1]) - float(s0.iloc[-1])) < 1e-12))
    legs.append(("lag_is_not_cadence",
                 float(s40.iloc[-1]) != float(s1.iloc[-1])))
    failed = [n_ for n_, ok in legs if not ok]
    for n_, ok in legs:
        print(("PASS " if ok else "FAIL ") + n_)
    print("selftest %d/%d legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def check(out_path=None):
    """Re-derive the published face from its own cells. No panel rebuild: this leg asks
    whether the numbers still add up, not whether the market moved."""
    path = out_path or os.path.join(E.PATHS.results_dir, "etf_book_punctuality.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    bad = []
    legs = []

    repro = all(c["reproduces_engine"] and c["max_abs_level_gap"] <= 1e-12
                for c in d["control_legs"])
    legs.append(("control_replays_the_engine", repro, ""))
    if not repro:
        bad.append("control")

    ctl = {}
    for r in d["rows"]:
        if r["axis"] == "control":
            ctl[r["arm"]] = r["cagr"]
    legs.append(("every_arm_has_a_control", set(ctl) == {a for a, _ in ARMS},
                 str(sorted(ctl))))

    m_bad = []
    for m in d["money_vs_control"]:
        row = next(r for r in d["rows"] if r["arm"] == m["arm"] and r["axis"] == m["axis"]
                   and r["lag"] == m["lag"] and r["cadence"] == m["cadence"])
        want = round((row["cagr"] - ctl[m["arm"]]) * 100, 2)
        if abs(want - m["dcagr_pp_vs_control"]) > 0.011:
            m_bad.append((m["arm"], m["axis"], m["lag"], want, m["dcagr_pp_vs_control"]))
        cny = round((row["cagr"] - ctl[m["arm"]]) * d["capital_cny"], 0)
        if abs(cny - m["cny_per_year_vs_control"]) > 1.0:
            m_bad.append((m["arm"], m["axis"], m["lag"], "cny", cny,
                          m["cny_per_year_vs_control"]))
    legs.append(("money_is_the_row_minus_its_own_control", not m_bad, str(m_bad[:3])))
    if m_bad:
        bad.append("money_vs_control")

    p_bad = []
    for p in d["phases"]:
        cells = p["per_phase_dcagr_pp"]
        if abs(round(float(np.median(cells)), 2) - p["median_dcagr_pp"]) > 0.011:
            p_bad.append((p["arm"], p["axis"], p["lag"], "median"))
        if p["median_dcagr_pp"] < 0 and p["share_phases_losing"] >= 0.8 and \
                abs(p["median_dcagr_pp"]) > 0.5 * (p["best_dcagr_pp"] - p["worst_dcagr_pp"]):
            want = "LATENESS_COSTS"
        else:
            want = "NOT_MEASURABLE"
        if want != p["verdict"]:
            p_bad.append((p["arm"], p["axis"], p["lag"], "verdict", want, p["verdict"]))
    legs.append(("verdict_is_re_derivable_from_its_own_cells", not p_bad, str(p_bad[:3])))
    if p_bad:
        bad.append("phases")

    worst = None
    for p in d["phases"]:
        if p["axis"] == "lag" and p["lag"] == 1:
            if worst is None or p["median_dcagr_pp"] < worst["median_dcagr_pp"]:
                worst = p
    legs.append(("a_one_day_late_row_exists", worst is not None, ""))
    hl_bad = []
    for arm, _vt in ARMS:
        one = next(p for p in d["phases"] if p["arm"] == arm and p["axis"] == "lag"
                   and p["lag"] == 1)
        line = next((s for s in d["headline"] if arm in s), None)
        if line is None or ("%.2fpp" % abs(one["median_dcagr_pp"])) not in line:
            hl_bad.append(arm)
    legs.append(("headline_quotes_the_phase_cell", not hl_bad, str(hl_bad)))
    if hl_bad:
        bad.append("headline")
    for n_, ok, extra in legs:
        print(("PASS " if ok else "FAIL ") + n_ + ((" " + extra) if extra and not ok else ""))
    print("check %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    if len(argv) > 1 and argv[1] == "check":
        return check()
    out = os.path.join(E.PATHS.results_dir, "etf_book_punctuality.json")
    payload = run(out)
    print("evidence_cutoff", payload["evidence_cutoff"])
    for c in payload["control_legs"]:
        print("control", c["arm"], "reproduces_engine", c["reproduces_engine"],
              "bars", c["bars"])
    print("%-12s %-8s %5s %8s %7s %7s %10s" %
          ("arm", "axis", "lag", "cagr", "sharpe", "maxdd", "cny/yr"))
    for r in payload["rows"]:
        print("%-12s %-8s %5d %7.2f%% %7.3f %6.1f%%" %
              (r["arm"], r["axis"], r["lag"], r["cagr"] * 100, r["sharpe"], r["maxdd"] * 100))
    for m in payload["money_vs_control"]:
        print("money %-12s %-8s lag=%d cad=%d  %+6.2fpp  %+10.0f CNY/yr  dSharpe %+.3f" %
              (m["arm"], m["axis"], m["lag"], m["cadence"], m["dcagr_pp_vs_control"],
               m["cny_per_year_vs_control"], m["dsharpe"]))
    print("\nphases (5 decision grids; median vs own phase control)")
    for p in payload["phases"]:
        print("%-12s %-8s lag=%-2d cad=%-3d median %+6.2fpp  worst %+6.2f  best %+6.2f  "
              "lose-share %.2f  %-15s %+9.0f CNY/yr" %
              (p["arm"], p["axis"], p["lag"], p["cadence"], p["median_dcagr_pp"],
               p["worst_dcagr_pp"], p["best_dcagr_pp"], p["share_phases_losing"],
               p["verdict"], p["median_cny_per_year"]))
    for t in payload["tolerance"]:
        print("tolerance", t["arm"], "monotone", t["monotone"], t["curve_lag_to_cagr"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))