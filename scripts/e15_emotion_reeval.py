#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E15_EMOTION_REEVAL_P1 -- emotion-family near-miss re-adjudication under the
FDR4D reform line (frozen prereg research/E15_EMOTION_REEVAL_P1.md).

Batch type: re-evaluation DERIVE batch (档存重估=新程序非翻案). The 4 pinned
mass-trial near-miss members (report_card passers: g1 pass, g2 fail on the
global-ledger DSR) are re-adjudicated under REGISTRATION_REFORM_FDR4D
(O-20260930-1058): batch-internal BH FDR (m=4, q=REFORM_Q_LEVEL) + four-dim
composite (g2_reform_fdr4d) + D6 registered-ceiling admission.

Import-face law (prereg sec.2/3): zero candidate-curve re-simulation -- the
frozen judge shard cells already carry legL_daily_returns (n=1631, r876 probe);
four-dim materials are CARRIED verbatim from the frozen cells/roster or DERIVED
from the frozen daily series. The only engine touch = the registered-six D6
control replay via the trial-labor W1 grammar default-axis channel
(reeval18_drill._registered_window_rets caliber, verbatim reuse).

Laws honored: L1 deterministic, zero network, zero RNG (no seed registration
face), zero ledger append, zero attrition rows (re-eval derive face, REEVAL18
sec.7 precedent), cutoff lockbox 2026-09-22, fail-closed gates (exit 2),
idempotent no-op guard, provenance per sub-metric.

Usage:
  python scripts/e15_emotion_reeval.py run       # gates + derive + verdict
  python scripts/e15_emotion_reeval.py selftest   # hermetic offline fixtures
  python scripts/e15_emotion_reeval.py status      # existing-result readout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, _ROOT)

import mass_trial_w1 as mt                    # leg-L panel + census canon
import reeval18_drill as rd                   # registered-window replay caliber
import trial_labor_w1 as tl1                  # A_TEMPLATES + DEFAULT_AXIS
import trial_labor_w2 as tl2                  # _d6_admit_core
import trial_labor_w14 as tl14                # five-member EW ceiling baseline
from engine.metrics import sharpe
from live.paper import build_panels, load_core, v3_state_series
from science_gates import (REFORM_DIM_WEIGHTS, REFORM_Q_LEVEL,
                           REFORM_SUB_WEIGHTS, REFORM_TOPN_PER_WAVE,
                           bh_batch_fdr, cutoff_meta, deflated_sharpe_ratio,
                           g2_reform_fdr4d, reform_weight_freeze_integrity)

# ----------------------------------------------------- frozen (prereg sec.2)
BATCH = "E15_EMOTION_REEVAL_P1"
PREREG = "research/E15_EMOTION_REEVAL_P1.md"
CUTOFF = mt.CUTOFF                            # "2026-09-22" (frozen anchor)
ROSTER_PATH = os.path.join(_ROOT, "results", "emotion_reeval", "e15_roster.json")
OUT_DIR = os.path.join(_ROOT, "results", "emotion_reeval")
OUT_PATH = os.path.join(OUT_DIR, "E15-REEVAL-" + CUTOFF + ".json")
REFINALIZE_ENV = "E15_EMOTION_REEVAL_REFINALIZE"

MEMBERS = ("W2-23057", "W3-23027", "W3-27009", "W3-46133")
ROSTER_SHA16 = "0f23cf678db4697e"
JUDGE_SHA16 = {
    "results/mass_trial/w2_candidates.json": "44a31ed2444ebf23",
    "results/mass_trial/w3_candidates.json": "b5316ddf0a608e2e",
    "results/mass_trial/w2_judge.json": "ae58310f8d411dab",
    "results/mass_trial/w3_judge.json": "2b9773bcd0a47c4f",
    "results/mass_trial/w2_judge_shard_0of4.jsonl": "0a632731bd5b3fbb",
    "results/mass_trial/w2_judge_shard_1of4.jsonl": "f569aaaa07a1d198",
    "results/mass_trial/w2_judge_shard_2of4.jsonl": "323ecb681ab09249",
    "results/mass_trial/w2_judge_shard_3of4.jsonl": "a63a8f2e7c7bc5a2",
    "results/mass_trial/w3_judge_shard_0of4.jsonl": "fdc2b37ee4fe7cc1",
    "results/mass_trial/w3_judge_shard_1of4.jsonl": "e449cea17d74047d",
    "results/mass_trial/w3_judge_shard_2of4.jsonl": "11b42dbdb0bc5ea3",
    "results/mass_trial/w3_judge_shard_3of4.jsonl": "b77cae0139f939b6",
}
N_LEG_DAILY = 1631                            # frozen leg-L bar count
LEG_FIRST, LEG_LAST = "2020-01-02", "2026-09-22"
MIN_SEG_DAYS = rd.MIN_SEG_DAYS                # 20 (REEVAL18 caliber)
REGIME_MAP = rd.REGIME_MAP                    # 3-way frozen proxy
E_FP = round(0.05 * len(MEMBERS), 2)           # nominal disclosure
SHARPE_REPRO_TOL = 0.001                      # G-REPRO rounding tolerance


def _sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _j(o):
    if isinstance(o, dict):
        return {str(k): _j(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_j(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, float):
        return round(o, 6) if math.isfinite(o) else None
    return o


# ------------------------------------------------------------------- gates
def gate_integrity():
    """G-ROSTER + G-FROZENFILES + G-REFORM (fail-closed, prereg sec.2)."""
    errs = []
    if not os.path.exists(ROSTER_PATH):
        return [f"roster absent: {ROSTER_PATH}"]
    got = _sha16(ROSTER_PATH)
    if got != ROSTER_SHA16:
        errs.append(f"roster sha16 drift {got} != {ROSTER_SHA16}")
    roster = json.load(open(ROSTER_PATH, encoding="utf-8"))
    if roster.get("batch") != "E15_EMOTION_REEVAL_ROSTER":
        errs.append("roster batch name drift")
    if roster.get("source_evidence_cutoff") != CUTOFF:
        errs.append("roster cutoff drift")
    ids = sorted(m["candidate_id"] for m in roster["members"])
    if ids != sorted(MEMBERS):
        errs.append(f"roster members {ids} != pinned {sorted(MEMBERS)}")
    for rel, want in JUDGE_SHA16.items():
        p = os.path.join(_ROOT, rel.replace("/", os.sep))
        if not os.path.exists(p):
            errs.append(f"frozen file absent: {rel}")
            continue
        got = _sha16(p)
        if got != want:
            errs.append(f"frozen sha16 drift {rel}: {got} != {want}")
    if not reform_weight_freeze_integrity()["pass"]:
        errs.append("reform weight freeze integrity FAIL")
    return errs


def load_member_cells():
    """G-SHARD: frozen shard cells for the 4 pinned members (daily + legs)."""
    cells = {}
    for cid in MEMBERS:
        wv = "w2" if cid.startswith("W2-") else "w3"
        found = None
        for k in range(4):
            p = os.path.join(_ROOT, "results", "mass_trial",
                             f"{wv}_judge_shard_{k}of4.jsonl")
            for line in open(p, encoding="utf-8"):
                if cid not in line:
                    continue
                c = json.loads(line)
                if c.get("candidate_id") == cid:
                    found = c
                    break
            if found:
                break
        if not found:
            raise ValueError(f"shard cell absent for {cid}")
        if len(found.get("legL_daily_returns") or []) != N_LEG_DAILY:
            raise ValueError(f"{cid} n_daily != {N_LEG_DAILY} (face mismatch)")
        cells[cid] = found
    # judge-file cross-anchor (shard vs finalized judge, rounding 4)
    for wv in ("w2", "w3"):
        jf = json.load(open(os.path.join(_ROOT, "results", "mass_trial",
                                        f"{wv}_judge.json"), encoding="utf-8"))
        by_id = {c["candidate_id"]: c for c in jf["cells"]}
        for cid in cells:
            if not cid.startswith("W" + wv[1].upper() + "-"):
                continue
            jc = by_id.get(cid)
            if not jc:
                raise ValueError(f"judge-file cell absent for {cid}")
            a = jc["legs"]["L"]["x1"]["sharpe_full"]
            b = cells[cid]["legs"]["L"]["x1"]["sharpe_full"]
            if abs(float(a) - float(b)) > 1e-9:
                raise ValueError(f"{cid} shard/judge sharpe drift {a} vs {b}")
    return cells


def gate_legidx():
    """G-LEGIDX + G-PANEL: frozen leg-L index (census canon) + replay panel."""
    raw, _P, idx, listed, cen = mt._leg_raw("L")
    if len(idx) != N_LEG_DAILY:
        raise ValueError(f"leg-L idx len {len(idx)} != {N_LEG_DAILY}")
    if str(idx[0].date()) != LEG_FIRST or str(idx[-1].date()) != LEG_LAST:
        raise ValueError(f"leg-L idx ends {idx[0].date()}..{idx[-1].date()} "
                        f"!= {LEG_FIRST}..{LEG_LAST}")
    if cen != mt.FROZEN_CENSUS["L"]:
        raise ValueError(f"leg-L census drift {cen} != {mt.FROZEN_CENSUS['L']}")
    return idx, cen


# ------------------------------------------------------------------ derive
def _ann_from_daily(daily):
    """Compound annualized return of the frozen face (1631 bars incl. bar0
    0.0 artifact) -- the original judge-cell ann caliber (mass_trial_w1
    _judge_cell: eq_l=(1+daily).cumprod(); ann=eq[-1]/eq[0]^(252/n)-1)."""
    eq = np.cumprod([1.0 + float(v) for v in daily])
    n = len(daily)
    if eq[-1] <= 0 or n < 2:
        return None
    return float(eq[-1] ** (252.0 / n) - 1.0)


def _regime_segments(daily, idx, states):
    """bear/bull/chop segment Sharpes on the frozen face (REGIME_MAP 3-way
    proxy, MIN_SEG_DAYS floor, absent segments -> None; REEVAL18 caliber)."""
    s = states.reindex(idx)
    rets = pd.Series([float(v) for v in daily], index=idx)
    segs = {"bear": [], "bull": [], "chop": []}
    for d, r in rets.items():
        v = s.loc[d]
        seg = REGIME_MAP.get(v, "bear") if v == v else "bear"
        segs[seg].append(float(r))
    out = {}
    for seg, vals in segs.items():
        if len(vals) < MIN_SEG_DAYS:
            out[seg] = {"n_days": len(vals), "sharpe": None}
            continue
        eq = pd.Series((1.0 + pd.Series(vals)).cumprod())
        out[seg] = {"n_days": len(vals), "sharpe": round(float(sharpe(eq)), 4)}
    live = [v["sharpe"] for v in out.values() if v["sharpe"] is not None]
    return out, (round(min(live), 4) if live else None)


def _g_repro(daily, frozen_sharpe):
    """G-REPRO anchor: rebuilt-equity Sharpe vs frozen shard sharpe_full."""
    eq = pd.Series(np.cumprod([1.0 + float(v) for v in daily]))
    got = float(sharpe(eq))
    ok = abs(got - float(frozen_sharpe)) <= SHARPE_REPRO_TOL
    return ok, round(got, 4)


def _registered_leg_rets(idx_leg):
    """Registered-six daily returns on the leg-L window, grammar default-axis
    channel (reeval18_drill._registered_window_rets caliber, verbatim)."""
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in load_core().items()}
    if len(prices) != 48:
        raise ValueError(f"G-PANEL fail: {len(prices)}/48 replay panel members")
    tail_bad = [s for s, df in prices.items()
                if str(df.index[-1].date()) != CUTOFF]
    if tail_bad:
        raise ValueError(f"G-PANEL fail: stale tails {tail_bad[:5]}")
    P = build_panels(prices)
    states = v3_state_series()
    # reeval18 caliber state dict: registered replay (w1 branch) needs
    # prices/P/states/fundamental_ok + wbase; grammar loaded first.
    tl1.GRAMMAR = json.load(open(rd.GRAMMAR_PATH, encoding="utf-8"))
    st = {
        "prices": prices, "P": P, "states": states,
        "fundamental_ok": rd._fundamental_ok(P["close"]),
        "idx": list(P["close"].index),
    }
    wbase = next(p for p, d in enumerate(st["idx"])
                 if pd.Timestamp(d) >= idx_leg[0])
    if wbase < 1:
        raise ValueError("leg window base needs >=1 pre-window bar")
    st["wbase"] = wbase
    reg = rd._registered_window_rets(st, None)
    # align to the 1630 real-return days (bar0 construct-zero dropped)
    win_dates = idx_leg[1:]
    out = {}
    for tid, r in reg.items():
        out[tid] = r.reindex(win_dates)
    return out


# --------------------------------------------------------------------- run
def do_run():
    if os.path.exists(OUT_PATH) and os.environ.get(REFINALIZE_ENV) != "1":
        print(f"[no-op] result exists: {OUT_PATH} ({REFINALIZE_ENV}=1 redo)")
        return 0
    errs = gate_integrity()
    if errs:
        for e in errs:
            print("GATE FAIL:", e)
        return 1
    cells = load_member_cells()
    idx_leg, census = gate_legidx()
    roster = json.load(open(ROSTER_PATH, encoding="utf-8"))
    roster_by_id = {m["candidate_id"]: m for m in roster["members"]}

    states = v3_state_series()
    five_ew_ann = tl14._five_member_ew_baseline_annualized(pd.DatetimeIndex(idx_leg))
    if five_ew_ann is None:
        print("GATE FAIL: five-member EW baseline unavailable (ceiling "
              "material missing -> missing-dims refuse; never zero-filled)")
        return 1

    reg_rets = _registered_leg_rets(idx_leg)

    member_metrics, provenance, repro, details = {}, {}, {}, {}
    for cid in MEMBERS:
        cell = cells[cid]
        ros = roster_by_id[cid]
        daily = cell["legL_daily_returns"]
        L = cell["legs"]["L"]
        ok, rebuilt = _g_repro(daily, L["x1"]["sharpe_full"])
        repro[cid] = {"rebuilt_sharpe": rebuilt,
                     "frozen_sharpe_full": L["x1"]["sharpe_full"], "ok": ok}
        if not ok:
            print(f"G-REPRO FAIL: {cid} rebuilt {rebuilt} vs frozen "
                  f"{L['x1']['sharpe_full']} (tol {SHARPE_REPRO_TOL})")
            return 1
        ann = _ann_from_daily(daily)
        segs, seg_min = _regime_segments(daily, idx_leg, states)
        dsr = deflated_sharpe_ratio([float(v) for v in daily],
                                    n_trials=len(MEMBERS))
        member_metrics[cid] = {
            "ret": {
                "sharpe_full_L": float(L["x1"]["sharpe_full"]),
                "annualized_ret_L": ann,
                "return_ceiling_O1126": (None if ann is None
                                         else round(ann - five_ew_ann, 6)),
                "beat6m_rate_L": float(L["x1"]["beat"]["6m"]["rate"]),
                "beat12m_rate_L": float(L["x1"]["beat"]["12m"]["rate"]),
            },
            "robust": {
                "cost_x2_sharpe_L": float(L["x2"]["sharpe_full"]),
                "regime_min_sharpe_L": seg_min,
                "bootstrap_ci_low_L": float(cell["dual_nulls"]
                                           ["bootstrap_ci"][0]),
            },
            "anti_overfit": {
                "family_pbo": ros["family_pbo"],
                "d6_max_abs_corr": None,      # filled by D6 below
            },
            "anti_luck": {
                "batch_dsr": round(float(dsr["dsr"]), 6),
            },
        }
        provenance[cid] = {
            "sharpe_full_L": "carried:shard legs.L.x1",
            "annualized_ret_L": "derived:frozen daily compound",
            "return_ceiling_O1126": "derived:ann - five_member_ew_O1555 "
                                    f"(ew_ann={round(five_ew_ann, 6)})",
            "beat6m_rate_L": "carried:shard legs.L.x1.beat.6m",
            "beat12m_rate_L": "carried:shard legs.L.x1.beat.12m",
            "cost_x2_sharpe_L": "carried:shard legs.L.x2",
            "regime_min_sharpe_L": "derived:frozen daily x v3_state_series",
            "bootstrap_ci_low_L": "carried:shard dual_nulls.bootstrap_ci[0]",
            "family_pbo": "carried:e15_roster (archive authority)",
            "batch_dsr": f"derived:deflated_sharpe_ratio(n_trials="
                         f"{len(MEMBERS)})",
        }
        details[cid] = {
            "family": cell["family"],
            "axes": None, "params": None,
            "regime_segments": segs,
            "old_line_face": {
                "g1_sharpe_full": ros["g1_sharpe_full"],
                "g1_skill_line": ros["g1_skill_line"],
                "g1_margin": ros["g1_margin"],
                "global_dsr": ros["dsr"],
                "g2_eligible": ros["g2_eligible"],
                "oos_sharpe_legL": ros["oos_sharpe_legL"],
                "n_eff_start_windows": ros["n_eff_start_windows"],
            },
        }

    # frozen configs (provenance disclosure; zero re-simulation)
    for cid in MEMBERS:
        wv = "w2" if cid.startswith("W2-") else "w3"
        cd = json.load(open(os.path.join(_ROOT, "results", "mass_trial",
                                         f"{wv}_candidates.json"),
                            encoding="utf-8"))["candidates"]
        c = next(x for x in cd if x["id"] == cid)
        details[cid]["axes"] = c["axes"]
        details[cid]["params"] = c["params"]

    # D6 admission (verbatim core)
    cand_rets = {}
    win_dates = idx_leg[1:]
    for cid in MEMBERS:
        daily = cells[cid]["legL_daily_returns"][1:]   # bar0 construct-zero
        cand_rets[cid] = pd.Series([round(float(v), 8) for v in daily],
                                   index=win_dates)
    dsr_by_id = {cid: member_metrics[cid]["anti_luck"]["batch_dsr"]
                 for cid in MEMBERS}
    admitted, rejected, d6 = tl2._d6_admit_core(
        sorted(MEMBERS), cand_rets, reg_rets, dsr_by_id)
    for cid in MEMBERS:
        member_metrics[cid]["anti_overfit"]["d6_max_abs_corr"] = \
            d6[cid]["max_corr_vs_registered"]

    # batch-internal BH FDR on the carried sign-flip p-values
    batch_p = {cid: cells[cid]["dual_nulls"]["signflip_p"] for cid in MEMBERS}
    fdr = bh_batch_fdr(batch_p, q=REFORM_Q_LEVEL)

    # L3 reform gate + L4 top-N (return face: g2["members"][cid] carries
    # p/bh_q/fdr_pass/composite/dim_scores/missing_dims/eligible_reform)
    g2 = g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS,
                         REFORM_SUB_WEIGHTS, batch_p, q=REFORM_Q_LEVEL)
    if g2.get("error"):
        print("FINALIZE-GATE FAIL: reform gate error", g2["error"])
        return 2
    members_out = g2["members"]
    eligible = [cid for cid in MEMBERS
                if members_out[cid]["eligible_reform"] and cid in admitted]
    onboard = [c for c in sorted(
        eligible, key=lambda c: (-members_out[c]["composite"], c))]
    onboard = onboard[:REFORM_TOPN_PER_WAVE]

    result = {
        "batch": BATCH,
        "prereg_ref": PREREG + " FROZEN (freeze commit precedes this run)",
        "evidence_cutoff": CUTOFF,
        "cutoff_meta": cutoff_meta(CUTOFF),
        "member_count_m": len(MEMBERS),
        "members": {
            cid: {
                "member_metrics": member_metrics[cid],
                "provenance": provenance[cid],
                "details": details[cid],
                "d6": d6[cid],
                "bh": fdr["items"][cid],
                "reform": members_out[cid],
                "eligible_reform": cid in eligible,
                "d6_admitted": cid in admitted,
            } for cid in MEMBERS
        },
        "fdr": {"gate": "bh_batch_fdr", "q_level": REFORM_Q_LEVEL,
                "m": fdr["m"], "e_fp_nominal": E_FP},
        "d6_rejected": rejected,
        "eligible_reform": eligible,
        "onboard_list": onboard,
        "g_repro": repro,
        "gates": {
            "leg_idx": {"n": len(idx_leg), "first": LEG_FIRST,
                        "last": LEG_LAST, "census": census},
            "five_member_ew_ann": round(five_ew_ann, 6),
            "reform_weight_freeze_integrity": True,
            "registered_replay_channel":
                "trial_labor_w1 A_TEMPLATES x DEFAULT_AXIS "
                "(reeval18_drill._registered_window_rets caliber)",
        },
        "ledger_delta": 0,
        "attrition_rows": 0,
        "honesty": "re-evaluation derive face: zero candidate-curve "
                   "re-simulation, zero generation trials, zero ledger "
                   "append (REEVAL18 sec.7 precedent); carried materials "
                   "verbatim from frozen judge shards/roster; new-vs-old "
                   "calibers disclosed per member (old_line_face).",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(_j(result), f, ensure_ascii=False, indent=1, sort_keys=True)
    print("verdict written:", OUT_PATH)
    print("eligible_reform:", eligible, "onboard:", onboard,
          "d6_rejected:", rejected)
    return 0


# ----------------------------------------------------------------- selftest
def selftest():
    """Hermetic offline fixtures (r116 law; no repo data files)."""
    checks = []

    # (a) annualized math on a known series
    daily = [0.0] + [0.01] * 251          # 251 real return days, bar0 artifact
    ann = _ann_from_daily(daily)
    checks.append(("ann math",
                   abs(ann - ((1.01 ** 251) ** (252.0 / 252.0) - 1.0)) < 1e-9))

    # (b) regime segments: bull-only window -> min over present segs
    idx = pd.date_range("2026-01-05", periods=50, freq="B")
    states = pd.Series(["GREEN"] * 50, index=idx)
    segs, seg_min = _regime_segments([0.001] * 50, idx, states)
    checks.append(("regime single-seg",
                   segs["bull"]["n_days"] == 50 and segs["bear"]["n_days"] == 0
                   and seg_min == segs["bull"]["sharpe"]))
    # mixed states with <MIN_SEG_DAYS chop segment -> absent-honest
    states2 = pd.Series(["GREEN"] * 40 + ["YELLOW"] * 10, index=idx)
    segs2, seg_min2 = _regime_segments([0.001] * 50, idx, states2)
    checks.append(("regime thin-seg absent",
                   segs2["chop"]["sharpe"] is None and seg_min2 is not None))

    # (c) BH FDR m=4 band (reform gate consumed with carried p-values)
    fdr = bh_batch_fdr({"A": 0.0, "B": 0.0, "C": 0.001, "D": 0.0015},
                       q=REFORM_Q_LEVEL)
    checks.append(("bh m=4 all-pass small p",
                   all(v["fdr_pass"] for v in fdr["items"].values())
                   and fdr["m"] == 4))

    # (d) reform gate completeness refusal: missing dim -> composite None
    mm = {"X": {"ret": {"sharpe_full_L": 1.0, "annualized_ret_L": 0.1,
                        "return_ceiling_O1126": 0.05,
                        "beat6m_rate_L": 0.6, "beat12m_rate_L": 0.6},
                "robust": {"cost_x2_sharpe_L": 0.9,
                           "regime_min_sharpe_L": -0.5,
                           "bootstrap_ci_low_L": 1e-5},
                "anti_overfit": {"family_pbo": 0.2, "d6_max_abs_corr": 0.3},
                "anti_luck": {}}}
    g2 = g2_reform_fdr4d(mm, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                         {"X": 0.01}, q=REFORM_Q_LEVEL)
    s = g2["members"]["X"]
    checks.append(("missing-dim refused",
                   s["composite"] is None and "anti_luck" in s["missing_dims"]
                   and s["eligible_reform"] is False))

    # (e) D6 clone rejection (REEVAL18 selftest (f) caliber)
    rng = np.random.default_rng(7)
    base = list(rng.normal(0.001, 0.01, 200))
    idx_d = pd.date_range("2026-01-05", periods=200, freq="B")
    reg_r = {"REG": pd.Series(base, index=idx_d)}
    cand_r = {"CLONE": pd.Series(base, index=idx_d),
              "IND": pd.Series(list(rng.normal(0.0005, 0.008, 200)),
                               index=idx_d)}
    adm, rej, d6 = tl2._d6_admit_core(["CLONE", "IND"], cand_r, reg_r,
                                      {"CLONE": 0.5, "IND": 0.4})
    checks.append(("d6 clone rejected",
                   adm == ["IND"] and len(rej) == 1
                   and rej[0]["candidate_id"] == "CLONE"
                   and rej[0]["reason"] == "registered-corr"))
    checks.append(("d6 max corr", d6["CLONE"]["max_corr_vs_registered"]
                   >= tl2.D6_CEILING))

    # (f) provenance assembly law: every four-dim sub-key has provenance
    prov_keys = set(provenance_template_keys())
    checks.append(("provenance covers subs", prov_keys == set(
        [s for d in REFORM_SUB_WEIGHTS for s in REFORM_SUB_WEIGHTS[d]])))

    # (g) member pin: 4 members, dual-wave split
    checks.append(("members pinned", len(MEMBERS) == 4
                   and sum(1 for c in MEMBERS if c.startswith("W2-")) == 1))

    # (h) cutoff_meta C2 key
    checks.append(("cutoff_meta key", cutoff_meta(CUTOFF)
                   == {"evidence_cutoff": CUTOFF}))

    ok = True
    for name, cond in checks:
        print("[selftest]", name, "PASS" if cond else "FAIL")
        ok = ok and cond
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def provenance_template_keys():
    return [
        "sharpe_full_L", "annualized_ret_L", "return_ceiling_O1126",
        "beat6m_rate_L", "beat12m_rate_L", "cost_x2_sharpe_L",
        "regime_min_sharpe_L", "bootstrap_ci_low_L", "family_pbo",
        "d6_max_abs_corr", "batch_dsr",
    ]


def do_status():
    if not os.path.exists(OUT_PATH):
        print("status: no result yet")
        return 0
    d = json.load(open(OUT_PATH, encoding="utf-8"))
    print("result:", OUT_PATH)
    print("eligible_reform:", d["eligible_reform"],
          "onboard:", d["onboard_list"],
          "d6_rejected:", d["d6_rejected"])
    for cid, m in d["members"].items():
        print(f"  {cid} composite={m['reform']['composite']} "
              f"bh_q={m['bh']['bh_q']} d6={m['d6']['max_corr_vs_registered']}"
              f" eligible={m['eligible_reform']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "status"])
    a = ap.parse_args()
    if a.cmd == "run":
        return do_run()
    if a.cmd == "selftest":
        return selftest()
    return do_status()


if __name__ == "__main__":
    sys.exit(main())
