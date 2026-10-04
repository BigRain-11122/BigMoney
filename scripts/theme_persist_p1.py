"""THEME_PERSIST_P1 runner -- theme-ring R4 judgment-question face.

Prereg (FROZEN v1.0, bm-a r657, freeze commit on origin/main):
research/THEME_PERSIST_P1.md. CEO order lineage: O-20261001-2103 R4
(persistence prediction gate) + O-20261001-2106 (measured readings only).

Face A = persistence separation tests on the FROZEN v0.2 wave table
  (43 waves, 5 decision-time features x 3 outcomes, wave-level label
  permutation K=2000 + theme-cluster bootstrap reference, Bonferroni
  n=5 within each outcome; zero thresholds fitted).

Face B = mechanical wave-ride system per theme proxy over its 750td
  ignition window (entry = ignition+1 close, break exit = close <=
  0.80*running peak with T+1 close execution, rebirth re-entry = close
  >= 1.25*trough within 250td of the exit bar, T+1 close execution),
  x1/x2 costs, vs same-window B&H, vs K=200 random-ignition pooled
  nulls (one random start per theme per replication, window length
  matched), LOO 16 folds, ignition-date terciles (6/5/5), regime
  segments, +-structural sensitivity variants.

Exploration-labeled: zero registration / zero paper claims (G2_SLOT_MON_P1
precedent). Exit axis = 1 (strategy's own exit; engine/exit_rules.py not
involved -- standalone L1 daily-close simulator).

Determinism: zero wall-clock fields in the batch payload (audit block
carries elapsed seconds only). Selftest = hermetic synthetic mechanics +
sha16/seed/cost/grammar gates + double-run byte identity (mini pipeline).

Usage: run | selftest
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as sg  # noqa: E402
from rev_osc_stock_p1 import COST_X1  # noqa: E402
from theme_event_library import (  # noqa: E402
    EVENTS, MINUS20_LINE, PEAK_SEARCH_TD, load_series,
)
from theme_wave_segmentation import (  # noqa: E402
    CLASS_LONG_MIN_TD, CLASS_PULSE_MAX_TD, REBOUND_MIN, REBOUND_SEARCH_TD,
)

BATCH = "THEME_PERSIST_P1"
PREREG = "research/THEME_PERSIST_P1.md"
CUTOFF = "2026-09-30"
WAVES_JSON = os.path.join(ROOT, "results", "theme_ring",
                          "theme_events_v02_waves.json")
WAVES_SHA16 = "aa9bb8488eeb4d06"          # freeze-window probe fact
SEED_NULLS = 20580000                     # science_gates.SEED_REGISTRY
K_PERM = 2000
K_NULLS = 200
LEDGER_PATH = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
OUT_DIR = os.path.join(ROOT, "results", "theme_persist_p1")
OUT_JSON = os.path.join(OUT_DIR, "theme_persist_p1.json")
OUT_D6 = os.path.join(OUT_DIR, "d6_numeric.json")
OUT_FACA = os.path.join(OUT_DIR, "faceA_permutation.csv")
OUT_FACB = os.path.join(OUT_DIR, "faceB_by_theme.csv")
OUT_NULLS = os.path.join(OUT_DIR, "nulls_pooled.csv")
BUDGET_SEC = 300                          # O-1901 (a)-1 item iii cap

# substream map (rng([SEED_NULLS, k]) substream law, frozen at prereg):
#   k in [0, 200)      -> null replication k
#   k in [1000, 1015)  -> face A permutation stream (test index 0..14)
#   k in [2000, 2015)  -> face A theme-cluster bootstrap stream
SUB_NULL, SUB_PERM, SUB_CLUST = 0, 1000, 2000

FEATURES = ["early20_ret", "overseas_20d", "breadth_at_20", "seq",
            "anchor_is_prior"]
OUTCOMES = ["dur_rank", "is_pulse", "is_long"]
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")


def _sha16_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def _rng(k):
    return np.random.default_rng([SEED_NULLS, k])


# ---------------------------------------------------------------- face A
# Rank-based statistics. Under label permutation the feature rank vector
# rx is FIXED; permuting a continuous outcome permutes its rank vector,
# permuting a binary outcome re-slices rx over a random positive subset.
# Both give the exact same null distributions as recomputing from raw
# values (multiset invariance of ranks) at a fraction of the cost.

def _corr(rx, ry):
    sx, sy = np.std(rx), np.std(ry)
    if sx == 0 or sy == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _auc_from_ranks(rx, y):
    """AUC of feature x for binary outcome y from x's rank vector."""
    y = np.asarray(y, dtype=int)
    npos, nneg = int(y.sum()), int(len(y) - y.sum())
    if npos == 0 or nneg == 0:
        return 0.5
    u = float(rx[y == 1].sum()) - npos * (npos + 1) / 2.0
    return u / (npos * nneg)


def face_a(waves):
    rows = []
    dur = np.array([w["dur_to_peak_td"] for w in waves], dtype=float)
    pulse = np.array([1 if w["wave_class"] == "pulse" else 0 for w in waves])
    long_ = np.array([1 if w["wave_class"] == "long" else 0 for w in waves])
    theme_ids = [w["theme_id"] for w in waves]
    uniq = sorted(set(theme_ids))
    by_theme = {t: [i for i, tt in enumerate(theme_ids) if tt == t]
                for t in uniq}
    ry_dur = pd.Series(dur).rank().values
    for fi, feat in enumerate(FEATURES):
        x = np.array(
            [w["seq"] if feat == "seq" else
             (1.0 if w["anchor"] == "prior" else 0.0)
             if feat == "anchor_is_prior" else float(w[feat])
             for w in waves], dtype=float)
        rx = pd.Series(x).rank().values
        for oi, out in enumerate(OUTCOMES):
            if out == "dur_rank":
                obs = _corr(rx, ry_dur)
            else:
                yv = pulse if out == "is_pulse" else long_
                obs = _auc_from_ranks(rx, yv)
                npos = int(yv.sum())
            ti = oi * len(FEATURES) + fi
            rng = _rng(SUB_PERM + ti)
            ge = 0
            for _ in range(K_PERM):
                if out == "dur_rank":
                    s = _corr(rx, ry_dur[rng.permutation(len(dur))])
                else:
                    sub = rng.choice(len(dur), size=npos, replace=False)
                    yv2 = np.zeros(len(dur), dtype=int)
                    yv2[sub] = 1
                    s = _auc_from_ranks(rx, yv2)
                if abs(s) >= abs(obs):
                    ge += 1
            p_perm = (1 + ge) / (K_PERM + 1)
            # theme-cluster bootstrap reference (16-theme resample)
            rng = _rng(SUB_CLUST + ti)
            ge_c = 0
            for _ in range(K_PERM):
                pick = rng.choice(len(uniq), size=len(uniq), replace=True)
                idx = np.concatenate([by_theme[uniq[p]] for p in pick])
                rxi, ryd = rx[idx], ry_dur[idx]
                if out == "dur_rank":
                    s = _corr(rxi, ryd)
                else:
                    yv = pulse if out == "is_pulse" else long_
                    s = _auc_from_ranks(rxi, yv[idx])
                if np.std(rxi) == 0:
                    continue
                if abs(s) >= abs(obs):
                    ge_c += 1
            p_clust = (1 + ge_c) / (K_PERM + 1)
            rows.append(dict(feature=feat, outcome=out, stat=obs,
                             p_perm=p_perm, p_cluster=p_clust,
                             bonf_significant=bool(p_perm < 0.05 / 5)))
    return rows


# ---------------------------------------------------------------- face B

def simulate(closes, break_line=MINUS20_LINE, rebirth=REBOUND_MIN,
             rebirth_win=REBOUND_SEARCH_TD, cost=COST_X1):
    """Mechanical wave-ride on one window. closes[0] = ignition bar.

    Entry: close of bar 1 (ignition+1, T+1 conservative proxy), pay cost.
    Exit : while holding, peak = running max close; close[i] <=
           peak*break_line triggers exit at close[i+1] (T+1, pay cost).
           Break on the last bar: hold to end (valued at last close,
           no exit cost -- B&H gets identical treatment).
    Re-entry: while flat, trough = min close since the exit bar; when
           close[m] >= trough*rebirth for m <= exit_bar + rebirth_win,
           re-enter at close[m+1]. No rebirth within the deadline =
           theme dead, flat to window end.
    """
    n = len(closes)
    eq = [1.0] * n
    pos = False
    peak = None
    trough = None
    deadline = None
    pending_entry = 1
    trades = []
    i = 1
    while i < n:
        px = closes[i]
        if pos:
            peak = max(peak, px)
            eq[i] = eq[i - 1] * (px / closes[i - 1])
            if px <= peak * break_line and i + 1 < n:
                j = i + 1
                eq[j] = eq[i] * (closes[j] / px) * (1 - cost)
                trades.append((j, "sell", closes[j]))
                pos = False
                peak = None
                trough = closes[j]
                deadline = j + rebirth_win
                i = j + 1
                continue
            i += 1
            continue
        eq[i] = eq[i - 1]
        if pending_entry is not None and i == pending_entry:
            eq[i] = eq[i - 1] * (1 - cost)
            pos = True
            peak = px
            trades.append((i, "buy", px))
            pending_entry = None
            i += 1
            continue
        if trough is not None and deadline is not None:
            if i > deadline:
                trough = None
                deadline = None
            else:
                trough = min(trough, px)
                if px >= trough * rebirth and i + 1 < n:
                    pending_entry = i + 1
                    trough = None
                    deadline = None
        i += 1
    return dict(eq=eq, trades=trades, n_bars=n, end_pos=pos)


def bh_series(closes, cost=COST_X1):
    """Buy-and-hold, same window and same entry bar as the system."""
    n = len(closes)
    eq = [1.0] * n
    if n < 2:
        return eq
    eq[1] = (1 - cost)
    for i in range(2, n):
        eq[i] = eq[i - 1] * (closes[i] / closes[i - 1])
    return eq


def _daily_rets(eq_map):
    """{theme: {date: eq}} -> {theme: {date: ret}} (first bar skipped)."""
    out = {}
    for t, d_eq in eq_map.items():
        ks = sorted(d_eq)
        out[t] = {ks[i]: d_eq[ks[i]] / d_eq[ks[i - 1]] - 1
                  for i in range(1, len(ks))}
    return out


def _pool(rets_map):
    """Equal-weight daily pooling across available themes per date.

    Returns (dates, pooled daily rets, pooled net)."""
    acc = {}
    for t, rmap in rets_map.items():
        for d, r in rmap.items():
            acc.setdefault(d, []).append(r)
    dates = sorted(acc)
    pooled = [float(np.mean(acc[d])) for d in dates]
    net = float(np.prod([1 + r for r in pooled]) - 1) if pooled else 0.0
    return dates, pooled, net


def _theme_windows(panel_by_theme):
    """Real ignition windows per theme: closes + dates, capped at cutoff."""
    closes, dates, wlens = {}, {}, {}
    for ev in EVENTS:
        full = panel_by_theme[ev["id"]]
        i0 = int(np.argmax(full.index >= ev["ignition"]))
        win = full.iloc[i0: i0 + PEAK_SEARCH_TD]
        win = win[win.index <= CUTOFF]
        closes[ev["id"]] = win.values.astype(float)
        dates[ev["id"]] = list(win.index)
        wlens[ev["id"]] = len(win)
    return closes, dates, wlens


def face_b(panel_by_theme, k_nulls=K_NULLS, sens=True):
    closes, dates, wlens = _theme_windows(panel_by_theme)
    sys_eq, bh_eq, by_theme = {}, {}, []
    for ev in EVENTS:
        tid = ev["id"]
        c = closes[tid]
        sim = simulate(c)
        bh = bh_series(c)
        sys_eq[tid] = dict(zip(dates[tid], sim["eq"]))
        bh_eq[tid] = dict(zip(dates[tid], bh))
        by_theme.append(dict(theme_id=tid, n_bars=len(c),
                             sys_net=float(sim["eq"][-1] - 1),
                             bh_net=float(bh[-1] - 1),
                             n_trades=len(sim["trades"]),
                             end_pos=bool(sim["end_pos"])))
    d_sys, p_sys_r, p_sys_net = _pool(_daily_rets(sys_eq))
    _, _, p_bh_net = _pool(_daily_rets(bh_eq))

    # LOO folds (frozen: sign of sys-bh per fold vs full-sample sign)
    full_sign = np.sign(p_sys_net - p_bh_net)
    loo, loo_stable = [], 0
    for t in sys_eq:
        sub_s = {x: sys_eq[x] for x in sys_eq if x != t}
        sub_b = {x: bh_eq[x] for x in bh_eq if x != t}
        _, _, sn = _pool(_daily_rets(sub_s))
        _, _, bn = _pool(_daily_rets(sub_b))
        m = bool(np.sign(sn - bn) == full_sign)
        loo.append(dict(left_out=t, sys_net=sn, bh_net=bn, sign_match=m))
        loo_stable += int(m)

    # ignition-date terciles (6/5/5)
    order = sorted(EVENTS, key=lambda e: e["ignition"])
    thirds = [[e["id"] for e in order[0:6]],
              [e["id"] for e in order[6:11]],
              [e["id"] for e in order[11:16]]]
    tercile = {}
    for gi, ids in enumerate(thirds):
        _, _, sn = _pool(_daily_rets({t: sys_eq[t] for t in ids}))
        _, _, bn = _pool(_daily_rets({t: bh_eq[t] for t in ids}))
        tercile[f"tercile_{gi}"] = dict(themes=ids, sys_net=sn, bh_net=bn)

    # random-ignition pooled nulls: one random start per theme per rep,
    # same proxy, same window length, same system and costs
    null_nets, per_theme_null = [], {e["id"]: [] for e in EVENTS}
    for k in range(k_nulls):
        rng = _rng(SUB_NULL + k)
        rep = {}
        for ev in EVENTS:
            tid = ev["id"]
            full = panel_by_theme[tid]
            wl = wlens[tid]
            hi = len(full) - wl
            if hi < 0:
                hi = 0
            s = int(rng.integers(0, hi + 1))
            win = full.iloc[s: s + wl]
            sim = simulate(win.values.astype(float))
            rep[tid] = dict(zip(list(win.index), sim["eq"]))
            per_theme_null[tid].append(float(sim["eq"][-1] - 1))
        _, _, nnet = _pool(_daily_rets(rep))
        null_nets.append(nnet)
    null_arr = np.array(null_nets)
    null_p95 = float(np.percentile(null_arr, 95))

    # structural sensitivity variants (pooled x1, disclosure only)
    sens_rows = []
    if sens:
        for bl in (0.75, 0.80, 0.85):
            for rb in (1.20, 1.25, 1.30):
                if abs(bl - float(MINUS20_LINE)) < 1e-12 \
                        and abs(rb - float(REBOUND_MIN)) < 1e-12:
                    continue
                m = {}
                for ev in EVENTS:
                    sim = simulate(closes[ev["id"]], break_line=bl,
                                   rebirth=rb)
                    m[ev["id"]] = dict(zip(dates[ev["id"]], sim["eq"]))
                _, _, sn = _pool(_daily_rets(m))
                sens_rows.append(dict(break_line=bl, rebirth=rb,
                                      pooled_sys_net=sn))
    return dict(by_theme=by_theme, sys_eq=sys_eq, bh_eq=bh_eq,
                pooled_dates=d_sys, pooled_sys_rets=p_sys_r,
                pooled_sys_net=p_sys_net, pooled_bh_net=p_bh_net,
                null_pooled_nets=[float(x) for x in null_arr],
                null_p95=null_p95, loo=loo, loo_stable=loo_stable,
                terciles=tercile, sensitivity=sens_rows,
                per_theme_null_nets=per_theme_null)


def regime_segments(pooled_dates, pooled_rets):
    """Disclosure only: pooled system daily returns by 510300 regime."""
    try:
        from t22_virtual_timepoints import regime_proxy
    except Exception:
        return None
    bench = load_series("sh510300")
    if bench is None:
        return None
    labels = regime_proxy(bench)
    lab_by_date = dict(zip(list(bench.index), list(labels)))
    seg = {}
    for d, r in zip(pooled_dates, pooled_rets):
        seg.setdefault(lab_by_date.get(d, "na"), []).append(r)
    return {k: dict(n=len(v), mean_daily=float(np.mean(v)),
                    cum_simple=float(np.sum(v)))
            for k, v in seg.items() if v}


def d6_numeric(sys_eq):
    """Pooled system daily series vs REG6 registered members (ew6 canon,
    identical code path to the live.paper anchor gate; MON_P1 precedent)."""
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    member_rets = {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        member_rets[tid] = eq.pct_change().dropna()
    dates, pooled, _ = _pool(_daily_rets(sys_eq))
    ps = pd.Series(pooled, index=[pd.Timestamp(d) for d in dates])
    rows = []
    for tid, sr in member_rets.items():
        j = pd.concat([ps, sr], axis=1, keys=["sys", "mem"]).dropna()
        if len(j) < 30:
            rows.append(dict(member=tid, n_common=len(j), corr=None,
                             reject=None))
            continue
        c = float(np.corrcoef(j["sys"].values, j["mem"].values)[0, 1])
        rows.append(dict(member=tid, n_common=len(j), corr=c,
                         reject=bool(abs(c) >= 0.7)))
    max_abs = max((abs(r["corr"]) for r in rows if r["corr"] is not None),
                  default=None)
    return dict(vs_members=rows, max_abs_corr=max_abs,
                any_reject=any(r.get("reject") for r in rows))


# ---------------------------------------------------------------- gates

def completeness_gates(waves, ledger=False):
    sha = _sha16_file(WAVES_JSON)
    assert sha == WAVES_SHA16, f"waves sha16 drift: {sha}"
    assert len(waves) == 43, f"n_waves {len(waves)} != 43"
    assert len({w["theme_id"] for w in waves}) == 16, "n_themes != 16"
    for w in waves:
        d = w["dur_to_peak_td"]
        expect = ("pulse" if d <= CLASS_PULSE_MAX_TD else
                  "long" if d >= CLASS_LONG_MIN_TD else "mid")
        assert w["wave_class"] == expect, f"class mismatch {w['wave_id']}"
    assert sg.SEED_REGISTRY.get("theme_persist_p1_nulls") == SEED_NULLS
    assert abs(COST_X1 - 0.0013041) < 1e-9, "COST_X1 import drift"
    # r673 guard refinement (live-repair, zero verdict/seed/prereg change):
    # the blunt base-to-base >=10000 check predates registry additions
    # made AFTER this prereg froze (theme_judge_p1_nulls=20585000, r667)
    # and false-positives on a genuinely disjoint band. Extent-aware band
    # scan below = the same law theme_judge_p1.py _seed_band_check froze
    # (my extent from module substream map, others conservative 3000,
    # gap >= 2000 both sides).
    lo, hi = (SEED_NULLS, SEED_NULLS + max(SUB_NULL + K_NULLS,
                                           SUB_PERM + 15,
                                           SUB_CLUST + 15))
    others = {k: v for k, v in sg.SEED_REGISTRY.items()
              if isinstance(v, int) and k != "theme_persist_p1_nulls"}
    for k, s in others.items():
        if lo <= s < hi:
            raise AssertionError(f"seed band clash: {k}={s} inside my band")
        if s < lo and lo - (s + 3000) < 2000:
            raise AssertionError(f"seed band clash: {k}={s} below-gap "
                                 f"{lo - (s + 3000)} < 2000")
        if s > hi and s - hi < 2000:
            raise AssertionError(f"seed band clash: {k}={s} above-gap "
                                 f"{s - hi} < 2000")
    txt = open(LEDGER_PATH, encoding="utf-8").read()
    # r673 guard refinement (live-repair, zero verdict change): prereg-
    # faithful dedup = scan consumed GENERATION rows for the face-B
    # triple (事件锚入场+破线出场+复活再入场); consumption-declaration
    # rows -- including this batch's OWN (burned r657, non-generation) --
    # are the declared exception (same law theme_judge_p1.py selftest
    # check 8 froze). Own-burn refusal moved to run intent below so
    # post-burn selftest stays reproducible (audit face).
    gen_rows = [ln for ln in txt.splitlines() if "gen=" in ln]
    clash = [ln for ln in gen_rows
             if "事件锚" in ln and "破线" in ln and "复活" in ln]
    assert not clash, f"grammar already consumed (dedup gate): {clash[:1]}"
    if ledger:
        assert "THEME_PERSIST" not in txt, \
            "batch already burned (own consumption row in ledger)"
    return sha


# ---------------------------------------------------------------- pipeline

def build_payload(run_nulls=True, d6=True, ledger=False):
    waves = json.load(open(WAVES_JSON, encoding="utf-8"))["waves"]
    sha = completeness_gates(waves, ledger=ledger)
    faceA_rows = face_a(waves)

    panel_by_theme = {}
    for ev in EVENTS:
        full = load_series(ev["proxy"])
        assert full is not None, f"panel missing {ev['proxy']}"
        assert os.path.exists(os.path.join(ROOT, "data", "daily",
                                           f"{ev['proxy']}.csv")), \
            f"anchor-face mismatch: data/daily/{ev['proxy']}.csv"
        panel_by_theme[ev["id"]] = full[full.index <= CUTOFF]

    fb = face_b(panel_by_theme, k_nulls=(K_NULLS if run_nulls else 4))

    fa_surv = [r for r in faceA_rows if r["bonf_significant"]]
    faceA_verdict = ("separation_face_survives" if fa_surv
                     else "persistence_prediction_negative")
    cond1 = fb["pooled_sys_net"] > fb["pooled_bh_net"]
    cond2 = fb["pooled_sys_net"] > fb["null_p95"]
    cond3 = fb["loo_stable"] >= 14
    faceB_verdict = ("mechanical_waveride_survives"
                     if (cond1 and cond2 and cond3)
                     else "mechanical_waveride_negative")

    pr = np.array(fb["pooled_sys_rets"], dtype=float)
    sr_ann = (float(np.mean(pr) / np.std(pr) * np.sqrt(252))
              if np.std(pr) > 0 else 0.0)
    t_val = float(sg.t_from_sharpe(sr_ann, len(pr)))
    m1 = sg.m1_t_value_gate(t_val) if hasattr(sg, "m1_t_value_gate") else None

    # x2 cost-stress leg (pooled)
    x2_eq = {}
    closes, dates, _ = _theme_windows(panel_by_theme)
    for ev in EVENTS:
        sim = simulate(closes[ev["id"]], cost=2 * COST_X1)
        x2_eq[ev["id"]] = dict(zip(dates[ev["id"]], sim["eq"]))
    _, _, x2_net = _pool(_daily_rets(x2_eq))

    payload = {
        "batch": BATCH,
        "prereg": PREREG,
        "exploration_labeled": True,
        "zero_registration_claims": True,
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(CUTOFF)},
        "gates": {
            "waves_sha16": sha,
            "completeness": "PASS",
            "ban_gate": "ADMIT rc0 (freeze window)",
            "exit_axis": "1-own-exit (break 0.80 + rebirth 1.25, T+1 close)",
        },
        "faceA": {
            "n_waves": 43, "n_features": 5, "n_outcomes": 3,
            "k_perm": K_PERM, "bonferroni_n": 5,
            "tests": faceA_rows, "verdict": faceA_verdict,
            "survivors": fa_surv,
        },
        "faceB": {
            "n_themes": 16, "by_theme": fb["by_theme"],
            "pooled_sys_net_x1": fb["pooled_sys_net"],
            "pooled_bh_net": fb["pooled_bh_net"],
            "pooled_sys_net_x2": x2_net,
            "null_p95": fb["null_p95"],
            "null_mean": float(np.mean(fb["null_pooled_nets"])),
            "null_n": len(fb["null_pooled_nets"]),
            "loo_stable": fb["loo_stable"], "loo": fb["loo"],
            "terciles": fb["terciles"], "sensitivity": fb["sensitivity"],
            "per_theme_null_nets": fb["per_theme_null_nets"],
            "null_pooled_nets": fb["null_pooled_nets"],
            "verdict": faceB_verdict,
            "conditions": dict(beat_bh=bool(cond1),
                               beat_null_p95=bool(cond2),
                               loo_stable=bool(cond3)),
        },
        "m1_t_face": {
            "sharpe_annualized_x1": sr_ann,
            "t_from_sharpe": t_val,
            "gate_read": (m1 if not isinstance(m1, (dict, list))
                          else json.loads(json.dumps(m1, default=str))),
        },
    }
    if d6:
        try:
            payload["d6"] = d6_numeric(fb["sys_eq"])
        except Exception as exc:
            payload["d6"] = {"error": repr(exc)}
        payload["regime_segments"] = regime_segments(
            fb["pooled_dates"], fb["pooled_sys_rets"])
    if ledger:
        payload["trials_ledger"] = sg.append_ledger(
            batch_name=BATCH, batch_trials=259,
            file_name="results/theme_persist_p1/theme_persist_p1.json",
            evidence_cutoff=CUTOFF,
            note="R4 persistence gate + mechanical wave-ride, "
                 "exploration-labeled two-question face (43 waves + 16 "
                 "systems + 200 random-ignition nulls)")
    return payload


def _write_outputs(payload):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT_D6, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload.get("d6", {}), fh, ensure_ascii=False,
                  indent=1, sort_keys=True)
    with open(OUT_FACA, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["feature", "outcome", "stat",
                                          "p_perm", "p_cluster",
                                          "bonf_significant"])
        w.writeheader()
        for r in payload["faceA"]["tests"]:
            w.writerow(r)
    with open(OUT_FACB, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["theme_id", "n_bars", "sys_net",
                                          "bh_net", "n_trades", "end_pos"])
        w.writeheader()
        for r in payload["faceB"]["by_theme"]:
            w.writerow(r)
    with open(OUT_NULLS, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["rep", "pooled_net"])
        w.writeheader()
        for i, v in enumerate(payload["faceB"]["null_pooled_nets"]):
            w.writerow(dict(rep=i, pooled_net=v))


# ---------------------------------------------------------------- selftest

def _synth(n, kind):
    if kind == "break_rebirth":
        c = np.concatenate([
            np.linspace(1.0, 2.0, 10),
            np.linspace(2.0, 1.4, 5),
            np.linspace(1.4, 1.0, 5),
            np.linspace(1.0, 1.35, 5),
            np.full(max(0, n - 25), 1.35),
        ])
    elif kind == "no_break":
        c = np.linspace(1.0, 1.5, n)
    else:
        c = np.concatenate([np.linspace(1.0, 2.0, 10),
                            np.linspace(2.0, 0.9, n - 10)])
    return c[:n]


def selftest():
    tally = [0, 0]

    def chk(name, cond):
        tally[0 if cond else 1] += 1
        print(f"  [selftest] {name}: {'PASS' if cond else 'FAIL'}")

    waves = json.load(open(WAVES_JSON, encoding="utf-8"))["waves"]
    try:
        sha = completeness_gates(waves)
        chk(f"completeness gates (sha16={sha})", True)
    except AssertionError as exc:
        chk(f"completeness gates ({exc})", False)

    c = _synth(40, "break_rebirth")
    sim = simulate(c)
    eq, tr = sim["eq"], sim["trades"]
    chk("entry at bar1 close with cost", abs(eq[1] - (1 - COST_X1)) < 1e-12)
    peak = np.maximum.accumulate(c)
    trig = int(np.argmax(c <= 0.80 * peak))
    sells = [t for t in tr if t[1] == "sell"]
    chk("break trigger bar + T+1 sell execution",
        bool(sells) and sells[0][0] == trig + 1)
    if sells:
        j = sells[0][0]
        expect = (1 - COST_X1) * (c[trig] / c[1]) \
            * (c[j] / c[trig]) * (1 - COST_X1)
        chk("sell-bar eq hand formula", abs(eq[j] - expect) < 1e-12)
        troughs = np.minimum.accumulate(c[j:])
        reb = None
        for m in range(1, len(troughs)):
            if c[j + m] >= troughs[m] * REBOUND_MIN:
                reb = j + m
                break
        buys2 = [t for t in tr if t[1] == "buy" and t[0] > j]
        chk("rebirth re-entry at trigger+1",
            bool(buys2) and reb is not None and buys2[0][0] == reb + 1)

    sim2 = simulate(_synth(40, "no_break"))
    chk("no-break holds to end (1 buy 0 sell)",
        len([t for t in sim2["trades"] if t[1] == "buy"]) == 1
        and len([t for t in sim2["trades"] if t[1] == "sell"]) == 0
        and sim2["end_pos"] is True)
    sim3 = simulate(_synth(40, "dead"))
    chk("dead face: exactly 1 buy 1 sell, flat at end",
        len([t for t in sim3["trades"] if t[1] == "buy"]) == 1
        and len([t for t in sim3["trades"] if t[1] == "sell"]) == 1
        and sim3["end_pos"] is False)

    c4 = _synth(30, "no_break")
    bh = bh_series(c4)
    chk("bh entry cost + ratio math",
        abs(bh[1] - (1 - COST_X1)) < 1e-12
        and abs(bh[5] - (1 - COST_X1) * c4[5] / c4[1]) < 1e-12)

    rng1 = _rng(SUB_PERM + 0)
    p1 = rng1.permutation(10)
    rng2 = _rng(SUB_PERM + 0)
    p2 = rng2.permutation(10)
    chk("rng substream determinism", bool(np.array_equal(p1, p2)))

    x = np.arange(43, dtype=float)
    y = (np.arange(43) % 3 == 1).astype(int)   # proper binary contract
    auc_rk = _auc_from_ranks(pd.Series(x).rank().values, y)
    pos, neg = x[y == 1], x[y == 0]
    u_ref = sum((pos > v).sum() + 0.5 * (pos == v).sum() for v in neg) \
        / (len(pos) * len(neg))
    chk("auc-from-ranks equals brute-force U", abs(auc_rk - u_ref) < 1e-12)

    a = build_payload(run_nulls=False, d6=False, ledger=False)
    b = build_payload(run_nulls=False, d6=False, ledger=False)
    ja = json.dumps(a, sort_keys=True, default=str)
    jb = json.dumps(b, sort_keys=True, default=str)
    chk("mini-pipeline double-run byte identity", ja == jb)

    print(f"selftest: {tally[0]} PASS, {tally[1]} FAIL")
    return 0 if tally[1] == 0 else 1


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    t0 = time.time()
    if args.cmd == "selftest":
        return selftest()
    payload = build_payload(run_nulls=True, d6=True, ledger=True)
    elapsed = time.time() - t0
    payload["audit"] = {
        "elapsed_sec": round(elapsed, 1),
        "budget_cap_sec": BUDGET_SEC,
        "over_budget": bool(elapsed > BUDGET_SEC),
        "machine": "bm-a",
        "compute": "single-process L1 in-round short batch (O-2100 precedent)",
    }
    if payload["audit"]["over_budget"]:
        print("BUDGET CAP EXCEEDED -- nothing finalized (exit 3)")
        return 3
    _write_outputs(payload)
    led = payload.get("trials_ledger", {})
    fb = payload["faceB"]
    print(f"{BATCH}: faceA={payload['faceA']['verdict']} "
          f"(survivors={len(payload['faceA']['survivors'])}) "
          f"faceB={fb['verdict']} sys_x1={fb['pooled_sys_net_x1']:.4f} "
          f"bh={fb['pooled_bh_net']:.4f} x2={fb['pooled_sys_net_x2']:.4f} "
          f"null_p95={fb['null_p95']:.4f} loo={fb['loo_stable']}/16 "
          f"ledger_total={led.get('total', 'n/a')} elapsed={elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
