# -*- coding: utf-8 -*-
"""PORTFOLIO_BOOK_P1 runner -- T-138 s2 (O-20260930-1147 L2 sleeve book).

Prereg FROZEN: research/PORTFOLIO_BOOK_P1.md (r505 freeze commit f28c89c23).
Post-run only sec.7/8 backfill; criteria frozen, no re-runs (engineering
re-runs need dual-run evidence per r446 law).

Batch face (prereg sec.0): 4 book-config cells = delta in {0.70, 0.50} x
weight rule in {EW, IVOL} over the frozen REEVAL18 roster 18 sleeves
(drill judgment archive members, verdicts carried, zero re-litigation).
Book-construction judgment batch, NOT a generation batch: sleeve replays
consume zero generation trials; the trials ledger counts the 4 book cells
only (prereg sec.8).

Import-face law (prereg sec.2/3): roster/panel/replay/anchor faces IMPORTED
verbatim from scripts/reeval18_drill.py (the frozen drill harness; wave
replay primitives flow through drill._wave_run -> tl1/tl2/tl3/tl5
verbatim); scoring constants IMPORTED from science_gates frozen canon
(REFORM_* / t_from_sharpe / bh_batch_fdr / g2_reform_fdr4d /
bootstrap_ci_sharpe / deflated_sharpe_ratio); book-layer cost rate from
knowledge/cost_spec.X1_RATE (import-asserted == 0.0013041, never
hand-copied). engine/exit_rules.py zero touch. Restatement law: frozen
archive values (member family_pbo, d6 vs-registered corr, composite rank,
five-member EW baseline) are ARCHIVE READS, not recomputed.

Subcommands (r446 three-command law):
  prep        fail-closed gates: roster sha16 pin + patch self-test +
              G-PANEL (cutoff-truncated face) + six-member live anchor
              gate + drill archive sha16 pin + composite face == roster +
              probe-matrix same-face reconstruction (payload_sha256
              identity vs frozen probe artifact 50b77e2a...) ->
              portfolio_book/manifest_book.json
  run         the burn: 18 sleeves x dual-cost verbatim replay
              (checkpoint per sleeve, kill-safe resume) -> 4 book configs
              computed FROM the JSON-roundtripped checkpoint via the
              single-source _compute_config helper (finalize recompute
              identity by construction; checkpoint per config) ->
              BOOK-burn-<cutoff>.json
  finalize    determinism gate (sentinel sleeve full re-replay sha match +
              all-4-config book-math replay == burn payload shas) +
              batch BH-FDR + four-dim composite (frozen constants import)
              + eligible_book verdict + trials-ledger append (+4) +
              gate_attrition judgment row (CRLF indent-1 rewrite per
              r289 law) + BOOK-<cutoff>.json + book_cells.csv
  selftest    hermetic offline fixtures (r116 law; no repo data files)
  status      checkpoint progress readout

Exit codes: 0 = ok/no-op, 1 = gate fail (VOID, zero products), 2 =
machinery error / blocked dependency (honest report, never mask).

Design notes (frozen in code, disclosed in results):
  * book cost face: rebalance-day turnover measured against PRE-COST
    drifted weights (gross denominator, non-circular); post-rebalance
    weights = target; non-rebalance days drift per prereg formula
    w_i(t) = w_i(t-1)(1+r_i(t))/(1+r_book(t)) with the NET book return.
  * entry: target weights established at window base (wbase) close from
    info through the prior day (strict causal, sigma shift(1) face);
    entry cost = sum|w_target| x X1_RATE charged once on the first
    window return day.
  * x2 leg: IDENTICAL weight path (x1 face drives weights), member x2
    returns, ALL book-layer costs doubled (2 x X1_RATE), per prereg sec.3.
  * IVOL: w_i propto 1/sigma_i,60d (rolling 60 on full-history x1
    returns, shift(1) strictly causal). Invalid sigma (non-finite or 0)
    -> that member's raw share falls back to the mean of valid raw
    shares ("equal-share demotion", counted + disclosed); no valid sigma
    at a decision date -> pure equal weights.
  * LOO: leave-one-member-out, SAME weight rule renormalized over the
    remaining members (no re-selection), min over removed members.
  * diversification_delta: sharpe_full_L - sum_i(wbar_i * sharpe_i);
    EW wbar_i = 1/n exactly (arithmetic mean face per prereg), IVOL
    wbar_i = realized mean end-of-day weight.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import reeval18_drill as drill              # frozen judgment harness (verbatim)
from engine.metrics import max_drawdown, sharpe
from knowledge.cost_spec import X1_RATE
from live.paper import self_test_patches
from p5_random_entry import passive_rel
from science_gates import (CostPatch, REFORM_DIM_WEIGHTS, REFORM_Q_LEVEL,
                           REFORM_SUB_WEIGHTS, _norm_cdf, append_ledger,
                           bh_batch_fdr, bootstrap_ci_sharpe, cutoff_meta,
                           deflated_sharpe_ratio, g2_reform_fdr4d,
                           t_from_sharpe)

# ------------------------------------------------------------------ frozen
WAVE = "PORTFOLIO_BOOK_P1"
PREREG = "research/PORTFOLIO_BOOK_P1.md"
CUTOFF = drill.CUTOFF                       # "2026-09-22" (frozen grid)
CI_SEED = drill.CI_SEED                     # 20260923 frozen family
PPY = drill.PPY                             # 252.0
W6 = drill.W6                               # WINDOWS["6m"]
MIN_SEG_DAYS = drill.MIN_SEG_DAYS           # 20
CAP_LADDER = drill.CAP_LADDER
REGIME_MAP = drill.REGIME_MAP
BATCH_CELLS = 4                             # prereg sec.0 book configs
DSR_N_TRIALS = 4                            # prereg sec.3 batch-internal DSR
IVOL_WINDOW = 60                           # sigma_i,60d rolling window

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
RES_DIR = os.path.join(drill.PATHS.results_dir, "portfolio_book")
DRILL_RESULTS = os.path.join(drill.PATHS.results_dir, "reeval18",
                             f"DRILL-{CUTOFF}.json")
DRILL_SHA16_PIN = "fe131c1a63e1e3d2"        # r505 probe-pinned archive sha
PROBE_PATH = os.path.join(drill.PATHS.results_dir, "portfolio_book_probe",
                          "pairwise_corr_p1.json")
PROBE_PAYLOAD_SHA256_PIN = ("50b77e2ac98e3be0a702658b3338dcb12149b7f4a"
                            "2be73a2b770b696ad92a8d4")
FIVE_EW_ANN_PIN = 0.028086                  # O-1126 frozen archive read
MANIFEST = os.path.join(RES_DIR, "manifest_book.json")
CKPT_MEMBERS = os.path.join(RES_DIR, "checkpoint_book_members.jsonl")
CKPT_CONFIGS = os.path.join(RES_DIR, "checkpoint_book_configs.jsonl")
BURN_JSON = os.path.join(RES_DIR, f"BOOK-burn-{CUTOFF}.json")
OUT_JSON = os.path.join(RES_DIR, f"BOOK-{CUTOFF}.json")
OUT_CSV = os.path.join(RES_DIR, "book_cells.csv")
REGIME_STATE = drill.REGIME_STATE
GATE_ATTRITION = os.path.join(drill.PATHS.results_dir, "gate_attrition.json")
MACHINE_JSON = os.path.join(_ROOT, "fleet", "machine.json")

# config order frozen: delta outer (0.70 first, prereg core), rule inner
DELTAS = (0.70, 0.50)
RULES = ("EW", "IVOL")

if abs(X1_RATE - 0.0013041) > 1e-12:
    raise ImportError(f"cost_spec X1_RATE drift: {X1_RATE} != 0.0013041")


def _j(x):
    return drill._j(x)


def _sha16(path):
    return drill._sha16(path)


def _payload_sha(payload):
    return drill._payload_sha(payload)


def _machine_id():
    try:
        return json.load(open(MACHINE_JSON, encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _cfg_id(delta, rule):
    return f"delta{delta:.2f}-{rule}"


# ------------------------------------------------------------------ probe
def _probe_face(st, roster, win_rets1, n_trades_win, comp_rank, generated):
    """Rebuild the r505 probe payload EXACTLY (same-face reconstruction).
    'generated' injected from the frozen artifact so the only varying face
    is data (drift = config mismatch VOID, fail-closed; never 'data rot').
    """
    n = len(roster["rows"])
    R = pd.DataFrame(win_rets1)             # roster insertion order
    C = R.corr()
    members = list(C.columns)
    vals = C.values
    off = [(i, j, float(vals[i, j]))
           for i in range(n) for j in range(i + 1, n)]
    offs = sorted(v for _, _, v in off)
    per_member_max = {members[i]: round(max(
        abs(float(vals[i, j])) for j in range(n) if j != i), 6)
        for i in range(n)}
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
        "generated": generated,
    }
    return payload


def _archive_faces():
    """Frozen drill archive reads: sha pin + composite rank + member faces."""
    got = _sha16(DRILL_RESULTS)
    if got != DRILL_SHA16_PIN:
        raise ValueError(f"drill archive sha16 drift: {got} != {DRILL_SHA16_PIN}")
    arc = json.load(open(DRILL_RESULTS, encoding="utf-8"))
    comp = {cid: m["composite"]
            for cid, m in arc["g2_reform"]["members"].items()}
    comp_rank = sorted(comp.items(), key=lambda kv: (-kv[1], kv[0]))
    base = arc["five_member_ew_baseline"]["annualized_ret"]
    if abs(float(base) - FIVE_EW_ANN_PIN) > 1e-9:
        raise ValueError(f"five-member EW baseline drift: {base} "
                         f"!= {FIVE_EW_ANN_PIN}")
    fpbo = {cid: c["family_pbo"] for cid, c in arc["cells"].items()}
    d6m = {cid: d["max_corr_vs_registered"]
           for cid, d in arc["d6"]["table"].items()}
    return {"arc": arc, "comp_rank": comp_rank, "comp": comp,
            "five_ew_ann": float(base), "family_pbo": fpbo, "d6_max": d6m}


# ------------------------------------------------------------------ replay
def _replay_members(st, rows, x2=True):
    """Verbatim sleeve replay (drill._wave_run dispatch). Returns per-cid
    full-history x1/x2 equity curves + x1 trades."""
    out = {}
    for row in rows:
        cid = row["candidate_id"]
        cand = drill._roster_cand(row)
        template = drill._roster_template(row)
        eq, trades, _m = drill._wave_run(st, row["wave"], cand, template)
        eq2 = None
        if x2:
            with CostPatch(2):
                eq2, _t2, _m2 = drill._wave_run(st, row["wave"], cand,
                                                template)
        out[cid] = {"eq1": eq, "eq2": eq2, "trades": trades,
                    "wave": row["wave"]}
        print(f"  replay {cid} ok ({'x1+x2' if x2 else 'x1'})")
    return out


def _decision_dates(st, rebal_pos):
    """Entry date (window base) + monthly rebalance dates, ISO strings."""
    dates = [str(st["idx"][st["wbase"]].date())]
    dates += [str(st["idx"][st["w0"] + k].date()) for k in sorted(rebal_pos)]
    return dates


def _member_payload(cid, wave, eq1, eq2, trades, st, dec_dates):
    """Checkpoint payload: RAW window returns (JSON roundtrip exact) +
    decision-date IVOL sigmas (shift(1) strictly causal) + faces."""
    wbase, w0, wend = st["wbase"], st["w0"], st["wend"]
    r1_full = eq1.pct_change().dropna()
    sig = r1_full.rolling(IVOL_WINDOW).std().shift(1)
    win1 = eq1.iloc[wbase:].pct_change().dropna()
    if len(win1) != st["n_win_days"]:
        raise ValueError(f"{cid}: window returns {len(win1)} != "
                         f"{st['n_win_days']}")
    sig_dec = {}
    for d in dec_dates:
        try:
            v = float(sig.loc[pd.Timestamp(d)])
        except Exception:
            v = None
        sig_dec[d] = v if (v is not None and math.isfinite(v)) else None
    if eq2 is not None:
        win2 = eq2.iloc[wbase:].pct_change().dropna()
        if len(win2) != st["n_win_days"]:
            raise ValueError(f"{cid}: x2 window returns {len(win2)}")
        r2 = [float(x) for x in win2.values]
    else:
        r2 = None
    w0s = str(st["idx"][w0].date())
    wes = str(st["idx"][wend].date())
    return {
        "candidate_id": cid, "wave": wave,
        "win_rets1": [float(x) for x in win1.values],
        "win_rets2": r2,
        "sig_dec": sig_dec,
        "sharpe_win": round(float(sharpe(eq1.iloc[wbase:])), 4),
        "n_trades_win": int(sum(1 for tr in trades
                                if w0s <= tr["date"] <= wes)),
    }


# ------------------------------------------------------------ book math
def _monthly_firsts(st):
    """Positions k in the window (idx[w0..wend]) that are the first panel
    trading day of their calendar month (prereg: monthly rebalance)."""
    idx = st["idx"]
    pos = []
    prev_month = None
    for k in range(st["n_win_days"]):
        d = idx[st["w0"] + k]
        m = (d.year, d.month)
        if m != prev_month:
            pos.append(k)
            prev_month = m
    return pos


def _target_weights(rule, sel, sig_dec, date, n_sel):
    """Target weights at a decision date. Returns (weights, n_invalid)."""
    if n_sel == 0:
        return np.array([]), 0
    if rule == "EW":
        return np.full(n_sel, 1.0 / n_sel), 0
    raw, valid_idx, n_invalid = [], [], 0
    for i, cid in enumerate(sel):
        v = sig_dec.get(cid, {}).get(date)
        if v is not None and math.isfinite(v) and v > 0.0:
            raw.append(1.0 / v)
            valid_idx.append(i)
        else:
            raw.append(None)
            n_invalid += 1
    if not valid_idx:
        return np.full(n_sel, 1.0 / n_sel), n_sel
    vmean = float(np.mean([raw[i] for i in valid_idx]))
    raw = [vmean if r is None else r for r in raw]
    arr = np.array(raw, dtype=float)
    return arr / arr.sum(), n_invalid


def _simulate_book(sel, rule, r1, r2, sig_dec, dates, rebal_pos, entry_date):
    """Book daily returns (x1 + x2 legs) + cost ledger. Pure function of
    checkpointed faces (determinism by construction).

    r1/r2: (N, m) member window daily returns (the x1 face drives the
    weight path; x2 only supplies returns). dates: ISO strings per
    window day. rebal_pos: monthly-first positions. entry_date: the
    window-base decision date (ISO string) for the entry target weights.
    """
    N, m = r1.shape
    rebal_set = set(rebal_pos)
    w, n_inv = _target_weights(rule, sel, sig_dec, entry_date, m)
    invalid_uses = n_inv
    entry_cost = float(np.abs(w).sum()) * X1_RATE
    r_book = np.empty(N)
    w_pre = np.empty((N, m))
    w_track = np.empty((N, m))
    cost_k = np.empty(N)
    events = 0
    rebal_cost = 0.0
    for k in range(N):
        w_pre[k] = w
        rg = float(w @ r1[k])
        cost = entry_cost if k == 0 else 0.0
        if k in rebal_set:
            tgt, n_inv = _target_weights(rule, sel, sig_dec, dates[k], m)
            invalid_uses += n_inv
            drift = w * (1.0 + r1[k]) / (1.0 + rg)   # pre-cost drift face
            cost += float(np.abs(tgt - drift).sum()) * X1_RATE
            events += 1
            rebal_cost += cost - (entry_cost if k == 0 else 0.0)
            w = tgt
        else:
            w = w * (1.0 + r1[k]) / (1.0 + rg - cost)
        r_book[k] = rg - cost
        cost_k[k] = cost
        w_track[k] = w
    # x2 leg: SAME weight path (x1 face), member x2 returns, costs doubled
    r_book2 = np.empty(N)
    for k in range(N):
        r_book2[k] = float(w_pre[k] @ r2[k]) - 2.0 * cost_k[k]
    return {"r1": r_book, "r2": r_book2, "w_track": w_track,
            "entry_cost": entry_cost,
            "rebalance_cost_total": rebal_cost,
            "rebalance_events": events,
            "invalid_sigma_uses": invalid_uses}


def _select_greedy(comp_rank, corr_df, delta):
    """Frozen greedy selection: composite-descending; |pairwise corr| >=
    delta with ANY already-selected member -> rejected."""
    selected, rejected = [], []
    for cid, _score in comp_rank:
        blocker = None
        for s in selected:
            c = float(corr_df.loc[cid, s])
            if abs(c) >= delta:
                blocker = (s, round(c, 6))
                break
        if blocker is None:
            selected.append(cid)
        else:
            rejected.append({"candidate_id": cid, "blocked_by": blocker[0],
                             "corr": blocker[1]})
    return selected, rejected


def _seg_faces(r_book, st):
    """Regime segments on the book window returns (drill caliber)."""
    idx = st["idx"]
    s_series = st["states"].reindex(idx[st["w0"]:st["wend"] + 1])
    seg_rets = {"bull": [], "chop": [], "bear": []}
    for pos in range(st["n_win_days"]):
        v = s_series.iloc[pos]
        seg = REGIME_MAP.get(v, "bear") if v == v else "bear"
        seg_rets[seg].append(float(r_book[pos]))
    segs = {}
    for seg, rets in seg_rets.items():
        segs[seg] = {"n_days": len(rets),
                     "sharpe": drill._seg_sharpe(rets)
                     if len(rets) >= MIN_SEG_DAYS else None}
    live = [v["sharpe"] for v in segs.values() if v["sharpe"] is not None]
    return segs, (round(min(live), 4) if live else None)


def _beat6m_book(eq_book, st):
    """Rolling 6m book beats vs passive (drill caliber) + rel distribution."""
    idx, w0, wend = st["idx"], st["w0"], st["wend"]
    k = tot = 0
    rels = []
    p = w0
    while p + W6 - 1 <= wend:
        sdate, edate = idx[p], idx[p + W6 - 1]
        syms = st["close"].columns[st["close"].loc[sdate].notna()]
        pret = float(passive_rel(st["close"], syms, sdate, edate).iloc[-1]
                     - 1.0)
        cret = float(eq_book.iloc[p + W6 - 1] / eq_book.iloc[p] - 1.0)
        k += int(cret > pret)
        tot += 1
        rels.append(cret - pret)
        p += 1
    dist = None
    if rels:
        s = sorted(rels)
        n = len(s)
        dist = {"best": round(s[-1], 6), "worst": round(s[0], 6),
                "p25": round(s[int(0.25 * (n - 1))], 6),
                "median": round(s[int(0.5 * (n - 1))], 6),
                "p75": round(s[int(0.75 * (n - 1))], 6), "n": n}
    return {"k": k, "n": tot, "rate": round(k / tot, 6) if tot else 0.0}, dist


def _monthly_start_ann(eq_book, st, monthly_firsts):
    """Monthly-start annualized distribution (prereg sec.8 full-start
    face). eq_book has N+1 values (base day first)."""
    vals = []
    N = st["n_win_days"]
    for k in monthly_firsts:
        if k >= N - 1:
            continue
        seg = float(eq_book.iloc[N] / eq_book.iloc[k + 1] - 1.0)
        vals.append((1.0 + seg) ** (PPY / (N - k)) - 1.0)
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    return {"starts": [round(v, 6) for v in vals],
            "best": round(s[-1], 6), "worst": round(s[0], 6),
            "p25": round(s[int(0.25 * (n - 1))], 6),
            "median": round(s[int(0.5 * (n - 1))], 6),
            "p75": round(s[int(0.75 * (n - 1))], 6)}


def _cap_face(r_book, cap):
    r_cap = cap * np.asarray(r_book, dtype=float)
    eq_cap = (1.0 + r_cap).cumprod()
    n = len(r_cap)
    total = float(eq_cap[-1] - 1.0)
    ann = float((1.0 + total) ** (PPY / n) - 1.0) if n else None
    eq_s = pd.Series(eq_cap)
    return {"cap": cap, "annualized_ret_capped": round(ann, 6),
            "sharpe_capped": round(float(sharpe(eq_s)), 4)}


def _w_mean_face(rule, sel, w_track):
    """Realized mean end-of-day weights (EW = exact 1/n arithmetic-mean
    face per prereg sec.3)."""
    m = len(sel)
    if rule == "EW":
        return {c: 1.0 / m for c in sel}
    return {c: round(float(np.mean(w_track[:, i])), 8)
            for i, c in enumerate(sel)}


def _diversification_delta(sharpe_full, member_sharpes, w_mean):
    wsum = sum(w_mean[c] * member_sharpes[c] for c in member_sharpes)
    return round(sharpe_full - wsum, 4)


def _compute_config(cfg_id, delta, rule, members, arc_f, st, C,
                     monthly_firsts, entry_date, cap, cap_state):
    """Single-source per-config face builder (run + finalize share this;
    pure function of checkpointed member payloads + frozen archive)."""
    sel, rejected = _select_greedy(arc_f["comp_rank"], C, delta)
    if not sel:
        raise ValueError(f"{cfg_id}: EMPTY SELECTION (degenerate)")
    r1 = np.array([[float(x) for x in members[c]["win_rets1"]]
                   for c in sel]).T
    r2 = np.array([[float(x) for x in members[c]["win_rets2"]]
                   for c in sel]).T
    sig_dec_sel = {c: members[c]["sig_dec"] for c in sel}
    dates = [str(st["idx"][st["w0"] + k].date())
             for k in range(st["n_win_days"])]
    sim = _simulate_book(sel, rule, r1, r2, sig_dec_sel, dates,
                         monthly_firsts, entry_date)
    r_book = sim["r1"]
    n = len(r_book)
    eq_book = pd.Series(np.concatenate(
        ([1.0], np.cumprod(1.0 + r_book))))
    eq_book2 = pd.Series(np.concatenate(
        ([1.0], np.cumprod(1.0 + sim["r2"]))))
    sharpe_full = float(sharpe(eq_book))
    total = float(eq_book.iloc[-1] / eq_book.iloc[0] - 1.0)
    ann = float((1.0 + total) ** (PPY / n) - 1.0)
    beat6m, beat6m_rel_dist = _beat6m_book(eq_book, st)
    segs, seg_min = _seg_faces(r_book, st)
    ci = bootstrap_ci_sharpe([float(x) for x in r_book], seed=CI_SEED)
    dsr = deflated_sharpe_ratio([float(x) for x in r_book],
                                n_trials=DSR_N_TRIALS)
    t = t_from_sharpe(sharpe_full, n)
    p_val = 1.0 - float(_norm_cdf(t))
    member_sharpes = {c: members[c]["sharpe_win"] for c in sel}
    w_mean = _w_mean_face(rule, sel, sim["w_track"])
    # LOO: same weight rule renormalized over remaining members (no
    # re-selection), min over removed
    loo = {}
    for drop in sel:
        sel_loo = [c for c in sel if c != drop]
        if not sel_loo:
            loo[drop] = None
            continue
        idxs = [sel.index(c) for c in sel_loo]
        sim_loo = _simulate_book(sel_loo, rule, r1[:, idxs], r2[:, idxs],
                                 sig_dec_sel, dates, monthly_firsts,
                                 entry_date)
        eq_loo = pd.Series(np.concatenate(
            ([1.0], np.cumprod(1.0 + sim_loo["r1"]))))
        loo[drop] = round(float(sharpe(eq_loo)), 4)
    live_loo = [v for v in loo.values() if v is not None]
    payload = {
        "config_id": cfg_id, "delta": delta, "rule": rule,
        "n_members": len(sel), "selected": list(sel), "rejected": rejected,
        "sharpe_full_L": round(sharpe_full, 4),
        "annualized_ret_L": round(ann, 6),
        "return_ceiling_O1126": round(ann - arc_f["five_ew_ann"], 6),
        "beat6m": beat6m, "beat6m_rel_dist": beat6m_rel_dist,
        "regime_segments": segs, "regime_min_sharpe": seg_min,
        "bootstrap_ci_low_L": round(float(ci["ci95_low"]), 4),
        "batch_dsr": round(float(dsr["dsr"]), 6),
        "t_stat": round(float(t), 4), "p_value": round(p_val, 6),
        "sharpe_x2_L": round(float(sharpe(eq_book2)), 4),
        "max_dd_x1": round(float(max_drawdown(eq_book)), 4),
        "max_dd_x2": round(float(max_drawdown(eq_book2)), 4),
        "entry_cost": round(sim["entry_cost"], 8),
        "rebalance_cost_total": round(sim["rebalance_cost_total"], 8),
        "rebalance_events": sim["rebalance_events"],
        "invalid_sigma_uses": sim["invalid_sigma_uses"],
        "monthly_start_ann": _monthly_start_ann(eq_book, st, monthly_firsts),
        "diversification_delta": _diversification_delta(
            sharpe_full, member_sharpes, w_mean),
        "member_window_sharpes": member_sharpes,
        "member_weights_mean": w_mean,
        "family_pbo_mean": round(float(np.mean(
            [arc_f["family_pbo"][c] for c in sel])), 6),
        "family_pbo_members": {c: arc_f["family_pbo"][c] for c in sel},
        "d6_max_corr": round(max(arc_f["d6_max"][c] for c in sel), 6),
        "d6_members": {c: arc_f["d6_max"][c] for c in sel},
        "loo_sharpes": loo,
        "loo_min_sharpe": round(min(live_loo), 4) if live_loo else None,
        "loo_ratio": (round(min(live_loo) / sharpe_full, 4)
                      if live_loo and sharpe_full else None),
        "cap_face": _cap_face(r_book, cap),
        "cap_state": cap_state,
    }
    return payload


# ------------------------------------------------------------------ prep
def cmd_prep() -> int:
    print(f"=== {WAVE} prep (prereg FROZEN {PREREG}) ===")
    try:
        roster = drill._load_roster()
    except Exception as e:
        print(f"PREP-GATE FAIL: roster -- {e}")
        return 1
    if not self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1
    try:
        arc_f = _archive_faces()
    except Exception as e:
        print(f"PREP-GATE FAIL: drill archive -- {e}")
        return 1
    try:
        st = drill._build_state()
    except Exception as e:
        print(f"PREP-GATE FAIL: state build -- {e}")
        return 2
    # G-ANCHOR: registered six replay vs live anchors (drill cmd_prep caliber)
    from firm.hr import load_trader
    from live.paper import anchor_gate
    anchors = {}
    for t in drill.tl1.A_TEMPLATES:
        trader = load_trader(t["trader_id"])
        a = anchor_gate(trader, st["prices"])
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        anchors[t["trader_id"]] = {"ok": True}
    # probe same-face reconstruction (18 x1 replays, the expensive gate)
    t0 = time.time()
    repl = _replay_members(st, roster["rows"], x2=False)
    win_rets1, n_trades_win = {}, {}
    for row in roster["rows"]:
        cid = row["candidate_id"]
        mp = _member_payload(cid, row["wave"], repl[cid]["eq1"], None,
                             repl[cid]["trades"], st, [])
        win_rets1[cid] = pd.Series(mp["win_rets1"])
        n_trades_win[cid] = mp["n_trades_win"]
        if float(win_rets1[cid].std()) <= 0.0:
            print(f"PREP-GATE FAIL: {cid} zero-variance window (degenerate)")
            return 1
    probe_art = json.load(open(PROBE_PATH, encoding="utf-8"))
    payload = _probe_face(st, roster, win_rets1, n_trades_win,
                          arc_f["comp_rank"], probe_art["generated"])
    got_sha = _payload_sha(payload)
    if got_sha != probe_art["payload_sha256"]:
        print(f"PREP-GATE FAIL: probe matrix same-face mismatch "
              f"{got_sha[:16]} != {probe_art['payload_sha256'][:16]} "
              f"(config mismatch VOID, not data rot)")
        return 1
    if got_sha != PROBE_PAYLOAD_SHA256_PIN:
        print(f"PREP-GATE FAIL: probe sha != prereg pin "
              f"{PROBE_PAYLOAD_SHA256_PIN[:16]}")
        return 1
    comp_ids = {c for c, _ in arc_f["comp_rank"]}
    if comp_ids != set(win_rets1):
        print("PREP-GATE FAIL: composite face != roster members")
        return 1
    man = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF),
        "roster_sha16": drill.ROSTER_SHA16,
        "drill_results_sha16": _sha16(DRILL_RESULTS),
        "grammar_sha16": st["grammar_sha16"],
        "probe_payload_sha256": got_sha,
        "window": {"start": str(st["idx"][st["w0"]].date()),
                   "end": str(st["idx"][st["wend"]].date()),
                   "base_date": str(st["idx"][st["wbase"]].date()),
                   "n_days": st["n_win_days"]},
        "panel": {"members": 48, "last_bar": CUTOFF},
        "anchors": anchors,
        "five_member_ew_ann": arc_f["five_ew_ann"],
        "x1_rate": X1_RATE,
        "batch_cells": BATCH_CELLS, "ci_seed": CI_SEED,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    os.makedirs(RES_DIR, exist_ok=True)
    json.dump(_j(man), open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"prep PASS: probe sha {got_sha[:16]} == frozen artifact; panel "
          f"48/48; anchors {len(anchors)}/6; window "
          f"{man['window']['start']}..{man['window']['end']} "
          f"({st['n_win_days']}d) [{time.time() - t0:.1f}s]")
    return 0


# ------------------------------------------------------------------- run
def _ckpt_ids(path, key):
    ids = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                ids.add(json.loads(line)[key])
    return ids


def _load_members_ckpt():
    members = {}
    for line in open(CKPT_MEMBERS, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            members[r["candidate_id"]] = r["payload"]
    return members


def cmd_run() -> int:
    print(f"=== {WAVE} run (18 sleeves x dual-cost + 4 book configs) ===")
    if not os.path.exists(MANIFEST):
        print("RUN-GATE FAIL: prep manifest absent (run prep first)")
        return 1
    t0 = time.time()
    roster = drill._load_roster()
    arc_f = _archive_faces()
    st = drill._build_state()
    monthly_firsts = _monthly_firsts(st)
    dec_dates = _decision_dates(st, monthly_firsts)
    entry_date = dec_dates[0]
    reg = json.load(open(REGIME_STATE, encoding="utf-8"))
    cap = CAP_LADDER.get(reg.get("state"))
    if cap is None:
        print(f"RUN-GATE FAIL: regime state {reg.get('state')} off-ladder")
        return 1
    # -- sleeve replay checkpoint (kill-safe resume)
    done = _ckpt_ids(CKPT_MEMBERS, "candidate_id")
    todo_rows = [r for r in roster["rows"]
                 if r["candidate_id"] not in done]
    if todo_rows:
        repl = _replay_members(st, todo_rows, x2=True)
        for row in todo_rows:
            cid = row["candidate_id"]
            mp = _member_payload(cid, row["wave"], repl[cid]["eq1"],
                                 repl[cid]["eq2"], repl[cid]["trades"],
                                 st, dec_dates)
            rec = {"candidate_id": cid, "sha256": _payload_sha(mp),
                   "payload": mp}
            with open(CKPT_MEMBERS, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  member checkpoint: +{len(todo_rows)} "
              f"[{time.time() - t0:.1f}s]")
    have = _ckpt_ids(CKPT_MEMBERS, "candidate_id")
    if len(have) != drill.BATCH_N_TRIALS:
        print(f"run PARTIAL: {len(have)}/18 sleeves on checkpoint "
              f"(resume-safe); rerun to complete")
        return 0
    # -- re-read checkpoint (JSON-roundtrip identity face: configs are a
    #    pure function of the checkpointed values)
    members = _load_members_ckpt()
    win_rets1 = {cid: pd.Series(p["win_rets1"])
                 for cid, p in members.items()}
    C = pd.DataFrame(win_rets1).corr()
    # -- 4 book configs
    t_cfg = time.time()
    for delta in DELTAS:
        for rule in RULES:
            cfg_id = _cfg_id(delta, rule)
            payload = _compute_config(cfg_id, delta, rule, members, arc_f,
                                       st, C, monthly_firsts, entry_date,
                                       cap, reg.get("state"))
            rec = {"config_id": cfg_id, "sha256": _payload_sha(payload),
                   "payload": payload}
            with open(CKPT_CONFIGS, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"  {cfg_id}: n={payload['n_members']} "
                  f"sharpe={payload['sharpe_full_L']} "
                  f"p={payload['p_value']} dsr={payload['batch_dsr']} "
                  f"div_delta={payload['diversification_delta']} "
                  f"loo_min={payload['loo_min_sharpe']}")
    # -- burn product (dedupe config rows, last wins)
    cfg_rows = {}
    for line in open(CKPT_CONFIGS, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            cfg_rows[r["config_id"]] = r
    if len(cfg_rows) != BATCH_CELLS:
        print(f"run PARTIAL: {len(cfg_rows)}/{BATCH_CELLS} configs on "
              f"checkpoint; rerun to complete")
        return 0
    first_member_line = [l for l in open(CKPT_MEMBERS, encoding="utf-8")
                         if l.strip()][0]
    burn = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF), "roster_sha16": drill.ROSTER_SHA16,
        "drill_results_sha16": _sha16(DRILL_RESULTS),
        "window": {"start": str(st["idx"][st["w0"]].date()),
                   "end": str(st["idx"][st["wend"]].date()),
                   "base_date": str(st["idx"][st["wbase"]].date()),
                   "n_days": st["n_win_days"]},
        "sentinel_candidate_id": roster["rows"][0]["candidate_id"],
        "sentinel_sha256": json.loads(first_member_line)["sha256"],
        "configs": {cid: r["payload"] for cid, r in cfg_rows.items()},
        "config_shas": {cid: r["sha256"] for cid, r in cfg_rows.items()},
        "ledger_delta": 0, "marks": "+0",
        "audit": {"machine": _machine_id(),
                  "elapsed_sec": round(time.time() - t0, 1),
                  "workers": 1, "stage": "run"},
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    json.dump(_j(burn), open(BURN_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"run DONE: 4/4 configs -> {BURN_JSON} "
          f"(replay+ckpt {t_cfg - t0:.1f}s, configs "
          f"{time.time() - t_cfg:.1f}s)")
    return 0


# -------------------------------------------------------------- finalize
def cmd_finalize() -> int:
    print(f"=== {WAVE} finalize ===")
    if not os.path.exists(BURN_JSON):
        print("FINALIZE-GATE FAIL: burn product absent (run not complete)")
        return 1
    burn = json.load(open(BURN_JSON, encoding="utf-8"))
    roster = drill._load_roster()
    arc_f = _archive_faces()
    st = drill._build_state()
    t0 = time.time()
    monthly_firsts = _monthly_firsts(st)
    dec_dates = _decision_dates(st, monthly_firsts)
    entry_date = dec_dates[0]
    reg = json.load(open(REGIME_STATE, encoding="utf-8"))
    cap = CAP_LADDER.get(reg.get("state"))
    if cap is None:
        print("FINALIZE-GATE FAIL: regime state off-ladder")
        return 1
    # -- determinism leg 1: sentinel sleeve full re-replay (drill caliber)
    srow = roster["rows"][0]
    if srow["candidate_id"] != burn["sentinel_candidate_id"]:
        print("FINALIZE-GATE FAIL: sentinel id drift")
        return 1
    cand = drill._roster_cand(srow)
    template = drill._roster_template(srow)
    eq, trades, _m = drill._wave_run(st, srow["wave"], cand, template)
    with CostPatch(2):
        eq2, _t2, _m2 = drill._wave_run(st, srow["wave"], cand, template)
    s_mp = _member_payload(srow["candidate_id"], srow["wave"], eq, eq2,
                           trades, st, dec_dates)
    s_sha = _payload_sha(s_mp)
    if s_sha != burn["sentinel_sha256"]:
        print(f"FINALIZE-GATE FAIL: sentinel determinism drift "
              f"{s_sha[:12]} != {burn['sentinel_sha256'][:12]}")
        return 2
    # -- determinism leg 2: all-4-config book-math replay from checkpoint
    members = _load_members_ckpt()
    if len(members) != drill.BATCH_N_TRIALS:
        print(f"FINALIZE-GATE FAIL: member checkpoint {len(members)}/18")
        return 1
    win_rets1 = {cid: pd.Series(p["win_rets1"])
                 for cid, p in members.items()}
    C = pd.DataFrame(win_rets1).corr()
    checked = {}
    for delta in DELTAS:
        for rule in RULES:
            cfg_id = _cfg_id(delta, rule)
            payload = _compute_config(cfg_id, delta, rule, members, arc_f,
                                       st, C, monthly_firsts, entry_date,
                                       cap, reg.get("state"))
            got = _payload_sha(payload)
            if got != burn["config_shas"][cfg_id]:
                print(f"FINALIZE-GATE FAIL: book-math determinism drift "
                      f"{cfg_id} {got[:12]} != "
                      f"{burn['config_shas'][cfg_id][:12]}")
                return 2
            checked[cfg_id] = payload
    print(f"  determinism: sentinel sha match + 4/4 config shas match "
          f"[{time.time() - t0:.1f}s]")
    # -- batch FDR + four-dim composite (frozen constants import)
    member_metrics, batch_p = {}, {}
    for cfg_id, p in checked.items():
        member_metrics[cfg_id] = {
            "ret": {
                "sharpe_full_L": p["sharpe_full_L"],
                "annualized_ret_L": p["annualized_ret_L"],
                "return_ceiling_O1126": p["return_ceiling_O1126"],
                "beat6m_rate_L": p["beat6m"]["rate"],
                "beat12m_rate_L": None,      # window < 12m (drill caliber)
            },
            "robust": {
                "cost_x2_sharpe_L": p["sharpe_x2_L"],
                "regime_min_sharpe_L": p["regime_min_sharpe"],
                "bootstrap_ci_low_L": p["bootstrap_ci_low_L"],
            },
            "anti_overfit": {
                "family_pbo": p["family_pbo_mean"],
                "d6_max_abs_corr": p["d6_max_corr"],
            },
            "anti_luck": {"batch_dsr": p["batch_dsr"]},
        }
        batch_p[cfg_id] = p["p_value"]
    g2 = g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS,
                         REFORM_SUB_WEIGHTS, batch_p, q=REFORM_Q_LEVEL)
    if g2.get("error"):
        print(f"FINALIZE-GATE FAIL: reform gate error {g2['error']}")
        return 2
    eligible = {}
    for cfg_id, p in checked.items():
        sc = g2["members"][cfg_id]
        eligible[cfg_id] = bool(
            sc["fdr_pass"] and sc["composite"] is not None
            and p["diversification_delta"] is not None
            and p["diversification_delta"] > 0)
    # -- trials ledger (canonical dict schema; embed-order law)
    led = append_ledger(batch_name=WAVE, batch_trials=BATCH_CELLS,
                        file_name=f"results/portfolio_book/BOOK-{CUTOFF}.json",
                        evidence_cutoff=CUTOFF,
                        note="4 book-config cells (recombination face); "
                             "sleeve replays consume zero generation trials")
    results = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF), "roster_sha16": drill.ROSTER_SHA16,
        "drill_results_sha16": _sha16(DRILL_RESULTS),
        "probe_payload_sha256": PROBE_PAYLOAD_SHA256_PIN,
        "window": burn["window"],
        "cap_pin": {"state": reg.get("state"), "cap": cap,
                    "asof": reg.get("asof"),
                    "source": "results/regime_state.json",
                    "note": "capped face = disclosure only, not composite"},
        "five_member_ew_baseline": {"annualized_ret": arc_f["five_ew_ann"]},
        "sentinel_determinism": {"candidate_id": srow["candidate_id"],
                                 "sha256": s_sha, "match": True},
        "config_determinism": {cid: burn["config_shas"][cid]
                               for cid in checked},
        "configs": checked,
        "member_metrics": member_metrics,
        "batch_p_values": batch_p,
        "g2_reform": _j(g2),
        "eligible_book": eligible,
        "verdict": ("eligible-book" if any(eligible.values())
                    else "judged-negative"),
        "n_eligible": int(sum(eligible.values())),
        "trials_ledger": led,
        "ledger_delta": BATCH_CELLS, "marks": "+0",
        "audit": {"machine": _machine_id(),
                  "elapsed_sec": round(time.time() - t0, 1),
                  "workers": 1, "stage": "finalize"},
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    json.dump(_j(results), open(OUT_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # -- book_cells.csv (4 configs, full columns)
    cols = ["config_id", "delta", "rule", "n_members", "selected",
            "sharpe_full_L", "annualized_ret_L", "return_ceiling_O1126",
            "beat6m_rate", "diversification_delta", "sharpe_x2_L",
            "regime_min_sharpe", "bootstrap_ci_low_L", "loo_min_sharpe",
            "loo_ratio", "family_pbo_mean", "d6_max_corr", "batch_dsr",
            "t_stat", "p_value", "bh_q", "fdr_pass", "composite",
            "eligible_book", "entry_cost", "rebalance_cost_total",
            "rebalance_events", "invalid_sigma_uses", "max_dd_x1",
            "max_dd_x2", "annualized_ret_capped", "sharpe_capped"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(cols) + "\n")
        for cfg_id, p in checked.items():
            sc = g2["members"][cfg_id]
            row = {
                "config_id": cfg_id, "delta": p["delta"], "rule": p["rule"],
                "n_members": p["n_members"],
                "selected": "|".join(p["selected"]),
                "sharpe_full_L": p["sharpe_full_L"],
                "annualized_ret_L": p["annualized_ret_L"],
                "return_ceiling_O1126": p["return_ceiling_O1126"],
                "beat6m_rate": p["beat6m"]["rate"],
                "diversification_delta": p["diversification_delta"],
                "sharpe_x2_L": p["sharpe_x2_L"],
                "regime_min_sharpe": p["regime_min_sharpe"],
                "bootstrap_ci_low_L": p["bootstrap_ci_low_L"],
                "loo_min_sharpe": p["loo_min_sharpe"],
                "loo_ratio": p["loo_ratio"],
                "family_pbo_mean": p["family_pbo_mean"],
                "d6_max_corr": p["d6_max_corr"],
                "batch_dsr": p["batch_dsr"], "t_stat": p["t_stat"],
                "p_value": p["p_value"], "bh_q": sc["bh_q"],
                "fdr_pass": sc["fdr_pass"], "composite": sc["composite"],
                "eligible_book": eligible[cfg_id],
                "entry_cost": p["entry_cost"],
                "rebalance_cost_total": p["rebalance_cost_total"],
                "rebalance_events": p["rebalance_events"],
                "invalid_sigma_uses": p["invalid_sigma_uses"],
                "max_dd_x1": p["max_dd_x1"], "max_dd_x2": p["max_dd_x2"],
                "annualized_ret_capped":
                    p["cap_face"]["annualized_ret_capped"],
                "sharpe_capped": p["cap_face"]["sharpe_capped"],
            }
            fh.write(",".join(str(row[c]) for c in cols) + "\n")
    # -- gate_attrition judgment row (CRLF indent-1 rewrite per r289 law)
    try:
        att = json.load(open(GATE_ATTRITION, encoding="utf-8"))
        att["history"].append({
            "batch": WAVE, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "judgment", "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": led["total"],
            "gates": {
                "bh_fdr_q": {cid: g2["members"][cid]["bh_q"]
                             for cid in checked},
                "fdr_pass": {cid: g2["members"][cid]["fdr_pass"]
                             for cid in checked},
                "diversification_delta": {cid: checked[cid]
                                          ["diversification_delta"]
                                          for cid in checked},
                "eligible_book": eligible,
            },
            "eliminated": None,
            "refs": {"results": OUT_JSON, "prereg": PREREG},
            "note": "4 book-config cells (recombination face, archive "
                    "sleeves); trials ledger +4",
        })
        text = json.dumps(att, ensure_ascii=False, indent=1)
        text = text.replace("\n", "\r\n")
        with open(GATE_ATTRITION, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    except Exception as e:
        print(f"WARN: gate_attrition append failed ({e}) -- ledger + "
              f"results intact, attrition row left for harvest round")
    print(f"finalize DONE -> {OUT_JSON}")
    print(f"  verdict={results['verdict']} "
          f"eligible={results['n_eligible']}/4")
    for cfg_id, p in checked.items():
        sc = g2["members"][cfg_id]
        print(f"  {cfg_id}: sharpe={p['sharpe_full_L']} "
              f"p={p['p_value']} bh_q={sc['bh_q']} "
              f"fdr={sc['fdr_pass']} comp={sc['composite']} "
              f"div_delta={p['diversification_delta']} "
              f"eligible={eligible[cfg_id]}")
    print(f"  trials ledger: {led['prev_total']} -> {led['total']} "
          f"(+{BATCH_CELLS})")
    return 0


# --------------------------------------------------------------- selftest
def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic offline fixtures) ===")
    fails = []

    def chk(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # (a) greedy selection: twin rejected, order kept, delta sensitivity
    rng = np.random.default_rng(7)
    n = 200
    idx = list(pd.date_range("2026-01-05", periods=n, freq="B"))
    a = pd.Series(rng.normal(0.001, 0.01, n), index=idx)
    b = a * 1.0                                   # corr == 1 with A
    c = pd.Series(rng.normal(0.0008, 0.01, n), index=idx)
    d = 0.6 * a + 0.8 * pd.Series(rng.normal(0, 0.008, n), index=idx)
    R = pd.DataFrame({"A": a, "B": b, "C": c, "D": d})
    C = R.corr()
    comp_rank = [("A", 0.9), ("B", 0.8), ("C", 0.7), ("D", 0.6)]
    sel, rej = _select_greedy(comp_rank, C, 0.50)
    chk("greedy d=0.50: twin B + corr~0.68 D rejected, C admitted",
        sel == ["A", "C"])
    chk("greedy d=0.50: blocker recorded",
        bool(rej) and rej[0]["candidate_id"] == "B"
        and rej[0]["blocked_by"] == "A")
    sel2, _ = _select_greedy(comp_rank, C, 0.70)
    chk("greedy d=0.70: corr-1.0 twin still rejected", "B" not in sel2)
    chk("greedy d=0.70: corr<0.70 D admitted", sel2 == ["A", "C", "D"])
    # (b) monthly firsts on a synthetic calendar
    idx2 = list(pd.date_range("2025-12-31", periods=90, freq="B"))
    st2 = {"idx": idx2, "w0": 1, "wend": len(idx2) - 1,
           "n_win_days": len(idx2) - 1, "wbase": 0}
    mf = _monthly_firsts(st2)
    months = {idx2[1 + k].month for k in mf}
    chk("monthly firsts: first == 0, one per month",
        mf[0] == 0 and len(mf) == len(months))
    # (c) IVOL target weights: normalization + invalid-sigma demotion
    sig_dec = {"M1": {"2025-12-31": 0.01}, "M2": {"2025-12-31": 0.02},
               "M3": {"2025-12-31": None}}
    w, n_inv = _target_weights("IVOL", ["M1", "M2", "M3"], sig_dec,
                               "2025-12-31", 3)
    chk("IVOL weights sum to 1", abs(float(w.sum()) - 1.0) < 1e-12)
    chk("IVOL low-vol member heaviest", w[0] > w[1])
    chk("IVOL invalid sigma counted", n_inv == 1)
    chk("IVOL demoted member ~= equal share",
        abs(w[2] - 1.0 / 3.0) < 0.05)
    w_ew, _ = _target_weights("EW", ["M1", "M2"], {}, "x", 2)
    chk("EW weights equal", bool(np.allclose(w_ew, [0.5, 0.5])))
    # (d) single-member book identity: entry cost once, no rebalance cost
    r1 = np.array([[0.01], [0.02], [-0.005], [0.007]])
    sim = _simulate_book(["M1"], "EW", r1, r1, {"M1": {}},
                         ["d0", "d1", "d2", "d3"], [0, 2], "d0")
    chk("single-member book: entry cost on day 0",
        abs(sim["r1"][0] - (0.01 - X1_RATE)) < 1e-12)
    chk("single-member book: no rebalance cost (w==1 identity)",
        abs(sim["r1"][1] - 0.02) < 1e-12
        and abs(sim["r1"][2] + 0.005) < 1e-12)
    chk("x2 leg doubles entry cost",
        abs(sim["r2"][0] - (0.01 - 2 * X1_RATE)) < 1e-12)
    chk("cost ledger: events counted",
        sim["rebalance_events"] == 2 and sim["entry_cost"] == X1_RATE)
    # (e) two-member drift formula (non-rebalance day, net denominator)
    r1b = np.array([[0.01, -0.01], [0.0, 0.0]])
    simb = _simulate_book(["M1", "M2"], "EW", r1b, r1b,
                          {"M1": {}, "M2": {}}, ["d0", "d1"], [], "d0")
    rb0 = 0.5 * 0.01 + 0.5 * (-0.01) - X1_RATE
    chk("two-member day0 net = gross - entry",
        abs(simb["r1"][0] - rb0) < 1e-12)
    chk("day0 drift formula (net denominator)",
        abs(simb["w_track"][0][0] - 0.5 * 1.01 / (1.0 - X1_RATE)) < 1e-12
        and abs(simb["w_track"][0][1] - 0.5 * 0.99 / (1.0 - X1_RATE)) < 1e-12)
    chk("day1 zero returns keep drifted weights",
        abs(simb["w_track"][1][0] - simb["w_track"][0][0]) < 1e-12)
    # (f) x2 leg uses the SAME weight path (prereg: x1 face drives weights)
    r2b = np.array([[0.02, -0.02], [0.0, 0.0]])
    simx = _simulate_book(["M1", "M2"], "EW", r1b, r2b,
                          {"M1": {}, "M2": {}}, ["d0", "d1"], [], "d0")
    chk("x2 leg = same weights on x2 returns minus 2x costs",
        abs(simx["r2"][0] - (0.5 * 0.02 + 0.5 * (-0.02) - 2 * X1_RATE))
        < 1e-12)
    # (g) EW diversification_delta == sharpe - arithmetic member mean
    rr = np.array([[0.01, 0.004], [0.012, 0.003], [-0.006, 0.002],
                   [0.008, 0.001], [0.011, 0.005]])
    simc = _simulate_book(["M1", "M2"], "EW", rr, rr,
                          {"M1": {}, "M2": {}},
                          ["d0", "d1", "d2", "d3", "d4"], [0], "d0")
    eq_book = pd.Series(np.concatenate(([1.0],
                                        np.cumprod(1.0 + simc["r1"]))))
    sb = float(sharpe(eq_book))
    s1 = float(sharpe(pd.Series(np.concatenate(
        ([1.0], np.cumprod(1.0 + rr[:, 0]))))))
    s2m = float(sharpe(pd.Series(np.concatenate(
        ([1.0], np.cumprod(1.0 + rr[:, 1]))))))
    ms = {"M1": round(s1, 4), "M2": round(s2m, 4)}
    wm = _w_mean_face("EW", ["M1", "M2"], simc["w_track"])
    delta = _diversification_delta(sb, ms, wm)
    chk("EW diversification_delta identity",
        delta == round(sb - (round(s1, 4) + round(s2m, 4)) / 2, 4))
    # (h) LOO indexing face: drop-M1 == direct two-member book of M2,M3
    r3 = np.column_stack([rr[:, 0], rr[:, 1],
                          np.array([0.002, 0.001, 0.0, 0.003, -0.001])])
    sel3 = ["M1", "M2", "M3"]
    sigd3 = {c: {} for c in sel3}
    dates3 = ["d0", "d1", "d2", "d3", "d4"]
    drop = "M1"
    sel_loo = [c for c in sel3 if c != drop]
    idxs = [sel3.index(c) for c in sel_loo]
    sim_loo = _simulate_book(sel_loo, "EW", r3[:, idxs], r3[:, idxs],
                             sigd3, dates3, [0], "d0")
    ref = _simulate_book(["M2", "M3"], "EW", r3[:, [1, 2]], r3[:, [1, 2]],
                         sigd3, dates3, [0], "d0")
    eq_loo = pd.Series(np.concatenate(([1.0],
                                       np.cumprod(1.0 + sim_loo["r1"]))))
    eq_ref = pd.Series(np.concatenate(([1.0],
                                       np.cumprod(1.0 + ref["r1"]))))
    chk("LOO indexing == direct reference book",
        abs(float(sharpe(eq_loo)) - float(sharpe(eq_ref))) < 1e-12)
    # (i) sigma shift(1) causality: decision-day return excluded
    rets = pd.Series(np.concatenate(
        (rng.normal(0.001, 0.005, 60), [0.5])))   # huge last-day return
    s_raw = rets.rolling(IVOL_WINDOW).std()
    s_shift = s_raw.shift(1)
    chk("sigma shift(1) excludes the decision-day return",
        float(s_shift.iloc[60]) < float(s_raw.iloc[60]))
    # (j) X1_RATE import pin (module import already asserts; face recheck)
    chk("X1_RATE == 0.0013041 (cost_spec import)",
        abs(X1_RATE - 0.0013041) < 1e-15)
    # (k) BH FDR fixture (drill caliber)
    fdr = bh_batch_fdr({"a": 0.001, "b": 0.02, "c": 0.5, "d": None}, q=0.10)
    chk("bh fixture: a passes", fdr["items"]["a"]["fdr_pass"])
    chk("bh fixture: c fails", not fdr["items"]["c"]["fdr_pass"])
    # (l) composite fixture with book-style dicts (extra keys tolerated)
    mm = {f"c{i}": {"ret": {"sharpe_full_L": float(i),
                            "annualized_ret_L": 0.1,
                            "return_ceiling_O1126": 0.01,
                            "beat6m_rate_L": 0.6, "beat12m_rate_L": None},
                    "robust": {"cost_x2_sharpe_L": float(i),
                               "regime_min_sharpe_L": 0.5,
                               "bootstrap_ci_low_L": 0.1},
                    "anti_overfit": {"family_pbo": 0.1,
                                     "d6_max_abs_corr": 0.2},
                    "anti_luck": {"batch_dsr": 0.5},
                    "diversification_delta": 0.3}
         for i in range(1, 4)}
    g2 = g2_reform_fdr4d(mm, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                         {f"c{i}": 0.001 for i in range(1, 4)},
                         q=REFORM_Q_LEVEL)
    chk("reform fixture: no error", not g2.get("error"))
    chk("reform fixture: monotone rank",
        g2["members"]["c3"]["composite"] > g2["members"]["c1"]["composite"])
    # (m) t/p direction (higher sharpe -> lower p)
    t_hi = t_from_sharpe(3.0, 176)
    t_lo = t_from_sharpe(1.0, 176)
    chk("t face direction", t_hi > t_lo)
    chk("p = 1 - Phi(t) in (0,1)",
        0.0 < 1.0 - float(_norm_cdf(t_hi)) < 1.0)
    # (n) cap face halves (disclosure math)
    cf = _cap_face(np.array([0.01, -0.02, 0.03, 0.01]), 0.5)
    chk("cap face: scaled-series sharpe computed",
        cf["sharpe_capped"] is not None
        and abs(cf["annualized_ret_capped"]) < 10.0)
    # (o) monthly-start annualized distribution (monotone face)
    eq_d = pd.Series(np.linspace(1.0, 1.5, 10))
    msa = _monthly_start_ann(eq_d, {"n_win_days": 9}, [0, 4])
    chk("monthly-start dist: best >= median >= worst",
        msa["best"] >= msa["median"] >= msa["worst"])
    n_fail = len(fails)
    print(f"selftest: {'ALL PASS' if not n_fail else f'{n_fail} FAIL'}")
    return 0 if not n_fail else 1


# ------------------------------------------------------------------ status
def cmd_status() -> int:
    m = len(_ckpt_ids(CKPT_MEMBERS, "candidate_id"))
    cfgs = _ckpt_ids(CKPT_CONFIGS, "config_id")
    print(f"{WAVE}: members {m}/18, configs {len(cfgs)}/4")
    print(f"  manifest: {'present' if os.path.exists(MANIFEST) else 'absent'}")
    print(f"  burn: {'present' if os.path.exists(BURN_JSON) else 'absent'}")
    print(f"  final: {'present' if os.path.exists(OUT_JSON) else 'absent'}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=WAVE)
    ap.add_argument("cmd", choices=["prep", "run", "finalize", "selftest",
                                    "status"])
    a = ap.parse_args(argv)
    try:
        if a.cmd == "prep":
            return cmd_prep()
        if a.cmd == "run":
            return cmd_run()
        if a.cmd == "finalize":
            return cmd_finalize()
        if a.cmd == "selftest":
            return cmd_selftest()
        return cmd_status()
    except KeyboardInterrupt:
        print("interrupted (checkpoint preserved)")
        return 2
    except Exception as e:                       # machinery error, never mask
        import traceback
        traceback.print_exc()
        print(f"ERROR: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
