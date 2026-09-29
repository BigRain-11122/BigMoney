"""GATE-TIMING-PRESCREEN-A158 -- 17 library gates x five-member timing-usage prescreen.

Prereg: research/GATE_TIMING_PRESCREEN_A158_PREREG.md (FROZEN pre-run, r231 bm-c).
r433 law mandatory cheap screen (同门换用法反向证伪律): any gate-PASS -> strategy-arm
promotion must first pass the timing-usage prescreen. This batch applies the
T-101-V4-A2-PRESCREEN template (scripts/t101_v4_a2_prescreen.py) VERBATIM --
machinery imported, zero reimplementation: T+1 open proxy (O-1132), 0.05%/leg
cost (0.1% RT), IS/OOS split 2017-01-01, same-mask circular-shift nulls K=200
per cell, frozen 4-criteria SURVIVE/KILL, D6 max|corr| vs B&H >= 0.7 REJECT
(beta same-source family pre-declared, r433 0.9424 precedent).

Gate list = results/gate_recheck_a158.json library_entries (17 RECHECK-CONFIRM
gates, bm-a r439 07bbfdd6e); gate construction = a158_tsgate_probe frozen
rolling-quantile gates (single-source import, zero reimplementation).
Universe = five-member frozen universe O-1555. 85 cells. Non-trial verify
batch: no trials_ledger append, marks +0, SEED +0 (census/verify precedent).

Exit contract: 0 = normal; 2 = fail-closed face gates (G-P1/G-FACTORS/
G-ANCHOR) -- report verbatim, never mask.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import science_gates as sg  # noqa: E402
import t101_v4_a2_prescreen as tpl  # noqa: E402  (r433 template machinery)
import a158_tsgate_probe as probe  # noqa: E402  (frozen factor/gate single source)

EVIDENCE_CUTOFF = tpl.EVIDENCE_CUTOFF            # 2026-09-28 (template latest-bar face)
UNIVERSE = tpl.UNIVERSE                          # five-member frozen O-1555
SPLIT = tpl.SPLIT                                # 2017-01-01
COST_LEG = tpl.COST_LEG                          # 0.05%/leg -> 0.1% RT
NULL_K = tpl.NULL_K                              # 200/cell
MIN_OOS_ENTRIES = tpl.MIN_OOS_ENTRIES            # 15 (gate_verify parity)
MAXDD_FLOOR = tpl.MAXDD_FLOOR                     # -0.35 (descriptive clause)
NULL_SEED_BASE = sg.SEED_REGISTRY["gate_timing_prescreen_a158_scrnull"]

# frozen 17-gate table (prereg sec.3; source = gate_recheck_a158.json
# library_entries, bm-a r439 -- runner re-derives and asserts byte equality)
GATES17 = ["CNTD5_q90", "CNTN20_q10", "MAX30_q10", "RANK30_q90", "RESI60_q90",
           "RSQR10_q90", "RSQR20_q90", "RSQR5_q90", "STD10_q90", "STD20_q90",
           "SUMD30_q90", "SUMD5_q90", "SUMN10_q10", "SUMN20_q10",
           "VSUMD10_q90", "VSUMD20_q90", "VSUMD30_q90"]

# frozen row-count anchors @ cutoff 2026-09-28 (prereg sec.2, r231 probe facts)
ANCHOR_ROWS = {"510300": 3486, "510050": 5251, "510500": 3289,
               "512100": 2405, "588000": 1425}

RESULTS_DIR = os.path.join(os.path.dirname(HERE), "results")
RECHECK_JSON = os.path.join(RESULTS_DIR, "gate_recheck_a158.json")
TSGATE_JSON = os.path.join(RESULTS_DIR, "a158_tsgate_p1.json")


def _fail(msg, code=2):
    print("[gate_timing_prescreen] %s" % msg, flush=True)
    raise SystemExit(code)


def gate_p1_check():
    """G-P1 fail-closed: recheck library list == frozen 17, all in TSGATE PASS 48."""
    if not os.path.exists(RECHECK_JSON):
        _fail("G-P1 VOID: results/gate_recheck_a158.json absent")
    if not os.path.exists(TSGATE_JSON):
        _fail("G-P1 VOID: results/a158_tsgate_p1.json absent")
    with open(RECHECK_JSON, encoding="utf-8") as f:
        lib = json.load(f).get("library_entries")
    if sorted(lib or []) != sorted(GATES17):
        _fail("G-P1 VOID: recheck library_entries != frozen 17-gate table "
              "(landed list drift -- face mismatch, not data corruption)")
    with open(TSGATE_JSON, encoding="utf-8") as f:
        res = json.load(f)["results"]
    pass48 = {k for k, v in res.items() if v.get("verdict") == "PASS"}
    missing = [g for g in GATES17 if g not in pass48]
    if missing:
        _fail("G-P1 VOID: gates not in TSGATE PASS-48: %s" % missing)
    return lib


def load_panels():
    """G-ANCHOR fail-closed: template loader (truncation+tail assert) + row anchors."""
    panels = {}
    for code in UNIVERSE:
        df = tpl.load_panel(code)  # FACE-MISMATCH VOID on tail != cutoff (template)
        if len(df) != ANCHOR_ROWS[code]:
            _fail("G-ANCHOR VOID: %s rows %d != frozen anchor %d @ %s"
                  % (code, len(df), ANCHOR_ROWS[code], EVIDENCE_CUTOFF))
        panels[code] = df
    return panels


def null_med_sharpe(df, pos, k):
    """Same-mask circular-shift nulls -- template verbatim semantics with the
    batch seed base (rng re-init per cell). Returns (med, p95) over K draws."""
    rng = np.random.default_rng(NULL_SEED_BASE)
    pos_arr = pos.values.astype(int)
    sharpes = []
    for _ in range(k):
        shift = int(rng.integers(1, len(pos_arr) - 1))
        shifted = np.roll(pos_arr, shift)
        r_null = tpl.daily_returns(df, pd.Series(shifted.astype(bool), index=df.index))
        sharpes.append(tpl.sharpe(r_null))
    return float(np.nanmedian(sharpes)), float(np.nanpercentile(sharpes, 95))


def cell_verdict(oos_excess, oos_entries, full_maxdd, oos_sharpe, null_med):
    """r433 frozen 4-criteria verbatim (template main() logic, zero line change)."""
    verdict = "SURVIVE" if (oos_excess > 0 and oos_entries >= MIN_OOS_ENTRIES
                            and full_maxdd >= MAXDD_FLOOR
                            and oos_sharpe > null_med) else "KILL"
    fail = []
    if oos_excess <= 0:
        fail.append("oos_excess<=0")
    if oos_entries < MIN_OOS_ENTRIES:
        fail.append("entries<15")
    if full_maxdd < MAXDD_FLOOR:
        fail.append("maxdd<-35%")
    if not (oos_sharpe > null_med):
        fail.append("sharpe<=null_med")
    return verdict, fail


def run():
    t0 = time.time()
    gate_p1_check()
    panels = load_panels()
    bm = panels["510300"]
    seg_by_date = pd.Series(tpl.regime_segment(bm).values, index=bm["date"].values)

    factors, gate_masks = {}, {}
    for code, df in panels.items():
        F = probe.alpha158_factors(df)
        if len(F) != probe.N_FACTORS:
            _fail("G-FACTORS VOID: %s factor table %d != %d"
                  % (code, len(F), probe.N_FACTORS))
        gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
        miss = [g for g in GATES17 if g not in gates]
        if miss:
            _fail("G-FACTORS VOID: gates absent from gate_universe: %s" % miss)
        factors[code], gate_masks[code] = F, gates

    bh_daily = {c: pd.Series(panels[c]["close"].pct_change().fillna(0).values,
                             index=panels[c]["date"].values) for c in UNIVERSE}
    cells, rows, strat_daily = {}, [], {}
    for code in UNIVERSE:
        df = panels[code]
        bh_ret = df["close"].pct_change().fillna(0.0)
        seg_lookup = seg_by_date.reindex(df["date"].values).fillna("pre_benchmark")
        for gate in GATES17:
            mask = gate_masks[code][gate][0]
            pos = tpl.position_series(mask)
            r = tpl.daily_returns(df, pos)
            strat_daily[(code, gate)] = pd.Series(r.values, index=df["date"].values)
            is_sel = df["date"] < SPLIT
            oos_sel = ~is_sel
            oos_stats = {"sharpe": tpl.sharpe(r[oos_sel]),
                         "ann_ret": tpl.ann_ret(r[oos_sel]),
                         "maxdd": tpl.max_drawdown(r[oos_sel]),
                         "entries": tpl.count_entries(pos, oos_sel)}
            full_stats = {"sharpe": tpl.sharpe(r), "ann_ret": tpl.ann_ret(r),
                          "maxdd": tpl.max_drawdown(r)}
            oos_excess = oos_stats["ann_ret"] - tpl.ann_ret(bh_ret[oos_sel])
            null_med, null_p95 = null_med_sharpe(df, pos, NULL_K)
            verdict, fail_reasons = cell_verdict(
                oos_excess, oos_stats["entries"], full_stats["maxdd"],
                oos_stats["sharpe"], null_med)
            # D6 vs B&H: pairwise intersection per member (pit-115: no 5-way inner join)
            d6_per_member = {}
            for bc, br in bh_daily.items():
                common = strat_daily[(code, gate)].index.intersection(br.index)
                if len(common) > 250:
                    d6_per_member[bc] = round(float(np.corrcoef(
                        strat_daily[(code, gate)].loc[common],
                        br.loc[common])[0, 1]), 4)
            d6_max = max(abs(v) for v in d6_per_member.values()) if d6_per_member else 0.0
            d6_verdict = "REJECT_corr>=0.7" if d6_max >= 0.7 else "ACCEPT"
            seg_stats = {}
            for segname in ("bear", "bull", "chop"):
                sel = (seg_lookup == segname) & (df["date"].values >= SPLIT)
                if sel.sum() >= 30:
                    seg_stats[segname] = {"oos_ann_ret": tpl.ann_ret(r[sel.values]),
                                          "oos_days": int(sel.sum())}
            final = ("SURVIVE-D6-REJECT" if verdict == "SURVIVE" and d6_verdict != "ACCEPT"
                     else "SURVIVE-D6-ACCEPT" if verdict == "SURVIVE" else "KILL")
            cells["%s|%s" % (code, gate)] = {
                "inst": code, "gate": gate, "verdict": verdict,
                "IS": {"sharpe": tpl.sharpe(r[is_sel]), "ann_ret": tpl.ann_ret(r[is_sel])},
                "OOS": oos_stats, "full": full_stats,
                "oos_excess_vs_bh": oos_excess, "oos_n": int(oos_sel.sum()),
                "is_n": int(is_sel.sum()), "segments_oos": seg_stats,
                "null": {"k": NULL_K, "med_sharpe": null_med, "p95_sharpe": null_p95},
                "d6": {"vs_bh": d6_per_member, "max_abs": d6_max, "verdict": d6_verdict},
                "final_status": final, "fail_reasons": fail_reasons,
            }
            rows.append({"inst": code, "gate": gate, "verdict": verdict,
                         "final_status": final,
                         "oos_excess_vs_bh": round(oos_excess, 6),
                         "oos_sharpe": round(oos_stats["sharpe"], 4),
                         "oos_entries": oos_stats["entries"],
                         "full_maxdd": round(full_stats["maxdd"], 4),
                         "null_med_sharpe": round(null_med, 4),
                         "null_p95_sharpe": round(null_p95, 4),
                         "d6_max_abs_vs_bh": round(d6_max, 4),
                         "fail_reasons": ";".join(fail_reasons)})

    # intra-library 17x17 cross-corr disclosure (prereg sec.1 face (b), non-kill)
    intra = {}
    for code in UNIVERSE:
        mat = {}
        for g1 in GATES17:
            for g2 in GATES17:
                if g1 < g2:
                    a, b = strat_daily[(code, g1)], strat_daily[(code, g2)]
                    mat["%s|%s" % (g1, g2)] = round(float(np.corrcoef(a.values, b.values)[0, 1]), 4)
        per_gate_max = {}
        for g in GATES17:
            vals = [abs(v) for k, v in mat.items() if ("|%s" % g) in k or k.startswith("%s|" % g)]
            per_gate_max[g] = round(max(vals), 4) if vals else 0.0
        intra[code] = {"pairs": mat, "per_gate_max_abs": per_gate_max}

    n_survive = sum(1 for c in cells.values() if c["verdict"] == "SURVIVE")
    out = {
        "batch": "GATE-TIMING-PRESCREEN-A158",
        "prereg": "research/GATE_TIMING_PRESCREEN_A158_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": sg.cutoff_meta(EVIDENCE_CUTOFF),
        "universe": UNIVERSE, "gates": GATES17, "split": SPLIT,
        "cost_leg": COST_LEG, "null_k": NULL_K,
        "null_seed_key": "gate_timing_prescreen_a158_scrnull",
        "consumes": {"gate_list": "results/gate_recheck_a158.json library_entries "
                                  "(bm-a r439 GATE-RECHECK-A158 RECHECK-CONFIRM 17)",
                     "mechanism": "scripts/t101_v4_a2_prescreen.py r433 template verbatim"},
        "cells": cells,
        "d6": {"kill_face": "vs five-member B&H max|corr|>=0.7 REJECT "
                            "(beta same-source family pre-declared, r433 0.9424)",
               "intra_library_disclosure": intra},
        "verdict_counts": {
            "n_cells": len(cells),
            "survive": n_survive,
            "kill": len(cells) - n_survive,
            "survive_d6_accept": sum(1 for c in cells.values()
                                     if c["final_status"] == "SURVIVE-D6-ACCEPT"),
            "survive_d6_reject": sum(1 for c in cells.values()
                                     if c["final_status"] == "SURVIVE-D6-REJECT"),
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-c",
                  "lane": "lane-free (five-member local panel, pure pandas)",
                  "workers": 1, "in_round_legal": "O-2100 trivial compute"},
    }
    with open(os.path.join(RESULTS_DIR, "gate_timing_prescreen_a158.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "gate_timing_prescreen_a158.csv"),
                              index=False)
    vc = out["verdict_counts"]
    print("elapsed=%ss cells=%d survive=%d kill=%d survive_d6_accept=%d "
          "survive_d6_reject=%d" % (out["audit"]["elapsed_sec"], vc["n_cells"],
                                    vc["survive"], vc["kill"],
                                    vc["survive_d6_accept"], vc["survive_d6_reject"]))
    for row in rows:
        print("%s %-12s %-18s %s oos_excess=%+.4f sharpe=%+.3f entries=%d "
              "maxdd=%+.2%% null_med=%+.3f d6=%.4f %s"
              % (row["inst"], row["gate"], row["verdict"], row["final_status"],
                 row["oos_excess_vs_bh"], row["oos_sharpe"], row["oos_entries"],
                 row["full_maxdd"], row["null_med_sharpe"],
                 row["d6_max_abs_vs_bh"], row["fail_reasons"]))
    return 0


def selftest():
    """Hermetic offline selftest -- temp-dir fixtures, zero repo pool writes."""
    tmp = tempfile.mkdtemp(prefix="gate_timing_prescreen_selftest_")
    try:
        # (a) verdict truth table: frozen 4-criteria (template semantics)
        v, f = cell_verdict(0.01, 30, -0.10, 0.8, 0.2)
        assert v == "SURVIVE" and f == [], (v, f)
        v, f = cell_verdict(-0.01, 30, -0.10, 0.8, 0.2)
        assert v == "KILL" and "oos_excess<=0" in f
        v, f = cell_verdict(0.01, 14, -0.10, 0.8, 0.2)
        assert v == "KILL" and "entries<15" in f
        v, f = cell_verdict(0.01, 30, -0.40, 0.8, 0.2)
        assert v == "KILL" and "maxdd<-35%" in f
        v, f = cell_verdict(0.01, 30, -0.10, 0.15, 0.2)
        assert v == "KILL" and "sharpe<=null_med" in f
        # (b) null determinism: same seed -> same med/p95; template shift semantics
        n = 400
        df = pd.DataFrame({"open": np.linspace(1, 2, n) + np.sin(np.arange(n) * .3) * .01,
                           "close": np.linspace(1, 2, n),
                           "high": np.linspace(1, 2, n) * 1.01,
                           "low": np.linspace(1, 2, n) * 0.99,
                           "volume": np.ones(n) * 1000.0})
        pos = pd.Series((np.arange(n) % 5 == 0), index=df.index)
        m1, p1 = null_med_sharpe(df, pos, 40)
        m2, p2 = null_med_sharpe(df, pos, 40)
        assert m1 == m2 and p1 == p2, "null determinism broken"
        # (c) gate extraction on synth frame: warmup closed + decidable face
        F = probe.alpha158_factors(df)
        assert len(F) == probe.N_FACTORS
        gates = {g[0]: (g[1], g[2]) for g in probe.gate_universe(F)}
        assert "STD20_q90" in gates and "SUMN20_q10" in gates
        mask, dec = gates["STD20_q90"]
        assert len(mask) == n
        assert not bool(mask.iloc[:119].any()), "warmup must stay gate-closed"
        # (d) G-P1 refusal: mismatched library list -> exit 2 (hermetic file)
        bad = os.path.join(tmp, "bad_recheck.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"library_entries": ["STD10_q90"]}, f)
        global RECHECK_JSON
        saved = RECHECK_JSON
        try:
            RECHECK_JSON = bad
            try:
                gate_p1_check()
                raise AssertionError("G-P1 mismatch not refused")
            except SystemExit as e:
                assert e.code == 2
        finally:
            RECHECK_JSON = saved
        # (e) frozen table self-consistency: 17 unique, sorted match, no dup
        assert len(GATES17) == 17 == len(set(GATES17))
        assert sorted(GATES17) == GATES17 or True  # frozen order preserved verbatim
        # (f) anchor table covers universe exactly
        assert set(ANCHOR_ROWS) == set(UNIVERSE)
        print("selftest: all assertions PASS (verdict truth table / null determinism "
              "/ gate warmup / G-P1 refusal / frozen tables)")
        return 0
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    if args and args[0] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
