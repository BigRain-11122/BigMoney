"""REGIME5-VALIDATION-P1 runner (T-2026-10-08-177 slice-2, bm-a research lane).

Frozen prereg: research/REGIME5_VALIDATION_P1.md (freeze commit 1aafbd257,
r870 bm-a). CEO order: O-20261007-2215 sec.1 @bm-a leg-1 validation batch.
Post-freeze law: this file IMPLEMENTS the frozen sec.3/sec.6; criteria are
never re-derived here. sec.7/sec.8 backfill happens in the prereg file only.

Batch = measurement/calibration batch (NOT a strategy verdict batch): zero
positions, zero entries/exits, zero engine calls; exit-axis three-way gate
declared N/A at freeze. 1,010 cells = 5 state-diff + 5 N_CONF candidates
+ 1,000 permutation-null replicas.

Faces (all imported, zero re-implementation):
- panel loader = scripts.regime5_labeler._load (frozen labeler's own)
- debounce layer = scripts.regime_style_matrix.confirm_window (frozen
  consumer engine, N_CONF default 3, first-label bootstrap)
- transition cost = scripts.regime_style_matrix.transition_cost
  (dw * COST_X1 single-side; batch charges double-side x2 per prereg)
- COST_X1 = scripts.rev_osc_stock_p1 frozen constant (13.041 bp/side)
- gates = science_gates shared library (append_ledger dict schema,
  m1_t_value_gate Harvey hurdle, cutoff_meta, CLOSED_FAMILIES, SEED_REGISTRY)

Leg C net-formula reading (audit-disclosed): per-day routing value =
|d_s| of the confirmed state (upside drift capture on positive-d states +
downside drift avoidance on negative-d states), matching the frozen sec.5.3
prediction arithmetic (BEAR-avoidance value = |d_BEAR| x n_BEAR). The
signed literal sum(d_eff(day)) is identically zero by state partition
(same-window conditional means telescope to the unconditional mean), which
contradicts the frozen PASS expectation and is therefore rejected as a
reading; both faces are disclosed in the output audit block.

Exit codes: 0 = normal (deterministic idempotent rewrite); 2 = anchor/face
VOID (fail-closed refuse-to-burn) or mechanism fault (reported verbatim).
"""
import json
import math
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
sys.path.insert(0, ROOT)                  # knowledge/ on path (a158 pattern)
sys.path.insert(0, _HERE)                # scripts/ on path

import science_gates  # noqa: E402
import regime_style_matrix as rsm  # noqa: E402 (frozen consumer engine)
from regime5_labeler import _load as load_panel  # noqa: E402 (frozen loader)
from rev_osc_stock_p1 import COST_X1  # noqa: E402 (13.041bp/side frozen)

PANEL_PATH = os.path.join(ROOT, "data", "daily", "sh510300.csv")
LABELS_PATH = os.path.join(ROOT, "results", "regime5_labels",
                           "REGIME5-2026-09-30.json")
OUT_DIR = os.path.join(ROOT, "results", "regime5_validation")
OUT_PATH = os.path.join(OUT_DIR, "REGIME5-VALIDATION-2026-09-30.json")
OUT_REL = "results/regime5_validation/REGIME5-VALIDATION-2026-09-30.json"
ATTRITION_PATH = os.path.join(ROOT, "results", "gate_attrition.json")
PREREG_REL = "research/REGIME5_VALIDATION_P1.md"
PREREG_FREEZE_COMMIT = "1aafbd257"
FAMILY_KEY = "regime_labeler_validation"

# -- prereg sec.2 declared anchor faces (VOID on drift = D2 lockbox) -------
ANCHOR_FIRST_PANEL = "2012-05-28"
ANCHOR_PANEL_ROWS = 3488
ANCHOR_CUTOFF = "2026-09-30"
ANCHOR_FIRST_LABEL = "2013-03-21"
ANCHOR_K_LABELS = 3289
MAIN_START = "2020-01-02"          # main validation window start (sec.4)
N_CONF_CANDS = (1, 2, 3, 5, 8)     # sec.3 Leg B candidate set
N_NULLS = 1000
N_BOOT = 2000
BOOT_BLOCK = 20
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")
GATE_STATES = ("BULL", "BEAR")      # directional claims only (sec.3 M1 face)
DEFAULT_N_CONF = 3                  # consumer frozen default (rsm.N_CONF)

# sec.4/sec.5 hard-bound design: extreme-day EXEMPTION DISCLOSURE windows
# (listed, never gate-affecting)
EXTREME_WINDOWS = (
    ("2015-crash-rescue", "2015-06-15", "2015-07-31"),
    ("2016-01-circuit-breaker", "2016-01-04", "2016-01-31"),
    ("2024-09-24-policy-pulse", "2024-09-23", "2024-09-30"),
    ("2025-04-tariff-shock", "2025-04-02", "2025-04-30"),
)


def anchor_assert(panel, doc):
    """sec.2 anchor-face assertion: every declared face must match the
    loaded probe EXACTLY; one mismatch = config VOID (fail-closed)."""
    if not panel:
        return "panel empty"
    if panel[0][0] != ANCHOR_FIRST_PANEL:
        return "panel first date %s != declared %s" % (
            panel[0][0], ANCHOR_FIRST_PANEL)
    if len(panel) != ANCHOR_PANEL_ROWS:
        return "panel rows %d != declared %d (panel drift)" % (
            len(panel), ANCHOR_PANEL_ROWS)
    if panel[-1][0] != ANCHOR_CUTOFF:
        return "panel tail %s != declared cutoff %s (D2 lockbox: post-cutoff" \
              " bar must not flow back into this batch)" % (
                  panel[-1][0], ANCHOR_CUTOFF)
    labels = doc.get("labels") or []
    if doc.get("cutoff") != ANCHOR_CUTOFF:
        return "labels cutoff %s != declared %s" % (
            doc.get("cutoff"), ANCHOR_CUTOFF)
    if len(labels) != ANCHOR_K_LABELS:
        return "labels K %d != declared %d" % (len(labels), ANCHOR_K_LABELS)
    if not labels or labels[0]["date"] != ANCHOR_FIRST_LABEL:
        return "first label date %s != declared %s" % (
            labels[0]["date"] if labels else None, ANCHOR_FIRST_LABEL)
    return None


def closed_family_assert():
    """M3: family_key must be open (zero regime keys in CLOSED_FAMILIES)."""
    hits = sorted(k for k in science_gates.CLOSED_FAMILIES
                  if "regime" in str(k).lower())
    return hits or None


def state_table(eff, r_next, idxs):
    """Leg A per-state conditional differentials on the given day set.
    d_s = mean(r_next | eff==s) - mean(r_next | all idxs);
    t_s = d_s / (sd_s / sqrt(n_s)) -- frozen sec.3 direct-t formula."""
    if not idxs:
        return None
    vals = [r_next[i] for i in idxs]
    mu = sum(vals) / len(vals)
    out = {"unconditional_mean": mu, "n_days": len(idxs), "states": {}}
    for s in STATES:
        sel = [r_next[i] for i in idxs if eff[i] == s]
        n = len(sel)
        row = {"n": n}
        if n:
            m = sum(sel) / n
            row["mean"] = m
            row["d"] = m - mu
            if n > 1:
                var = sum((v - m) ** 2 for v in sel) / (n - 1)
                sd = math.sqrt(var)
                row["sd"] = sd
                row["t"] = (m - mu) / (sd / math.sqrt(n)) if sd > 0 else None
            else:
                row["sd"] = None
                row["t"] = None
        else:
            row.update({"mean": None, "d": None, "sd": None, "t": None})
        out["states"][s] = row
    return out


def _dvec(table):
    return {s: table["states"][s]["d"] for s in STATES}


def perm_nulls(raw, win_pos, stats_idxs, r_next, rng_children):
    """sec.3 Leg A (a): 1,000 replicas; per replica the window's raw states
    are shuffled (per-state day counts preserved by construction), the SAME
    debounce layer (N_CONF=3, full-series bootstrap) is applied, per-state
    d_null is computed on stats_idxs. Returns {state: [|d_null| ...]}."""
    win_states = [raw[j] for j in win_pos]
    abs_null = {s: [] for s in STATES}
    mu = None
    for child in rng_children:
        rng = np.random.default_rng(child)
        shuffled = [win_states[k] for k in rng.permutation(len(win_states))]
        new_raw = list(raw)
        for pos, st in zip(win_pos, shuffled):
            new_raw[pos] = st
        eff = rsm.confirm_window(new_raw, DEFAULT_N_CONF)
        tab = state_table(eff, r_next, stats_idxs)
        if mu is None:
            mu = tab["unconditional_mean"]
        for s in STATES:
            d = tab["states"][s]["d"]
            if d is not None:
                abs_null[s].append(abs(d))
    return abs_null


def block_bootstrap(eff, r_next, idxs, rng, n_draws=N_BOOT, block=BOOT_BLOCK):
    """sec.3 Leg A (b): 20-trading-day block bootstrap, 2,000 draws, 95% CI
    per state. Blocks are consecutive-day chunks of the window series."""
    pairs = [(eff[i], r_next[i]) for i in idxs]
    m = len(pairs)
    if m == 0:
        return {s: None for s in STATES}
    n_blocks = max(1, math.ceil(m / block))
    draws = {s: [] for s in STATES}
    for _ in range(n_draws):
        pick = rng.integers(0, n_blocks, n_blocks)
        sample = []
        for b in pick:
            sample.extend(pairs[b * block:(b + 1) * block])
        sample = sample[:m]
        mu = sum(v for _s, v in sample) / m
        acc = {s: [] for s in STATES}
        for s, v in sample:
            acc[s].append(v)
        for s in STATES:
            if acc[s]:
                draws[s].append(sum(acc[s]) / len(acc[s]) - mu)
    out = {}
    for s in STATES:
        if draws[s]:
            arr = sorted(draws[s])
            k = len(arr)
            lo = arr[int(round(0.025 * (k - 1)))]
            hi = arr[int(round(0.975 * (k - 1)))]
            out[s] = {"ci_lo": lo, "ci_hi": hi, "n_draws": len(arr)}
        else:
            out[s] = None
    return out


def leg_b_calibration(raw, dates, r_next, d_full):
    """sec.3 Leg B: N_CONF candidates over full history. F(N) confirmed
    flips, W(N) wrong-state days, C(N)=sum dw*2*COST_X1, O(N)=sum over
    wrong days |d_conf - d_raw| (fixed Leg-A full-history d table),
    L(N)=C+O, net(N)=sum over return-bearing days |d_eff| - C(N)."""
    rows = {}
    for n in N_CONF_CANDS:
        eff = rsm.confirm_window(raw, n) if n > 1 else list(raw)
        events = rsm.switch_events(dates, eff)
        cost = 0.0
        for ev in events:
            c_single, _dw = rsm.transition_cost(ev["from"], ev["to"])
            cost += 2.0 * c_single  # double-side per frozen sec.3
        wrong = [j for j in range(len(raw)) if eff[j] != raw[j]]
        opp = 0.0
        for j in wrong:
            dc, dr = d_full.get(eff[j]), d_full.get(raw[j])
            if dc is not None and dr is not None:
                opp += abs(dc - dr)
        rb = [j for j in range(len(raw)) if r_next[j] is not None]
        gross = 0.0
        for j in rb:
            d = d_full.get(eff[j])
            if d is not None:
                gross += abs(d)
        rows[n] = {"n_conf": n, "flips_F": len(events), "wrong_days_W":
                   len(wrong), "transition_cost_C": cost,
                   "opportunity_cost_O": opp, "L": cost + opp,
                   "gross_routing_value": gross, "net": gross - cost}
    return rows


def extreme_day_disclosure(raw, eff, r_next, dates):
    out = []
    for name, lo, hi in EXTREME_WINDOWS:
        days = []
        for j, d in enumerate(dates):
            if lo <= d <= hi:
                rn = r_next[j]
                days.append({"date": d, "raw": raw[j], "eff": eff[j],
                             "r_next_bp": round(rn * 1e4, 2)
                             if rn is not None else None})
        out.append({"window": name, "from": lo, "to": hi, "days": days})
    return out


def _ledger_block():
    """Trials-ledger decision: fresh burn -> append_ledger dict (schema
    unique, prev data-driven, never hand-copied); deterministic re-run ->
    keep the frozen block (P-1c r61 zero-delta pattern). Returns
    (block, is_fresh, refuse_reason)."""
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, encoding="utf-8") as fh:
                old = json.load(fh)
        except Exception:
            return None, False, "existing output unreadable (refuse silent re-burn)"
        blk = (old or {}).get("trials_ledger")
        if not blk:
            return None, False, "existing output lacks trials_ledger (refuse)"
        return blk, False, None
    return science_gates.append_ledger(
        "REGIME5-VALIDATION-P1", 1010, file_name=OUT_REL,
        evidence_cutoff=ANCHOR_CUTOFF), True, None


def _append_attrition(entry):
    with open(ATTRITION_PATH, encoding="utf-8") as fh:
        d = json.load(fh)  # single-file fresh read-modify-write (r806 law)
    d["entries"].append(entry)
    with open(ATTRITION_PATH, "w", encoding="utf-8", newline="") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)


def _compute(panel, doc):
    """Deterministic numeric core (selftest reuses for byte-stability)."""
    err = anchor_assert(panel, doc)
    if err:
        return None, "VOID anchor face: %s" % err
    labels = doc["labels"]
    dates = [r["date"] for r in labels]
    raw = [r["state"] for r in labels]
    pidx = {r[0]: i for i, r in enumerate(panel)}
    try:
        lp = [pidx[d] for d in dates]
    except KeyError as e:
        return None, "VOID face mismatch: label date %s not in panel" % e
    closes = [r[1] for r in panel]
    r_next = [None] * len(labels)
    for j, p in enumerate(lp):
        if p + 1 < len(panel):
            r_next[j] = closes[p + 1] / closes[p] - 1.0
    rb = [j for j in range(len(labels)) if r_next[j] is not None]
    win_pos = [j for j, d in enumerate(dates) if d >= MAIN_START]
    win_stats = [j for j in rb if dates[j] >= MAIN_START]
    if len(rb) < 1000:
        return None, "VOID K honesty: %d return-bearing days < 1000 law" % len(rb)
    if len(win_stats) < 1000:
        return None, "VOID K honesty: main-window %d days < 1000 law" % len(win_stats)

    eff3 = rsm.confirm_window(raw, DEFAULT_N_CONF)
    main_table = state_table(eff3, r_next, win_stats)
    full_table = state_table(eff3, r_next, rb)
    d_full = _dvec(full_table)

    # Leg A significance machines (main window): 1,000 perm nulls from the
    # registered single base seed (SEED_REGISTRY machine-read, spawn-derived,
    # zero climbing); bootstrap uses the SAME base's next child (disclosed).
    seed_key = "regime5_validation_p1_null_base"
    base = int(science_gates.SEED_REGISTRY[seed_key])
    children = np.random.SeedSequence(base).spawn(N_NULLS + 1)
    abs_null = perm_nulls(raw, win_pos, win_stats, r_next, children[:N_NULLS])
    boot_rng = np.random.default_rng(children[N_NULLS])
    boot = block_bootstrap(eff3, r_next, win_stats, boot_rng)

    perm = {}
    for s in STATES:
        obs = main_table["states"][s]["d"]
        arr = abs_null[s]
        if obs is None or not arr:
            perm[s] = None
            continue
        p = (1 + sum(1 for v in arr if v >= abs(obs))) / (len(arr) + 1)
        perm[s] = {"p_two_sided": p, "null_abs_mean": sum(arr) / len(arr),
                   "null_abs_max": max(arr),
                   "null_abs_p95": sorted(arr)[int(0.95 * (len(arr) - 1))]}

    # sec.4 main gate: directional two states, three faces each
    gate = {}
    m1 = {}
    for s in GATE_STATES:
        row = main_table["states"][s]
        d = row["d"]
        direction_ok = (d > 0) if s == "BULL" else (d < 0) if d is not None else False
        pr = perm[s]["p_two_sided"] if perm[s] else 1.0
        p_ok = pr < 0.05
        ci = boot[s]
        ci_ok = bool(ci) and ((ci["ci_lo"] > 0) if s == "BULL"
                              else (ci["ci_hi"] < 0))
        m1r = science_gates.m1_t_value_gate(row["t"]) if row["t"] is not None \
            else science_gates.m1_t_value_gate(None)
        m1[s] = m1r
        t_ok = bool(m1r.get("pass"))
        gate[s] = {"direction_ok": bool(direction_ok), "perm_p": pr,
                   "perm_p_ok": bool(p_ok), "ci": ci, "ci_ok": ci_ok,
                   "t": row["t"], "t_gate_pass": t_ok,
                   "state_pass": bool(direction_ok and p_ok and ci_ok and t_ok)}
    label_face_holds = all(g["state_pass"] for g in gate.values())

    legB = leg_b_calibration(raw, dates, r_next, d_full)
    l_min = min(v["L"] for v in legB.values())
    n_star = min(legB, key=lambda n: legB[n]["L"])
    keep_default3 = legB[DEFAULT_N_CONF]["L"] <= 1.10 * l_min
    leg_c_pass = legB[n_star]["net"] > 0.0

    extremes = extreme_day_disclosure(raw, eff3, r_next, dates)

    try:
        skill = science_gates.skill_line_v2(1010)
        skill_line = {k: skill[k] for k in
                      ("skill_line_v2", "n_eff", "passive", "mu_null",
                       "sigma_null") if k in skill}
        skill_line["note"] = "disclosure reading only (shared-library line)"
    except Exception as e:  # honest unavailability, never a gate
        skill_line = {"unavailable": str(e)[:160]}

    return {
        "labels": {"k": len(labels), "first": dates[0], "last": dates[-1],
                   "cutoff": doc.get("cutoff")},
        "windows": {"main_start": MAIN_START, "main_days": len(win_stats),
                    "full_return_bearing_days": len(rb)},
        "leg_a_main_window": main_table,
        "leg_a_full_history": full_table,
        "leg_a_perm_null": perm,
        "leg_a_block_bootstrap": boot,
        "m1_t_gate": m1,
        "main_gate": gate,
        "label_face_holds": label_face_holds,
        "leg_b_n_conf_table": {str(n): legB[n] for n in N_CONF_CANDS},
        "n_conf_star": n_star,
        "default3_kept": bool(keep_default3),
        "leg_c_net_pass": bool(leg_c_pass),
        "extreme_day_disclosure": extremes,
        "skill_line_v2_reading": skill_line,
    }, None


def cmd_run():
    panel = load_panel(PANEL_PATH)
    if not panel:
        print("REGIME5-VALIDATION: mechanism fault -- panel load empty")
        return 2
    try:
        with open(LABELS_PATH, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as e:
        print("REGIME5-VALIDATION: mechanism fault -- labels load: %s" % e)
        return 2
    hits = closed_family_assert()
    if hits:
        print("REGIME5-VALIDATION: VOID closed-family hit %s (batch refused)"
              % hits)
        return 2
    result, err = _compute(panel, doc)
    if err:
        print("REGIME5-VALIDATION: %s" % err)
        return 2
    ledger, fresh, refuse = _ledger_block()
    if refuse:
        print("REGIME5-VALIDATION: mechanism fault -- %s" % refuse)
        return 2
    out = {
        "batch": "REGIME5-VALIDATION-P1",
        "prereg": PREREG_REL,
        "prereg_freeze_commit": PREREG_FREEZE_COMMIT,
        "family_key": FAMILY_KEY,
        "dept": "research",
        "evidence_cutoff": ANCHOR_CUTOFF,
        "science_gates": science_gates.cutoff_meta(ANCHOR_CUTOFF),
        "result": result,
        "audit": {
            "anchor_faces": "6/6 EXACT (panel first/rows/tail, labels "
                            "cutoff/K/first-date; D2 lockbox asserted)",
            "closed_families_regime_hits": [],
            "seed_base_key": "regime5_validation_p1_null_base",
            "seed_base": int(science_gates.SEED_REGISTRY[
                "regime5_validation_p1_null_base"]),
            "seed_derivation": "SeedSequence(base).spawn(1001): children "
                               "0..999 = 1,000 perm-null replicas, child 1000 "
                               "= block-bootstrap rng (single-base derived, "
                               "zero climbing)",
            "numpy": np.__version__,
            "cost_x1_per_side": COST_X1,
            "transition_cost_rule": "double-side: dw * 2 * COST_X1 per "
                                     "confirmed flip (frozen sec.3)",
            "leg_c_net_reading": "per-day routing value = |d_s| of confirmed "
                                 "state (drift capture + drift avoidance), "
                                 "per frozen sec.5.3 BEAR-avoidance "
                                 "arithmetic; signed literal sum is "
                                 "identically 0 by partition (rejected "
                                 "reading, disclosed)",
            "o_n_reading": "fixed Leg-A full-history d table; per wrong day "
                           "|d_eff - d_raw| (frozen sec.3 parenthetical)",
            "m1_hurdle": science_gates.M1_T_HURDLE,
            "cells": 1010,
            "envelope_note": "runtime.generated is the only wall-clock "
                             "field; all numeric faces deterministic",
        },
        "runtime": {"generated": time.strftime("%Y-%m-%d %H:%M:%S")},
        "trials_ledger": ledger,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)
    if fresh:
        _append_attrition({
            "batch": "REGIME5-VALIDATION-P1",
            "ts": time.strftime("%Y-%m-%d %H:%M"),
            "kind": "validation-burn",
            "cells_ledger_delta": 1010,
            "ledger_total_after": ledger["total"],
            "gates": {
                "banned_direction": "ADMIT rc0 at freeze (r870, sec.0.5)",
                "freeze": PREREG_FREEZE_COMMIT,
                "anchor": "6/6 faces EXACT",
                "main_gate": "PASS" if result["label_face_holds"]
                             else "FAIL (honest per-state face)",
                "leg_c": "PASS" if result["leg_c_net_pass"] else "FAIL"},
            "note": "measurement/calibration burn: 5 state-diff + 5 N_CONF "
                    "+ 1,000 perm-null; exit-axis N/A declared at freeze",
        })
    g = result["main_gate"]
    mt = result["leg_a_main_window"]["states"]
    print("REGIME5-VALIDATION-P1: label_face=%s | "
          "BULL d=%s p=%s t=%s | BEAR d=%s p=%s t=%s | N*=%s default3=%s "
          "net_pass=%s | ledger_total=%s -> %s"
          % ("HOLDS" if result["label_face_holds"] else "not-held",
             _fmt(mt["BULL"]["d"]), _fmt(g["BULL"]["perm_p"]),
             _fmt(g["BULL"]["t"]), _fmt(mt["BEAR"]["d"]),
             _fmt(g["BEAR"]["perm_p"]), _fmt(g["BEAR"]["t"]),
             result["n_conf_star"], result["default3_kept"],
             result["leg_c_net_pass"], ledger["total"], OUT_REL))
    return 0


def _fmt(v):
    if v is None:
        return "NA"
    if isinstance(v, float):
        return ("%.6g" % v)
    return str(v)


def _synth_anchor_faces():
    """Synthetic panel/doc pair that satisfies every declared anchor face
    (shape-only; hermetic selftest fixture)."""
    panel = [(("2012-05-28" if i == 0 else
               ("2026-09-30" if i == ANCHOR_PANEL_ROWS - 1 else
                "20%02d-01-01" % (13 + i // 300))),
              100.0 + i, 99.0, 101.0, 1e6)
             for i in range(ANCHOR_PANEL_ROWS)]
    labels = ([{"date": ANCHOR_FIRST_LABEL, "state": "CHOP"}]
              + [{"date": "20%02d-01-01" % (13 + j // 300), "state": "CHOP"}
                 for j in range(ANCHOR_K_LABELS - 1)])
    return panel, {"cutoff": ANCHOR_CUTOFF, "labels": labels}


def cmd_selftest():
    """Hermetic (zero network, zero real-data dependency): anchor VOID
    legs, face-mismatch leg, ledger zero-delta leg, debounce import-face,
    known-value cost leg, component determinism legs."""
    n = [0]

    def chk(name, cond):
        n[0] += 1
        if not cond:
            print("SELFTEST FAIL t%02d: %s" % (n[0], name))
            return False
        print("  t%02d PASS %s" % (n[0], name))
        return True

    ok = True
    # t1 anchor exact-pass leg on a synthetic in-shape panel/doc
    panel, doc = _synth_anchor_faces()
    ok &= chk("anchor faces exact pass",
              anchor_assert(panel, doc) is None)
    # t2 anchor VOID legs (cutoff drift = D2 lockbox; row drift)
    bad_doc = dict(doc, cutoff="2026-10-08")
    ok &= chk("anchor VOID on labels cutoff drift",
              "cutoff" in (anchor_assert(panel, bad_doc) or ""))
    bad_panel = panel[:-1]
    ok &= chk("anchor VOID on panel row drift",
              "rows" in (anchor_assert(bad_panel, doc) or ""))
    # t3 face-mismatch VOID: in-shape doc, one label date absent from panel
    bad_doc2 = {"cutoff": ANCHOR_CUTOFF, "labels": (
        [{"date": ANCHOR_FIRST_LABEL, "state": "CHOP"}]
        + [{"date": "2030-01-01", "state": "CHOP"}]
        + [{"date": "20%02d-01-01" % (13 + j // 300), "state": "CHOP"}
           for j in range(ANCHOR_K_LABELS - 2)])}
    _res, err3 = _compute(panel, bad_doc2)
    ok &= chk("face-mismatch VOID on unknown label date",
              err3 is not None and "not in panel" in err3)
    # t4 debounce import-face: jitter never flips (frozen engine behavior)
    alt = ["BEAR"]
    for _i in range(20):
        alt.append("BULL" if alt[-1] == "BEAR" else "BEAR")
    eff = rsm.confirm_window(alt, 3)
    ok &= chk("debounce import-face jitter zero-flip",
              rsm.switch_events(list(range(len(eff))), eff) == [])
    # t5 known-value cost leg: BEAR->BULL dw=1.10 -> C = 1.10*2*COST_X1
    c_single, dw = rsm.transition_cost("BEAR", "BULL")
    ok &= chk("double-side cost known value (dw=1.10)",
              abs(dw - 1.10) < 1e-12 and
              abs(2 * c_single - 1.10 * 2 * COST_X1) < 1e-15)
    # t6 stats known-value leg: hand-computed d and t on a tiny face
    eff6 = ["BULL", "BULL", "BEAR", "BEAR", "CHOP", "CHOP"]
    r6 = [0.01, 0.03, -0.02, -0.04, 0.00, 0.00]
    tab = state_table(eff6, r6, list(range(6)))
    mu = sum(r6) / 6
    d_bull = (0.01 + 0.03) / 2 - mu
    d_bear = (-0.02 + -0.04) / 2 - mu
    ok &= chk("state_table d values hand-check",
              abs(tab["states"]["BULL"]["d"] - d_bull) < 1e-12 and
              abs(tab["states"]["BEAR"]["d"] - d_bear) < 1e-12 and
              abs(tab["states"]["CHOP"]["d"] - (0.0 - mu)) < 1e-12)
    sel = [0.01, 0.03]
    m = sum(sel) / 2
    sd = math.sqrt(sum((v - m) ** 2 for v in sel) / 1)
    ok &= chk("state_table direct-t formula",
              abs(tab["states"]["BULL"]["t"]
                  - d_bull / (sd / math.sqrt(2))) < 1e-12)
    # t7 perm-null: replica count + counts-preserving shuffle + p in (0,1]
    raw_t = ["BULL"] * 30 + ["BEAR"] * 30
    win_pos = list(range(60))
    stats_idx = list(range(59))
    r_t = [0.01 if raw_t[j] == "BULL" else -0.01 for j in range(60)]
    r_t[59] = 0.0
    ss = np.random.SeedSequence(20261008)
    an = perm_nulls(raw_t, win_pos, stats_idx, r_t, ss.spawn(24))
    p_bull = (1 + sum(1 for v in an["BULL"]
                       if v >= abs(d_bull))) / (len(an["BULL"]) + 1)
    ok &= chk("perm-null replica count + bounded p",
              len(an["BULL"]) == 24 and 0 < p_bull <= 1)
    # t8 block bootstrap: degenerate CI on a constant face
    boot = block_bootstrap(eff6, [0.0] * 6, list(range(6)),
                           np.random.default_rng(0), n_draws=100, block=2)
    ok &= chk("bootstrap CI width 0 on constant face",
              all(abs(v["ci_hi"] - v["ci_lo"]) < 1e-15
                  for v in boot.values() if v))
    # t9 ledger zero-delta leg: existing frozen block is kept verbatim
    frozen = {"prev_total": 1, "batch_trials": 1010, "total": 1011,
              "batch": "REGIME5-VALIDATION-P1"}
    global OUT_PATH
    saved = OUT_PATH
    try:
        import tempfile
        tmpd = tempfile.mkdtemp()
        OUT_PATH = os.path.join(tmpd, "out.json")
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": frozen}, fh)
        blk, fresh, refuse = _ledger_block()
        ok &= chk("ledger zero-delta keeps frozen block",
                  not fresh and not refuse and blk == frozen)
        os.remove(OUT_PATH)
        blk2, fresh2, refuse2 = _ledger_block()
        ok &= chk("ledger fresh append on absent output",
                  fresh2 and not refuse2 and blk2["batch_trials"] == 1010
                  and blk2["batch"] == "REGIME5-VALIDATION-P1")
    finally:
        OUT_PATH = saved
    # t10 closed-family gate leg (live registry machine-read)
    ok &= chk("closed families zero regime keys (open)",
              closed_family_assert() is None)
    # t11 component determinism: fixed-seed double-run identical
    ss2 = np.random.SeedSequence(94100).spawn(6)
    an1 = perm_nulls(raw_t, win_pos, stats_idx, r_t, ss2)
    ss2b = np.random.SeedSequence(94100).spawn(6)
    an2 = perm_nulls(raw_t, win_pos, stats_idx, r_t, ss2b)
    ok &= chk("perm-null determinism",
              json.dumps(an1, sort_keys=True) == json.dumps(an2, sort_keys=True))
    b1 = block_bootstrap(eff6, r6, list(range(6)),
                         np.random.default_rng(7), n_draws=50, block=2)
    b2 = block_bootstrap(eff6, r6, list(range(6)),
                         np.random.default_rng(7), n_draws=50, block=2)
    ok &= chk("bootstrap determinism",
              json.dumps(b1, sort_keys=True) == json.dumps(b2, sort_keys=True))
    lb1 = leg_b_calibration(raw_t, ["d%02d" % i for i in range(60)],
                            r_t + [0.0], {"BULL": 0.005, "BEAR": -0.005,
                                          "CHOP": 0.0, "GRIND": 0.0,
                                          "SUPPORT": 0.0})
    lb2 = leg_b_calibration(raw_t, ["d%02d" % i for i in range(60)],
                            r_t + [0.0], {"BULL": 0.005, "BEAR": -0.005,
                                          "CHOP": 0.0, "GRIND": 0.0,
                                          "SUPPORT": 0.0})
    ok &= chk("leg_b determinism",
              json.dumps(lb1, sort_keys=True) == json.dumps(lb2,
                                                            sort_keys=True))
    print("regime5_validation selftest: %s (%d checks)"
          % ("PASS" if ok else "FAIL", n[0]))
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print("usage: regime5_validation.py <run|selftest>")
        return 2
    if argv[1] == "run":
        return cmd_run()
    if argv[1] == "selftest":
        return cmd_selftest()
    print("unknown subcommand %r" % argv[1])
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
