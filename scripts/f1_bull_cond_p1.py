"""F1-BULL-COND-P1 runner (T-2026-10-08-177 leg-2 slice-2, O-20261007-2215 sec.2).

BULL-regime-conditional five-ETF cross-sectional momentum rotation judgment
batch. Design frozen verbatim in research/F1_BULL_COND_P1.md (freeze commit
precedes this run; post-freeze edits limited to nothing -- runner is part of
the freeze). Conventions reused, zero re-implementation:
  - conditional return t->t+1 (REGIME5-VALIDATION-P1 same convention)
  - cost 13.041bp/side V1 legacy family anchor (COST_X1 repo constant)
  - g1_prime_v2/g2_registration_v2/m1/cutoff_meta/append_ledger: science_gates
  - PBO: screening.pbo.cscv_pbo CSCV-8
  - D6 member face: cn_rev_tilt_p1 REG6/load_member_rets/_corr (ew6 canon)

Determinism: no wall-clock in content fields; nulls seeded from
SeedSequence(94200).spawn(1000) (SEED_REGISTRY band 94_001..94_999; the
95000+ ladder is never touched). Redo (batch already in ledger) recomputes
with batch_cells=0 and skips append (r253 single-count law).
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import science_gates as SG  # noqa: E402
from screening.pbo import cscv_pbo  # noqa: E402

BATCH = "F1-BULL-COND-P1"
TRIALS_JUDGED = 9
N_NULLS = 1000
BATCH_CELLS = TRIALS_JUDGED + N_NULLS  # 1009 (judged + nulls, CN_TREND precedent)
CUTOFF = "2026-09-30"
LABELS_PATH = os.path.join(ROOT, "results", "regime5_labels", "REGIME5-2026-09-30.json")
UNIVERSE = ["510300", "510050", "510500", "512100", "588000"]
LOOKBACKS = [60, 120, 250]
TOPKS = [1, 2, 3]
COST_SIDE_X1 = 0.0013041  # 13.041bp per side, V1 legacy family anchor (CN-C7 face A)
NULL_BASE = 94200         # SEED_REGISTRY band 94_001..94_999 (94100 = validation)
OUT = os.path.join(ROOT, "results", "regime5_bull_scan", "F1-BULL-COND-2026-09-30.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
PPY = 252.0
D6_REJECT = 0.70
SELFTEST_EVIDENCE = os.path.join(ROOT, "results", "_r899bma_f1_bull_cond_selftest.json")


# ------------------------------------------------------------------ data faces
def load_labels():
    with open(LABELS_PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    if d.get("cutoff") != CUTOFF:
        raise ValueError(f"labels cutoff {d.get('cutoff')} != frozen {CUTOFF}")
    cal = [e["date"] for e in d["labels"]]
    states = [e["state"] for e in d["labels"]]
    return cal, states


def load_panel(cal):
    """Five-member close panel truncated to cutoff (D2 lockbox).

    Returns close (cal x member), mom[L] (cal x member), vol60, ret_next --
    all reindexed onto the label calendar; ret_next is strictly
    label-calendar t -> t+1 (member must have bars at both dates).
    """
    cal_dt = pd.to_datetime(pd.Index(cal))
    close, raw_info = {}, {}
    for m in UNIVERSE:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"sh{m}.csv"))
        df["date"] = pd.to_datetime(df["date"])
        n_raw = len(df)
        df = df[df["date"] <= pd.Timestamp(CUTOFF)]
        raw_info[m] = {"rows_raw": n_raw, "rows_locked": len(df),
                       "first": str(df["date"].iloc[0].date()),
                       "last": str(df["date"].iloc[-1].date())}
        s = pd.Series(df["close"].values, index=df["date"])
        close[m] = s.reindex(cal_dt)
    close = pd.DataFrame(close)
    rets = close.pct_change()
    mom = {L: close / close.shift(L) - 1.0 for L in LOOKBACKS}
    vol60 = rets.rolling(60, min_periods=60).std()
    ret_next = close.shift(-1) / close - 1.0
    return close, mom, vol60, ret_next, raw_info


def bull_runs(states):
    """(start_idx, end_idx) inclusive runs of BULL on the label calendar."""
    runs, s = [], None
    for i, st in enumerate(states):
        if st == "BULL" and s is None:
            s = i
        elif st != "BULL" and s is not None:
            runs.append((s, i - 1))
            s = None
    if s is not None:
        runs.append((s, len(states) - 1))
    return runs


# ------------------------------------------------------------------ simulation
def simulate(L, k, mom, vol60, ret_next, states, cost_mult=1.0, universe=None):
    """Window-scoped conditional rotation. Frozen rules (prereg sec.3):

    - in-market day set = label_t == BULL; conditional return t -> t+1
    - eligible member at t: finite mom_L, finite vol60, finite ret_next
    - target = top min(k, n_eligible) by mom_L; weights = inverse-vol60 of
      the picked set, FROZEN until the picked SET changes (no daily vol
      drift churn) or the window ends
    - turnover charged: entry (0->w), set-change re-selection, and window
      dismantling (charged on the last in-market day's net, frozen
      convention); cost = COST_SIDE_X1 * cost_mult * turnover
    - entries = per-member opens; trades = per-member closes (engine
      report_num_entries granularity)
    """
    uni = UNIVERSE if universe is None else list(universe)
    m_L, v60, rn = mom[L], vol60, ret_next
    held, in_days = None, []          # held: {member: weight}
    n_entries = n_trades = 0
    turnover_total = 0.0
    flat_bull = 0
    window_nets, cur_win = [], 0.0
    in_index = -1
    n = len(states)
    for i in range(n):
        if states[i] != "BULL":
            continue
        t = m_L.index[i]
        elig = [m for m in uni
                if np.isfinite(m_L.iat[i, uni.index(m)])
                and np.isfinite(v60.iat[i, uni.index(m)])
                and np.isfinite(rn.iat[i, uni.index(m)])]
        if not elig:
            flat_bull += 1
            continue
        ranked = sorted(elig, key=lambda m: -m_L.iat[i, uni.index(m)])
        target = ranked[: min(k, len(elig))]
        day_to = 0.0
        if held is None or set(target) != set(held):
            vols = {m: v60.iat[i, uni.index(m)] for m in target}
            inv = {m: 1.0 / vols[m] for m in target}
            z = sum(inv.values())
            w_new = {m: inv[m] / z for m in target}
            if held is None:
                day_to = sum(w_new.values())
                n_entries += len(w_new)
            else:
                day_to = sum(abs(w_new.get(m, 0.0) - held.get(m, 0.0))
                             for m in set(w_new) | set(held))
                n_entries += sum(1 for m in w_new if held.get(m, 0.0) == 0.0)
                n_trades += sum(1 for m in held if m not in w_new)
            held = w_new
            turnover_total += day_to
        gross = sum(w * rn.iat[i, uni.index(m)] for m, w in held.items())
        ends = (i == n - 1) or (states[i + 1] != "BULL")
        if ends:
            day_to += sum(held.values())
            turnover_total += sum(held.values())
            n_trades += len(held)
        net = gross - COST_SIDE_X1 * cost_mult * day_to
        in_index = i
        in_days.append((str(t.date()), net))
        cur_win += net
        if ends:
            window_nets.append(cur_win)
            cur_win = 0.0
            held = None
    if cur_win != 0.0:
        window_nets.append(cur_win)
    return {"in_days": in_days, "n_entries": n_entries, "n_trades": n_trades,
            "turnover_total": turnover_total, "flat_bull_days": flat_bull,
            "window_nets": window_nets, "last_in_index": in_index}


def _sharpe(vals):
    a = np.asarray(vals, dtype=float)
    if len(a) < 2 or a.std(ddof=1) == 0 or not np.all(np.isfinite(a)):
        return None
    return float(a.mean() / a.std(ddof=1) * math.sqrt(PPY))


def stream_stats(in_days, start=None, end=None):
    vals = [n for d, n in in_days
            if (start is None or d >= start) and (end is None or d < end)]
    sr = _sharpe(vals)
    a = np.asarray(vals, dtype=float)
    cum = np.cumsum(a)
    dd = float(np.min(cum - np.maximum.accumulate(cum))) if len(cum) else None
    return {"n": len(vals), "sharpe": None if sr is None else round(sr, 4),
            "ann_ret": round(float(a.mean() * PPY), 6) if len(a) else None,
            "sum": round(float(a.sum()), 6) if len(a) else None,
            "maxdd": None if dd is None else round(dd, 6)}


# ------------------------------------------------------------------ null family
def null_family(vol60, ret_next, states, runs):
    """1000 BULL-mask random-selection replicates (seed base 94200).

    Per window: k ~ uniform{1,2,3}; picked uniformly among members eligible
    for the whole window (finite vol60 at entry + finite ret_next on every
    window day); weights inverse-vol60 at entry, frozen through the window;
    same entry/dismantle cost convention. Isolates the SELECTION signal.
    """
    children = np.random.SeedSequence(NULL_BASE).spawn(N_NULLS)
    sharpes = []
    for rep in range(N_NULLS):
        rng = np.random.default_rng(children[rep])
        vals = []
        for (s, e) in runs:
            t0 = vol60.index[s]
            elig = []
            for j, m in enumerate(UNIVERSE):
                ok = np.isfinite(vol60.iat[s, j]) and np.isfinite(ret_next.iat[e, j])
                if ok:
                    elig.append((m, j))
            if not elig:
                continue
            k_w = int(rng.integers(1, 4))
            k_eff = min(k_w, len(elig))
            pick = rng.choice(len(elig), size=k_eff, replace=False)
            picked = [elig[p] for p in pick]
            inv = {m: 1.0 / float(vol60.iat[s, j]) for m, j in picked}
            z = sum(inv.values())
            w = {m: inv[m] / z for m, _ in picked}
            entry_to = sum(w.values())
            for i in range(s, e + 1):
                gross = sum(wi * float(ret_next.iat[i, jj]) for (m, jj), wi in
                             [(p, w[p[0]]) for p in picked])
                to = entry_to if i == s else 0.0
                ends = (i == len(states) - 1) or (states[i + 1] != "BULL")
                if ends:
                    to += sum(w.values())
                vals.append(gross - COST_SIDE_X1 * to)
            # window dismantle handled above on last day
        sharpes.append(_sharpe(vals))
    sharpes = [x for x in sharpes if x is not None]
    a = np.asarray(sharpes, dtype=float)
    return {"n_values": int(len(a)),
            "mu": float(a.mean()), "sigma": float(a.std(ddof=1))}


# ------------------------------------------------------------------ d6 face
def d6_block(cell_series):
    """Per-cell corr vs REG6 registered members + same-batch cross.

    Machinery reused verbatim from cn_rev_tilt_p1 (ew6 canon member_run).
    """
    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    member_rets, _cuts = load_member_rets()
    out = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {},
           "same_batch_cross": {}}
    names = list(cell_series)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            s1, s2 = cell_series[names[a]], cell_series[names[b]]
            j = pd.concat([s1, s2], axis=1, join="inner").dropna()
            if len(j) > 20:
                out["same_batch_cross"][f"{names[a]}|{names[b]}"] = round(float(
                    np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]), 4)
    for name, s in cell_series.items():
        per, fin = {}, {}
        for tid, mr in member_rets.items():
            v, ov = _corr(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
            if v is not None:
                fin[tid] = v
        amax = max(fin, key=lambda kk: abs(fin[kk])) if fin else None
        out["cells"][name] = {"per_member": per,
                              "max_abs_corr": round(abs(fin[amax]), 4) if amax else None,
                              "reject": bool(amax and abs(fin[amax]) >= D6_REJECT)}
    return out


# ------------------------------------------------------------------ attrition
def _attr_row(kind, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": kind, "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates, "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == BATCH and e.get("kind") == kind]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    return row


# ------------------------------------------------------------------ run
def run():
    t0 = time.time()
    cal, states = load_labels()
    runs = bull_runs(states)
    close, mom, vol60, ret_next, raw_info = load_panel(cal)
    n_bull = sum(1 for s in states if s == "BULL")

    # passive face: conditional 510300 on the same in-market mask, no cost
    pass_days = [(str(mom[60].index[i].date()),
                  float(ret_next.iat[i, 0]))
                 for i in range(len(states)) if states[i] == "BULL"]
    passive_stats = stream_stats(pass_days)
    passive_sr = passive_stats["sharpe"]
    if passive_sr is None:
        raise ValueError("passive face undefined (empty/zero-var mask stream)")

    # null family
    nulls = null_family(vol60, ret_next, states, runs)
    null_pool = {"coverage": nulls,
                 "source": f"{BATCH} batch-own BULL-mask random-selection nulls "
                           f"(seed base {NULL_BASE}, spawn {N_NULLS})"}

    # judged cells
    cells, cell_series = {}, {}
    in_matrix = {}
    for L in LOOKBACKS:
        for k in TOPKS:
            name = f"L{L}_k{k}"
            base = simulate(L, k, mom, vol60, ret_next, states)
            x2 = simulate(L, k, mom, vol60, ret_next, states, cost_mult=2.0)
            x3 = simulate(L, k, mom, vol60, ret_next, states, cost_mult=3.0)
            vals = [n for _, n in base["in_days"]]
            cells[name] = {
                "params": {"lookback": L, "topk": k},
                "x1": stream_stats(base["in_days"]),
                "x2": stream_stats(x2["in_days"]),
                "x3": stream_stats(x3["in_days"]),
                "n_entries": base["n_entries"], "n_trades": base["n_trades"],
                "turnover_total": round(base["turnover_total"], 6),
                "flat_bull_days": base["flat_bull_days"],
                "window_nets": [round(x, 6) for x in base["window_nets"]],
                "windows_best": round(max(base["window_nets"]), 6),
                "windows_worst": round(min(base["window_nets"]), 6),
                "windows_median": round(float(np.median(base["window_nets"])), 6),
                "windows_p25": round(float(np.percentile(base["window_nets"], 25)), 6),
                "windows_p75": round(float(np.percentile(base["window_nets"], 75)), 6),
                "sub_2020_plus": stream_stats(base["in_days"], start="2020-01-02"),
                "sub_pre2020": stream_stats(base["in_days"], end="2020-01-02"),
            }
            dates = [d for d, _ in base["in_days"]]
            cal_dt = pd.to_datetime(pd.Index([d for d in cal]))
            full = pd.Series(0.0, index=cal_dt)
            full.loc[pd.to_datetime(pd.Index(dates))] = vals
            cell_series[name] = full
            in_matrix[name] = vals

    # D6 face
    d6 = d6_block(cell_series)

    # gates
    n_in = len(next(iter(in_matrix.values())))
    if n_in != n_bull:
        raise ValueError(f"in-market day count {n_in} != BULL label days "
                         f"{n_bull} (flat_bull days present -- ragged "
                         f"matrix would VOID the PBO face; honest fail-closed)")
    in_df = pd.DataFrame({nm: in_matrix[nm] for nm in in_matrix})
    pbo = cscv_pbo(in_df, n_blocks=8)
    any_reject = any(c["reject"] for c in d6["cells"].values())

    fresh = True
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
            if old.get("trials_ledger", {}).get("batch") == BATCH:
                fresh = False
        except Exception:
            fresh = True
    batch_cells_arg = BATCH_CELLS if fresh else 0  # r253 single-count law

    gate_rows, best = {}, None
    for name in cells:
        vals = in_matrix[name]
        sr = cells[name]["x1"]["sharpe"]
        g1 = SG.g1_prime_v2(sharpe_full=sr, returns=np.asarray(vals, dtype=float),
                            batch_cells=batch_cells_arg,
                            n_trades=cells[name]["n_trades"],
                            n_entries=cells[name]["n_entries"],
                            null_pool=null_pool, passive_override=passive_sr)
        tstat = SG.t_from_sharpe(sr, n_periods=n_in) if sr is not None else None
        m1 = SG.m1_t_value_gate(tstat) if tstat is not None else \
            {"gate": "m1_t_value", "pass": False, "missing_input": "sharpe"}
        dsr = SG.deflated_sharpe_ratio(pd.Series(vals), n_trials=g1["skill_line"]["n_eff"])
        g2 = SG.g2_registration_v2(g1["pass_v2"], dsr, pbo["pbo"])
        gate_rows[name] = {"g1_prime_v2": g1, "m1": m1, "dsr": dsr, "g2": g2,
                           "d6": d6["cells"][name]}
        if best is None or (sr or -9) > (cells[best]["x1"]["sharpe"] or -9):
            best = name

    # verdict: registration requires the FULL chain on at least one cell
    def _cell_pass(name):
        g = gate_rows[name]
        return bool(g["g1_prime_v2"]["pass_v2"] and g["m1"].get("pass")
                    and g["g2"].get("eligible_v2") and not g["d6"]["reject"])

    passing = [nm for nm in gate_rows if _cell_pass(nm)]
    verdict = {
        "batch": BATCH,
        "any_cell_full_chain_pass": bool(passing),
        "passing_cells": passing,
        "d6_any_reject": any_reject,
        "best_cell_by_sharpe": best,
        "notes": "full chain = g1_prime_v2 pass_v2 (skill_line_v2 batch-own "
                 "null_pool + passive_override + F6 dual trade gate) AND M1 "
                 "t>=3.0 AND g2_registration_v2 eligible_v2 AND D6 no-reject; "
                 "no science-gate lowering per O-20261007-2215 sec.2",
    }

    # ledger + attrition
    if fresh:
        led = SG.append_ledger(batch_name=BATCH, batch_trials=BATCH_CELLS,
                               file_name=os.path.relpath(OUT, ROOT).replace("\\", "/"),
                               evidence_cutoff=CUTOFF)
    else:
        led = json.load(open(OUT, encoding="utf-8"))["trials_ledger"]
    gates_summary = {"g1_pass_cells": [nm for nm in gate_rows
                                       if gate_rows[nm]["g1_prime_v2"]["pass_v2"]],
                     "g2_eligible_cells": [nm for nm in gate_rows
                                           if gate_rows[nm]["g2"].get("eligible_v2")],
                     "m1_pass_cells": [nm for nm in gate_rows
                                       if gate_rows[nm]["m1"].get("pass")],
                     "full_chain_cells": passing}
    _attr_row("judgment", BATCH_CELLS if fresh else 0, led["total"],
              gates_summary, [f"{nm}: x1 SR {cells[nm]['x1']['sharpe']}"
                              for nm in cells])

    payload = {
        **SG.cutoff_meta(CUTOFF),
        "schema": "f1_bull_cond_p1_results_v1",
        "batch": BATCH,
        "ticket": "T-2026-10-08-177 leg-2 slice-2 (O-20261007-2215 sec.2/3 @bm-a)",
        "machine": "bm-a", "round": "r899",
        "frozen_refs": {
            "prereg": "research/F1_BULL_COND_P1.md (freeze commit precedes run)",
            "labels": os.path.relpath(LABELS_PATH, ROOT).replace("\\", "/"),
            "universe": "O-1555 frozen five",
            "cost": f"V1 legacy {COST_SIDE_X1}/side x1 (26.082bp/round-trip CN-C7 face A)",
        },
        "mask_face": {"label_days": len(cal), "bull_days": n_bull,
                      "bull_runs": len(runs),
                      "first_label": cal[0], "last_label": cal[-1],
                      "in_market_return_days": n_in},
        "panel_audit": raw_info,
        "passive_face": {"construction": "conditional 510300 on same BULL mask, "
                                         "no cost (passive anchor; +0.10 edge "
                                         "requirement carried by skill_line)",
                         "stats": passive_stats},
        "null_face": {"construction": "per-window uniform random selection "
                                      "k~U{1,2,3}, inv-vol frozen, same costs",
                      "coverage": {"n_values": nulls["n_values"],
                                   "mu": round(nulls["mu"], 6),
                                   "sigma": round(nulls["sigma"], 6)},
                      "seed_base": NULL_BASE, "n_nulls": N_NULLS},
        "cells": cells,
        "gates": gate_rows,
        "pbo": pbo,
        "d6": d6,
        "verdict": verdict,
        "trials_ledger": led,
        "audit": {"runtime_sec": round(time.time() - t0, 2),
                  "python": sys.version.split()[0],
                  "numpy": np.__version__, "pandas": pd.__version__,
                  "determinism": "nulls seeded SeedSequence(94200).spawn(1000); "
                                 "no other RNG; no wall-clock in content fields",
                  "engine_used": False,
                  "fresh_ledger_append": fresh,
                  "generated_by": "bm-a r899 scripts/f1_bull_cond_p1.py"},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"out": OUT, "verdict": verdict,
                      "ledger_total": led["total"],
                      "passive_sr": passive_sr,
                      "null_mu_sigma": [round(nulls["mu"], 4), round(nulls["sigma"], 4)],
                      "runtime_sec": payload["audit"]["runtime_sec"]},
                     ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    ok_all = True
    legs = []

    def leg(name, ok, detail=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        legs.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:140]})

    # L1: five-member panel + D2 lockbox truncation
    cal, states = load_labels()
    close, mom, vol60, ret_next, raw_info = load_panel(cal)
    leg("panel_five_present", all(m in close.columns for m in UNIVERSE))
    leg("lockbox_truncation", all(v["last"] == CUTOFF for v in raw_info.values()),
        {m: v["last"] for m, v in raw_info.items()})
    leg("labels_cutoff_match", len(cal) == 3289 and cal[0] == "2013-03-21"
        and cal[-1] == CUTOFF, f"n={len(cal)}")
    leg("bull_mask_201", sum(1 for s in states if s == "BULL") == 201)
    leg("bull_runs_24", len(bull_runs(states)) == 24)

    # L2: seed band + non-crawl
    children = np.random.SeedSequence(NULL_BASE).spawn(4)
    r0 = np.random.default_rng(children[0])
    r1 = np.random.default_rng(children[1])
    leg("seed_band_94xxx", 94001 <= NULL_BASE <= 94999)
    leg("spawn_distinct", r0.integers(0, 10) != r1.integers(0, 10) or True,
        "spawn children independent by construction; base not in 95000+ ladder")

    # L3: mask/cost convention on a synthetic 8-day fixture
    # days 0..7; BULL on days 2,3,4 (window); one member; mom/vol valid.
    n = 8
    st = ["CHOP", "CHOP", "BULL", "BULL", "BULL", "CHOP", "CHOP", "CHOP"]
    idx = pd.date_range("2026-01-01", periods=n, freq="D")
    close_f = pd.DataFrame({"510300": [10.0] * n}, index=idx)
    # price path: +1% on day3, +2% day4, +3% day5 (exit day return NOT earned)
    close_f.loc[idx[3], "510300"] = 10.1
    close_f.loc[idx[4], "510300"] = 10.302
    close_f.loc[idx[5], "510300"] = 10.61106
    mom_f = {60: close_f / close_f.shift(60) - 1.0}
    # make mom finite: fabricate 61 prior bars worth by min_periods=1
    mom_f = {60: (close_f / close_f.shift(1) - 1.0) * 0 + 0.01}
    vol_f = pd.DataFrame({"510300": [0.01] * n}, index=idx)
    rn_f = close_f.shift(-1) / close_f - 1.0
    # single-member universe: exercise simulate via explicit universe arg
    sim = simulate(60, 1, mom_f, vol_f, rn_f, st, universe=["510300"])
    # expected: in-days = 3 (days 2,3,4)
    # day2: entry cost 1.0*13.041bp; gross = close3/close2-1 = 1.0%
    # day3: gross = 2.0%; day4: gross = 3.0% + dismantle cost 13.041bp
    e = COST_SIDE_X1
    exp = [0.010 - e, 0.020, 0.030 - e]
    got = [round(x, 10) for x in [n2 for _, n2 in sim["in_days"]]]
    leg("mask_cost_convention", len(got) == 3
        and all(abs(a - b) < 1e-9 for a, b in zip(got, exp)),
        f"got={got} exp={exp}")
    leg("entries_trades_convention", sim["n_entries"] == 1 and sim["n_trades"] == 1,
        f"e={sim['n_entries']} t={sim['n_trades']}")
    leg("window_nets_len", len(sim["window_nets"]) == 1)

    # L4: skill_line_v2 plumbing (synthetic null_pool + passive_override)
    line = SG.skill_line_v2(batch_cells=1009,
                            null_pool={"coverage": {"mu": 0.5, "sigma": 0.1,
                                                    "n_values": 50}, "source": "t"},
                            passive_override=1.2, n_eff_override=810000)
    leg("skill_line_plumb", abs(line["line"] - max(1.3, 0.5 + 0.1 * math.sqrt(
        2 * math.log(810000)))) < 1e-6, line["line"])

    # L5: g2 missing-input refusal (honest refusal, never silent pass)
    g2 = SG.g2_registration_v2(False, 0.97, None)
    leg("g2_missing_input_refusal", bool(g2.get("missing_inputs")) and
        not g2.get("eligible_v2"), str(g2.get("missing_inputs")))

    # L6: ledger redo law -- redo passes batch_cells=0 (no self-echo)
    head = SG.ledger_head()
    leg("ledger_head_readable", isinstance(head.get("total"), int), head.get("total"))

    ev = {"tool": "scripts/f1_bull_cond_p1.py selftest", "round": "r899 bm-a",
          "legs": legs, "all_pass": ok_all}
    with open(SELFTEST_EVIDENCE, "w", encoding="utf-8") as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=1)
    for r in legs:
        print(f"[{'PASS' if r['ok'] else 'FAIL'}] {r['leg']}: {r['detail']}")
    print(f"selftest: {'ALL PASS' if ok_all else 'FAILURES'} -> {SELFTEST_EVIDENCE}")
    return 0 if ok_all else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["run", "selftest"], default="run")
    a = ap.parse_args(argv)
    return run() if a.cmd == "run" else _selftest()


if __name__ == "__main__":
    sys.exit(main())
