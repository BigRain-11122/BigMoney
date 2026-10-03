"""G2_SLOT_MON_P2 stage-2 registration-caliber verdict runner (monthly-
translation 2-face shortlist {old_032, best_016}; frozen prereg
research/G2_SLOT_MON_P2.md v1.0, freeze commit 9b8a19fdf precedes any P2
run -- R99 law; freeze-window probe PASS 6/6 results/_r648bma_p2_probe.json).

Law lineage: r647 G2_SLOT_MON_P1 census nominated 2/47 stage-2 (old_032
steady + best_016 marginal) -> this batch = the independent sec.9 freeze
registration-caliber full-gates chain (MON_P1 sec.4 nomination line
verbatim). Face verdict three states: eligible-for-registration
(g2_registration_v2 all-pass) / judged-negative (any frozen line fails,
failed lines disclosed) / consumption-blocked (law-A exit census >20%
non-rank). Registration EXECUTION stays with the hr.py promotion pipeline
-- this batch only judges, never registers (prereg sec.0).

Machinery: single-source reuse of scripts/g2_slot_mon_p1.py (anti-rebuild
law) -- panel build, monthly grid, blend sleeve (P1 blend_sleeve + additive
r649 trade counters), null sleeves (additive r649 seed param; frozen band
[20570000,20570060) registered r648), IC block, D6 member canon. P2 adds
only the registration-chain legs:

  leg i    per-face fwd-5d rank-IC + PARENT anchor identity (1e-6, fail-closed)
  leg ii   monthly Top-16 blend sleeves x1/x2 (P1 blend canon) + metrics +
           126td rolling beat (stride 21) + regime segments (descriptive,
           r633 G-SEG density lesson: no count gate at monthly density) +
           extreme-day disclosure
  leg iii  60 same-mask monthly random nulls rng([20570000, k]) -- |mean IC|
           band + x2 beat/EW48-excess bands + x1-Sharpe null pool for g1'
  leg iv   D6: both faces' x1/x2 blend daily series vs REG6 all members
           pairwise |corr| (gate >=0.7 = family-merge rejection) + inter-
           face pair disclosure (predicted high, not a gate)
  leg v    registration chain per face (headline = x1): g1_prime_v2
           (null_pool = P2 in-batch pool, passive_override = EW48 same-
           window Sharpe, n_trades/n_entries = sleeve rotation counts,
           n_eff_override = r259 prev-echo guard) -> x2 survival -> M1
           t>=3.0 (t_from_sharpe, claim_class new_strategy) -> DSR ->
           same-family CSCV PBO (family matrix = frozen parent-roster
           family faces recompute, 18 old / 27 tail, identity cross-check
           vs parent leg ii at 1e-9 after parent 4dp rounding, fail-closed)
           -> g2_registration_v2
  exit     census carrier: per-rebalance exit log, rank-rotation is the only
           legal reason (constructive); non-rank share > CENSUS_BLOCK_SHARE
           (0.20) -> consumption-blocked

Engine face (sec.0.6): blend approximation carrier -- the judged sleeve
legs never touch the engine exit stack (asserted: no engine modules loaded
by the carrier graph before the read-only D6 member leg; D6 consumes the
ew6 registered-member canon via live.paper exactly like the finalized
rev_osc_stock_p1 r281 precedent -- transitive engine-graph load disclosed
in audit, zero engine code path in any judged computation).

Budget cap 300s (O-1901 (a)-1 item iii): over-budget abort = exit 3,
nothing finalized. Determinism: zero wall-clock fields in the batch JSON;
selftest = double-run byte identity (mini pipeline, real panel) +
shortlist/cutoff/seed-band/parent-IC/cost/exit-census/zero-engine legs.

Usage: run | selftest
"""
import argparse
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
sys.path.insert(0, os.path.join(ROOT, "screening"))
sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))

from g2_slot_mon_p1 import (  # noqa: E402  single-source reuse (anti-rebuild)
    ANCHOR_HEAD, COST_FACES, COST_X1, COST_X1_EXPECT, D6_MIN_OVERLAP,
    D6_REJECT, INERVICE_SHA16_EXPECT, INSERVICE_SHA16, PARENT_IC_TOL,
    PANEL_START, REG6, ROSTER_SHA16, _corr, _r, beat_rate, blend_sleeve,
    build_panel, compute_faces, ew48_window, ic_block, member_series,
    monthly_grid, null_sleeves, sleeve_metrics, vendor_head,
)
import science_gates as sg  # noqa: E402
from pbo import cscv_pbo  # noqa: E402

BATCH = "G2_SLOT_MON_P2"
TICKET = "T-2026-10-03-164-P1"
PREREG_REL = "research/G2_SLOT_MON_P2.md"
CUTOFF = "2026-09-22"
PANEL_START = "2020-01-02"
SEED_NULLS = 20570000
K_NULLS = 60
BATCH_CELLS = 62          # sec.0 declaration face: 2 judged cell-faces + 60 nulls
BATCH_TRIALS = 124        # sec.3 frozen ledger face (2 blend legs + 60 null
                          # sleeves + 60 null IC faces + 2 family-matrix legs)
BUDGET_CAP_S = 300        # O-1901 (a)-1 item iii
GATES_PREBURN_CAP_S = 240
M1_HURDLE = 3.0
M1_CLAIM_CLASS = "new_strategy"
DSR_GATE = 0.95
PBO_GATE = 0.25
CENSUS_BLOCK_SHARE = 0.20
FAMILY_KEY = "g2_slot_mon_p2_xs"
PARENT_METRIC_TOL = 1e-9  # after parent 4dp rounding (parent stores rounded)
SHORTLIST = ("best_016", "old_032")
FACE_FAMILY = {"best_016": "tail", "old_032": "old"}
PARENT_IC_ANCHORS = {"best_016": 0.017731, "old_032": 0.027954}

PROBE_JSON = os.path.join(ROOT, "results", "_r648bma_p2_probe.json")
PARENT_CENSUS_JSON = os.path.join(ROOT, "results", "g2_slot_mon_p1",
                                  "g2_slot_mon_p1_census.json")
PARENT_PROBE_JSON = os.path.join(ROOT, "results", "_r647bma_slot_mon_roster_probe.json")
OUT_DIR = os.path.join(ROOT, "results", "g2_slot_mon_p2")
OUT_JSON = os.path.join(OUT_DIR, "g2_slot_mon_p2_verdict.json")
D6_JSON = os.path.join(OUT_DIR, "d6_numeric.json")
IC_CSV = os.path.join(OUT_DIR, "ic_by_face.csv")
FAM_CSV = {"old": os.path.join(OUT_DIR, "family_matrix_old.csv"),
           "tail": os.path.join(OUT_DIR, "family_matrix_tail.csv")}
ATTR_JSON = os.path.join(ROOT, "results", "gate_attrition.json")


def _fail(msg, code=2):
    print("[g2slotmonp2] FAIL: %s" % msg, flush=True)
    raise SystemExit(code)


# ---------------------------------------------------------------- identity faces

def shortlist_and_families():
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    parent_probe = json.load(open(PARENT_PROBE_JSON, encoding="utf-8"))
    roster = parent_probe["roster"]
    canon = json.dumps(roster, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"))
    sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    fams = {fam: sorted(parent_probe["leg1_roster"]["per_batch"][fam]["faces"])
            for fam in ("old", "tail")}
    classes = dict(probe["legs"]["L6_class_carry"]["classes"])
    short = tuple(sorted(probe["legs"]["L1_shortlist_integrity"]["expected"]))
    return probe, roster, sha, fams, classes, short


def engine_modules_loaded():
    return sorted(m for m in sys.modules if m == "engine" or m.startswith("engine."))


def assert_carrier_zero_engine(stage):
    mods = engine_modules_loaded()
    if mods:
        _fail("%s: engine graph loaded before this stage (%s) -- blend "
              "carrier must stay zero-engine (sec.0.6)" % (stage, mods[:5]))


# ---------------------------------------------------------------- gates

def run_gates(panel_facts):
    g = {}
    g["members"] = panel_facts["n_members"] == 48
    g["columns"] = not panel_facts["bad_columns_members"]
    g["dup_dates"] = not panel_facts["dup_date_members"]
    g["cutoff_truncation"] = panel_facts["union_last"] == CUTOFF
    g["vendor_head"] = vendor_head() == ANCHOR_HEAD
    probe, roster, sha, fams, classes, short = shortlist_and_families()
    g["shortlist_integrity"] = (short == SHORTLIST
                                and all(f in roster for f in SHORTLIST))
    g["roster_sha"] = sha.startswith(ROSTER_SHA16)
    g["family_counts"] = len(fams["old"]) == 18 and len(fams["tail"]) == 27
    g["shortlist_in_family"] = (SHORTLIST[1] in fams["old"]
                                and SHORTLIST[0] in fams["tail"])
    own = sg.SEED_REGISTRY.get("g2_slot_mon_p2_nulls")
    g["seed_registered"] = own == SEED_NULLS
    overlap = []
    for k, v in sg.SEED_REGISTRY.items():
        if k == "g2_slot_mon_p2_nulls":
            continue
        try:
            iv = int(v)
        except (TypeError, ValueError):
            continue
        if SEED_NULLS <= iv < SEED_NULLS + K_NULLS:
            overlap.append(k)
    g["seed_band_disjoint"] = not overlap
    g["cost_x1_single_source"] = abs(COST_X1 - COST_X1_EXPECT) < 1e-12
    g["whitelist_sha16"] = INSERVICE_SHA16 == INERVICE_SHA16_EXPECT
    g["closed_family_open"] = FAMILY_KEY not in getattr(sg, "CLOSED_FAMILIES", {})
    anchors = probe["legs"]["L5_parent_ic_anchors"]["anchors"]
    g["parent_anchors_present"] = all(
        abs(float(anchors[f]["ic5_mean"]) - PARENT_IC_ANCHORS[f]) < 1e-12
        for f in SHORTLIST)
    fails = [k for k, v in g.items() if not v]
    return (not fails), g, fails, probe, roster, sha, fams, classes


# ---------------------------------------------------------------- legs

def sleeve_face_row(sl1, sl2, panel, ic_block_row, T):
    idx = panel["idx"]
    m1 = sleeve_metrics(sl1["series"], idx, sl1["first_exec"])
    m2 = sleeve_metrics(sl2["series"], idx, sl2["first_exec"])
    ew1 = ew48_window(panel["rets"], sl1["first_exec"])
    ew2 = ew48_window(panel["rets"], sl2["first_exec"])
    br1, nw1 = beat_rate(sl1["series"], ew1, sl1["first_exec"], T)
    br2, nw2 = beat_rate(sl2["series"], ew2, sl2["first_exec"], T)
    row = {
        "ic": ic_block_row,
        "x1": {**m1, "beat_rate": br1, "n_windows": nw1,
               "turnover_total": _r(sl1["turnover_total"], 4),
               "n_rebal": sl1["n_rebal"], "n_skip": sl1["n_skip"],
               "n_buys_total": sl1["n_buys_total"], "n_exits_total": sl1["n_exits_total"]},
        "x2": {**m2, "beat_rate": br2, "n_windows": nw2,
               "turnover_total": _r(sl2["turnover_total"], 4),
               "n_rebal": sl2["n_rebal"], "n_skip": sl2["n_skip"],
               "n_buys_total": sl2["n_buys_total"], "n_exits_total": sl2["n_exits_total"]},
        "ew48_total_ret_x2_window": _r(float(np.prod(1.0 + ew2) - 1.0), 6),
        "first_exec": str(idx[sl1["first_exec"]].date()),
    }
    # extreme-day disclosure (sec.5(c): descriptive, no gate)
    ser = np.asarray(sl2["series"])
    order = np.argsort(-np.abs(ser))[:3]
    row["extreme_days_x2"] = [
        {"date": str(idx[sl2["first_exec"] + int(i)].date()),
         "r": _r(float(ser[int(i)]), 4)} for i in order]
    return row


def family_matrix(panel, grid_pairs, faces_res, fam_list):
    """Monthly x2 blend daily-return matrix (dates x faces) for one family +
    per-face sleeve handles (parent leg ii identity cross-check input)."""
    idx = panel["idx"]
    cols, sleeves = {}, {}
    for f in fam_list:
        Fmat = faces_res[f][0]
        if Fmat is None:
            continue

        def score_fn(g, _F=Fmat):
            return _F[g]
        sl = blend_sleeve(score_fn, grid_pairs, panel["rets"], COST_FACES["x2"])
        if sl is None:
            continue
        sleeves[f] = sl
        cols[f] = pd.Series(sl["series"], index=idx[sl["first_exec"]:
                                                   sl["first_exec"] + len(sl["series"])])
    mat = pd.DataFrame(cols).dropna()
    return mat, sleeves


def parent_crosscheck(panel, sleeves, parent_census, T):
    """sec.5(f): recompute identity vs parent census leg ii (same machinery,
    same window). Parent stores 4dp-rounded faces -> compare after rounding
    (tolerance 1e-9 on the rounded values; drift = mechanical fault)."""
    idx = panel["idx"]
    drift, checked = [], 0
    for f, sl in sorted(sleeves.items()):
        prow = parent_census["faces"].get(f)
        if prow is None or "x2" not in prow:
            drift.append([f, "missing parent x2 row"])
            continue
        m = sleeve_metrics(sl["series"], idx, sl["first_exec"])
        ew = ew48_window(panel["rets"], sl["first_exec"])
        br, _nw = beat_rate(sl["series"], ew, sl["first_exec"], T)
        rec = {"ann": _r(m["ann"]), "sharpe": _r(m["sharpe"]),
               "maxdd": _r(m["maxdd"]), "total_ret": _r(m["total_ret"]),
               "beat_rate": br, "turnover_total": _r(sl["turnover_total"], 4),
               "n_rebal": sl["n_rebal"]}
        for k in rec:
            pv = prow["x2"].get(k)
            if rec[k] is None or pv is None:
                drift.append([f, k, "none-mismatch", rec[k], pv])
                continue
            if abs(float(rec[k]) - float(pv)) > PARENT_METRIC_TOL:
                drift.append([f, k, rec[k], pv])
        checked += 1
    return {"n_faces_checked": checked, "n_drift": len(drift),
            "drift": drift[:20],
            "compare_caliber": "parent stores 4dp-rounded leg ii faces; identity asserted on rounded values at 1e-9 (same machinery + same window recompute)"}


def exit_census_face(sl):
    n_ex = int(sl["n_exits_total"])
    log = sl["exit_log"]
    n_other = 0  # constructive: rank rotation is the only exit path (sec.0.6)
    other_share = float(n_other) / n_ex if n_ex else 0.0
    return {
        "law": "rank-rotation-only (sec.0.6 hold-through monthly rank rotation; constructive census carrier)",
        "n_rebal": int(sl["n_rebal"]), "n_exits_total": n_ex,
        "n_exits_rank_rotation": n_ex, "n_exits_other": n_other,
        "other_share": round(other_share, 6),
        "block_share": CENSUS_BLOCK_SHARE,
        "blocked": bool(other_share > CENSUS_BLOCK_SHARE),
        "exit_log": log,
        "note": "selection schedule identical across cost faces (x1/x2 differ only by the cost term); log rows = per-rebalance {n_exits, n_buys}",
    }


def d6_block(panel, sleeves_by_face, want=True):
    out = {"reject_line": D6_REJECT, "min_overlap": D6_MIN_OVERLAP,
           "members": list(REG6), "faces": {}, "inter_face_pairs": {}}
    if not want:
        out["skipped"] = "d6 leg disabled (mini/selftest explicit)"
        return out
    mrets, mcutoffs = member_series()   # read-only ew6 canon (r281 precedent)
    for f, sl_pair in sleeves_by_face.items():
        if sl_pair is None:
            out["faces"][f] = {"skipped": "face compute failed (honest)"}
            continue
        face = {}
        fmax, farg = 0.0, None
        for cname, sl in sl_pair.items():
            s = pd.Series(sl["series"],
                          index=panel["idx"][sl["first_exec"]:
                                             sl["first_exec"] + len(sl["series"])])
            pm = {}
            for tid in REG6:
                v, ov = _corr(s, mrets[tid])
                pm[tid] = {"corr": v, "overlap_days": ov}
                if v is not None and abs(v) > fmax:
                    fmax, farg = abs(v), "%s:%s" % (cname, tid)
            face[cname] = {"per_member": pm}
        face["max_abs_corr"] = _r(fmax, 4)
        face["argmax"] = farg
        face["reject"] = bool(fmax >= D6_REJECT)
        out["faces"][f] = face
    # inter-face pair disclosure (predicted high -- same-engine lineage; NOT a gate)
    for cname in ("x1", "x2"):
        pa = sleeves_by_face.get(SHORTLIST[1])
        pb = sleeves_by_face.get(SHORTLIST[0])
        if not pa or not pb:
            continue
        a, b = pa[cname], pb[cname]
        sa = pd.Series(a["series"], index=panel["idx"][a["first_exec"]:a["first_exec"] + len(a["series"])])
        sb = pd.Series(b["series"], index=panel["idx"][b["first_exec"]:b["first_exec"] + len(b["series"])])
        v, ov = _corr(sa, sb)
        out["inter_face_pairs"][cname] = {"pair": "%s|%s" % (SHORTLIST[1], SHORTLIST[0]),
                                          "corr": v, "overlap_days": ov}
    out["member_cutoffs"] = mcutoffs
    return out


def regime_face(panel, sl2):
    """510300 t22 3-way proxy segments (descriptive only -- r633 G-SEG density
    lesson: no >=50 count gate at monthly 81-start density)."""
    from t22_virtual_timepoints import regime_proxy
    members = panel["members"]
    if "510300" not in members:
        return None
    idx = panel["idx"]
    c = pd.Series(panel["F"]["close"][:, members.index("510300")], index=idx)
    labels = np.asarray(regime_proxy(c), dtype=object)
    ew = ew48_window(panel["rets"], sl2["first_exec"])
    seg = {}
    for lab in ("bull", "chop", "bear", "na"):
        dpos = np.flatnonzero(labels[sl2["first_exec"]:] == lab) + sl2["first_exec"]
        if len(dpos) < 5:
            seg[lab] = {"n_days": int(len(dpos))}
            continue
        rel = dpos - sl2["first_exec"]
        s_cum = float(np.prod(1.0 + sl2["series"][rel]) - 1.0)
        e_cum = float(np.prod(1.0 + ew[rel]) - 1.0)
        seg[lab] = {"n_days": int(len(dpos)), "sleeve_cum": _r(s_cum, 4),
                    "ew48_cum": _r(e_cum, 4), "beat": bool(s_cum > e_cum)}
    seg["note"] = "descriptive disclosure only (monthly-density family: segment counts below any >=50 gate; r633 G-SEG lesson, prereg sec.3 leg ii)"
    return seg


# ---------------------------------------------------------------- pipeline

def run_pipeline(panel, fams, k_nulls, parent_census, want_d6=True,
                 want_chain=True, ledger=False, fam_slice=None):
    """Deterministic core (everything except final write). ledger=False ->
    no trials_ledger block (selftest mini-runs never touch the chain file)."""
    t_start = time.time()
    idx, T = panel["idx"], panel["facts"]["n_days"]
    grid_pairs = monthly_grid(idx)
    fam_lists = {fam: (list(fam_slice[fam]) if fam_slice else list(fams[fam]))
                 for fam in ("old", "tail")}
    all_faces = sorted(set(fam_lists["old"]) | set(fam_lists["tail"]))
    faces_res = compute_faces(panel, all_faces)

    # leg i: IC + parent anchor identity (fail-closed at caller)
    ic_rows, ic_drift = {}, []
    for f in SHORTLIST:
        Fmat = faces_res[f][0]
        if Fmat is None:
            ic_rows[f] = None
            continue
        blk = ic_block(Fmat, panel)
        ic_rows[f] = {k: v for k, v in blk.items() if k != "daily"}
        if blk["ic5_mean"] is not None:
            if abs(blk["ic5_mean"] - PARENT_IC_ANCHORS[f]) > PARENT_IC_TOL:
                ic_drift.append([f, blk["ic5_mean"], PARENT_IC_ANCHORS[f]])

    # leg ii: shortlist sleeves (x1 headline + x2 survival face)
    sleeves = {}
    for f in SHORTLIST:
        Fmat = faces_res[f][0]
        if Fmat is None:
            sleeves[f] = None
            continue

        def score_fn(g, _F=Fmat):
            return _F[g]
        sleeves[f] = {
            "x1": blend_sleeve(score_fn, grid_pairs, panel["rets"], COST_FACES["x1"]),
            "x2": blend_sleeve(score_fn, grid_pairs, panel["rets"], COST_FACES["x2"]),
        }

    # leg iii: nulls (frozen band, rng([seed, k]) substream law)
    nulls = null_sleeves(panel, grid_pairs, k_nulls, seed=SEED_NULLS) if k_nulls else {}
    null_stats, null_ic_rows = {}, {}
    for k in sorted(nulls):
        nb = nulls[k]
        icb = ic_block(nb["Fmat"], panel)
        null_ic_rows[k] = {"ic5_mean": icb["ic5_mean"], "ic5_n": icb["ic5_n"]}
        row = {}
        for cname, cost in COST_FACES.items():
            sl = blend_sleeve(nb["score_fn"], grid_pairs, panel["rets"], cost)
            if sl is None:
                row[cname] = None
                continue
            m = sleeve_metrics(sl["series"], idx, sl["first_exec"])
            ew = ew48_window(panel["rets"], sl["first_exec"])
            br, nw = beat_rate(sl["series"], ew, sl["first_exec"], T)
            row[cname] = {"metrics": m, "beat_rate": br, "n_windows": nw,
                          "turnover_total": _r(sl["turnover_total"], 4),
                          "n_rebal": sl["n_rebal"],
                          "excess_x2_vs_ew48_full": (_r(float(np.prod(1.0 + sl["series"]) - 1.0
                                                         - (np.prod(1.0 + ew) - 1.0)), 6)
                                                      if cname == "x2" else None)}
        null_stats[k] = row
    abs_means = [abs(v["ic5_mean"]) for v in null_ic_rows.values()
                 if v["ic5_mean"] is not None]
    null_p95 = round(float(np.percentile(abs_means, 95)), 6) if abs_means else None
    null_br_x2 = [null_stats[k]["x2"]["beat_rate"] for k in null_stats
                  if null_stats[k].get("x2") and null_stats[k]["x2"]["beat_rate"] is not None]
    null_ex_x2 = [null_stats[k]["x2"]["excess_x2_vs_ew48_full"] for k in null_stats
                  if null_stats[k].get("x2") and null_stats[k]["x2"]["excess_x2_vs_ew48_full"] is not None]
    null_sharpe_x1 = [null_stats[k]["x1"]["metrics"]["sharpe"] for k in null_stats
                      if null_stats[k].get("x1") and null_stats[k]["x1"]["metrics"]["sharpe"] is not None]
    vals = np.array([float(v) for v in null_sharpe_x1])
    null_pool = ({"values": [round(float(v), 4) for v in vals],
                  "coverage": {"mu": round(float(vals.mean()), 4),
                               "sigma": round(float(vals.std(ddof=1)), 4),
                               "n_values": int(len(vals)),
                               "schemas_parsed": ["g2_slot_mon_p2:nulls x1 sleeve full-period Sharpe (K=%d in-batch, band [20570000,20570060))" % k_nulls],
                               "known_unparsed": []},
                  "source": "g2_slot_mon_p2 in-batch nulls (monthly random selection sleeves; x1 caliber matches g1 headline face)"}
                 if len(vals) else None)

    # family matrices + PBO + parent identity cross-check (leg v PBO input)
    fam_mats, fam_pbo, fam_cross = {}, {}, {}
    for fam, fl in fam_lists.items():
        mat, fam_sleeves = family_matrix(panel, grid_pairs, faces_res, fl)
        fam_mats[fam] = {"matrix": mat, "sleeves": fam_sleeves}
        fam_cross[fam] = parent_crosscheck(panel, fam_sleeves, parent_census, T) \
            if parent_census is not None else None
        fam_pbo[fam] = cscv_pbo(mat, n_blocks=8) if mat.shape[1] >= 2 else None

    # leg iv: D6 (read-only member canon; carrier stays zero-engine before it)
    d6 = d6_block(panel, sleeves, want=want_d6)

    # leg v: registration chain per face (headline = x1)
    gates = {}
    if want_chain:
        prev_total = None
        if os.path.exists(OUT_JSON):
            try:
                with open(OUT_JSON, encoding="utf-8") as fh:
                    prev_total = int(json.load(fh)["trials_ledger"]["prev_total"])
            except Exception:
                prev_total = None
        head_base = prev_total if prev_total is not None \
            else int(sg.ledger_head()["total"])
        for f in SHORTLIST:
            fam = FACE_FAMILY[f]
            sl1, sl2 = sleeves[f]["x1"], sleeves[f]["x2"]
            m1 = sleeve_metrics(sl1["series"], idx, sl1["first_exec"])
            ew1 = ew48_window(panel["rets"], sl1["first_exec"])
            passive_sh = sleeve_metrics(ew1, idx, sl1["first_exec"])["sharpe"]
            g1 = sg.g1_prime_v2(sharpe_full=m1["sharpe"], returns=sl1["series"],
                                batch_cells=BATCH_CELLS, pool="core48",
                                n_trades=sl1["n_exits_total"],
                                n_entries=sl1["n_buys_total"],
                                null_pool=null_pool,
                                passive_override=passive_sh,
                                n_eff_override=head_base + BATCH_CELLS)
            t_stat = sg.t_from_sharpe(m1["sharpe"], int(len(sl1["series"])))
            m1g = sg.m1_t_value_gate(t_stat, hurdle=M1_HURDLE,
                                     claim_class=M1_CLAIM_CLASS)
            dsr = sg.deflated_sharpe_ratio(sl1["series"],
                                           n_trials=g1["skill_line"]["n_eff"])
            pbo_f = fam_pbo[FACE_FAMILY[f]]
            g2 = sg.g2_registration_v2(g1["pass_v2"], dsr,
                                       float(pbo_f["pbo"]) if pbo_f else None,
                                       dsr_gate=DSR_GATE, pbo_gate=PBO_GATE)
            gates[f] = {
                "family": fam,
                "g1_prime_v2": g1,
                "passive_override_ew48_sharpe": passive_sh,
                "x2_survival": {"x2_sharpe": sleeve_metrics(sl2["series"], idx, sl2["first_exec"])["sharpe"],
                               "pass": bool(sleeve_metrics(sl2["series"], idx, sl2["first_exec"])["sharpe"] > 0)},
                "m1": m1g,
                "dsr": dsr,
                "family_pbo": {"family": fam, "pbo": (float(pbo_f["pbo"]) if pbo_f else None),
                               "verdict": (pbo_f.get("verdict") if pbo_f else None),
                               "matrix_faces": int(fam_mats[fam]["matrix"].shape[1]),
                               "matrix_rows": int(fam_mats[fam]["matrix"].shape[0])},
                "g2_registration_v2": g2,
            }

    # face rows + exit census + verdicts
    face_rows, exit_census, face_verdicts = {}, {}, {}
    for f in SHORTLIST:
        if sleeves[f] is None:
            face_rows[f] = "face compute failed (vendor err) -- honest"
            face_verdicts[f] = {"verdict": "judged-negative",
                                "failed_lines": ["face-compute"]}
            continue
        row = sleeve_face_row(sleeves[f]["x1"], sleeves[f]["x2"], panel,
                              ic_rows[f], T)
        row["regime_segments_x2"] = regime_face(panel, sleeves[f]["x2"])
        face_rows[f] = row
        ec = exit_census_face(sleeves[f]["x1"])
        exit_census[f] = ec
        if want_chain:
            g = gates[f]
            failed = []
            if not g["g1_prime_v2"]["pass_v2"]:
                failed.append("g1_prime_v2")
            if not g["x2_survival"]["pass"]:
                failed.append("x2_survival")
            if not g["m1"].get("pass"):
                failed.append("m1_t_value")
            if not g["g2_registration_v2"]["dsr_ok"]:
                failed.append("dsr")
            if not g["g2_registration_v2"]["pbo_ok"]:
                failed.append("family_pbo")
            d6r = d6["faces"].get(f, {}).get("reject")
            if d6r:
                failed.append("d6_family_merge")
            if ec["blocked"]:
                face_verdicts[f] = {"verdict": "consumption-blocked",
                                    "failed_lines": ["exit_census_non_rank_share"],
                                    "exit_census_other_share": ec["other_share"]}
                continue
            face_verdicts[f] = {
                "verdict": "eligible-for-registration" if not failed else "judged-negative",
                "failed_lines": failed,
                "budget_line": "in-budget at finalize (cap enforced pre-finalize; over-budget = legal stop, never a verdict)",
                "note": "registration execution = hr.py promotion pipeline (monthly face); this batch only judges",
            }

    # sec.5 predictions vs actual (honest reconciliation, descriptive)
    pv = {"note": "pre-registered sec.5 predictions reconciled against run readings; no line was moved"}
    if want_chain:
        g32 = gates[SHORTLIST[1]]
        pv["a_old_032"] = {
            "prediction": "G1'/M1/DSR borderline; x2 survival pass; PBO 0.30-0.60 expected hardest line",
            "actual": {"g1_pass": g32["g1_prime_v2"]["pass_v2"],
                       "g1_line": g32["g1_prime_v2"]["skill_line"]["line"],
                       "x1_sharpe_vs_line": [g32["g1_prime_v2"]["sharpe_full"],
                                              g32["g1_prime_v2"]["skill_line"]["line"]],
                       "m1_t": g32["m1"].get("t_stat", g32["m1"]),
                       "dsr": g32["g2_registration_v2"]["dsr"],
                       "pbo": g32["g2_registration_v2"]["family_pbo"],
                       "x2_survival": g32["x2_survival"]["pass"]}}
        g16 = gates[SHORTLIST[0]]
        pv["b_best_016"] = {
            "prediction": "judged-negative expected (marginal nomination; t>=3.0 likely fail; PBO 0.35-0.65 same-cluster)",
            "actual_verdict": face_verdicts[SHORTLIST[0]]["verdict"],
            "failed_lines": face_verdicts[SHORTLIST[0]].get("failed_lines")}
    if null_br_x2:
        pv["d_null_band"] = {"prediction": "null x2 beat-rate mean 0.00-0.30",
                             "actual_mean": _r(float(np.mean(null_br_x2)), 4)}
    if d6.get("inter_face_pairs"):
        pv["e_inter_face"] = {"prediction": "|corr| >= 0.7 (same-engine lineage, disclosure not gate)",
                              "actual": {k: v["corr"] for k, v in d6["inter_face_pairs"].items()}}
    pv["f_family_matrix_identity"] = {
        "prediction": "45-face recompute identical to parent leg ii (1e-9 on rounded)",
        "actual": {fam: {"n_checked": fam_cross[fam]["n_faces_checked"],
                         "n_drift": fam_cross[fam]["n_drift"]}
                   for fam in fam_cross if fam_cross[fam] is not None}
        if all(v is not None for v in fam_cross.values()) else "parent census not supplied (mini)"}

    payload = {
        "batch": BATCH, "ticket": TICKET, "prereg": PREREG_REL,
        "stage": "stage-2 registration-caliber verdict (independent sec.9 freeze; judge-only: zero registration execution, zero paper claims)",
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(CUTOFF)},
        "verdict_scope": "face-level three-state (eligible-for-registration | judged-negative | consumption-blocked); data gates fail-closed abort pre-finalize (no verdict emitted on data-gate failure)",
        "panel": {
            "members_sha16": INSERVICE_SHA16,
            "n_members": panel["facts"]["n_members"],
            "n_days": panel["facts"]["n_days"],
            "window": "%s..%s" % (panel["facts"]["union_first"], panel["facts"]["union_last"]),
            "mask_fraction": panel["facts"]["mask_fraction"],
            "min_valid_per_member": panel["facts"]["min_valid_per_member"],
            "grid": {"caliber": "monthly (first trading day of each calendar month)",
                     "n_signal_days": len(grid_pairs),
                     "first_signal": str(idx[grid_pairs[0][0]].date()) if grid_pairs else None},
            "ew48_definition": "fixed 1/48 weights, NaN->0 accrual, costless B&H (disclosed; g1 passive_override = same-window EW48 Sharpe)",
            "cost_faces_bp_per_side": {"x1": round(COST_FACES["x1"] * 1e4, 3),
                                       "x2": round(COST_FACES["x2"] * 1e4, 3)},
            "vendor_head": vendor_head(),
        },
        "shortlist": {"faces": list(SHORTLIST), "family_by_face": FACE_FAMILY,
                      "parent_ic_anchors": PARENT_IC_ANCHORS,
                      "lineage": "r647 MON_P1 census 2/47 stage-2 nominations; probe results/_r648bma_p2_probe.json PASS 6/6"},
        "faces": face_rows,
        "exit_census": exit_census,
        "nulls": {"k": k_nulls, "seed": SEED_NULLS, "substream": "rng([seed, k])",
                  "band": [SEED_NULLS, SEED_NULLS + k_nulls],
                  "abs_mean_ic": sorted(_r(x, 6) for x in abs_means),
                  "p95_abs_mean_ic": null_p95,
                  "beat_rate_x2": sorted(x for x in null_br_x2),
                  "beat_rate_x2_mean": _r(float(np.mean(null_br_x2)), 4) if null_br_x2 else None,
                  "excess_x2_vs_ew48_full": sorted(x for x in null_ex_x2),
                  "null_pool_sharpe_x1": null_pool},
        "family_matrices": {
            fam: {"faces": list(fam_mats[fam]["matrix"].columns),
                  "n_rows": int(fam_mats[fam]["matrix"].shape[0]),
                  "first_date": (str(fam_mats[fam]["matrix"].index[0].date())
                                 if fam_mats[fam]["matrix"].shape[0] else None),
                  "pbo_cscv": fam_pbo[fam],
                  "parent_crosscheck": fam_cross[fam]}
            for fam in ("old", "tail")},
        "gates": gates,
        "face_verdicts": face_verdicts,
        "predictions_vs_actual": pv,
        "d6": {"reject_line": D6_REJECT,
               "max_abs_corr_by_face": {f: d6["faces"].get(f, {}).get("max_abs_corr")
                                        for f in SHORTLIST} if want_d6 else None,
               "inter_face_pairs": d6.get("inter_face_pairs"),
               "note": "full numeric face in results/g2_slot_mon_p2/d6_numeric.json (same write)"},
        "audit": {
            "network": "zero", "deterministic": True, "device": "cpu (torch)",
            "engine": "none in the judged carrier (blend approximation; asserted pre-D6); D6 member leg loads the read-only ew6 canon graph (live.paper transitive engine import = rev_osc_stock_p1 r281 finalized precedent, disclosed)",
            "budget_cap_s": BUDGET_CAP_S,
            "exit_axis": "hold-through monthly rank rotation (sec.0.6; falling out of monthly Top-16 = only exit)",
            "ic_anchor_drift": ic_drift,
            "zero_engine_asserted_before_d6": True,
        },
    }
    if ledger:
        payload["trials_ledger"] = sg.append_ledger(
            batch_name=BATCH, batch_trials=BATCH_TRIALS,
            file_name="results/g2_slot_mon_p2/g2_slot_mon_p2_verdict.json",
            evidence_cutoff=CUTOFF,
            note="stage-2 registration-caliber verdict: 2 shortlist cell-faces + 60 in-batch nulls (62 cells) + 60 null IC faces + 2 family-matrix legs = 124 trials (frozen sec.3); monthly-translation lineage r647 MON_P1; judge-only, zero registration execution")
    extras = {
        "fam_mats": fam_mats, "d6_full": d6, "ic_drift": ic_drift,
        "fam_cross": fam_cross, "elapsed": round(time.time() - t_start, 1),
    }
    return payload, extras


# ---------------------------------------------------------------- run / selftest

def _attr_row(payload, elapsed):
    led = payload.get("trials_ledger", {})
    fv = payload["face_verdicts"]
    att = json.load(open(ATTR_JSON, encoding="utf-8-sig"))
    att["entries"].append({
        "batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": led.get("batch_trials", 0),
        "ledger_total_after": led.get("total"),
        "gates": {
            "face_verdicts": {f: fv[f].get("verdict") for f in fv},
            "failed_lines": {f: fv[f].get("failed_lines") for f in fv},
            "g1_pass": {f: payload["gates"][f]["g1_prime_v2"]["pass_v2"]
                        for f in payload["gates"]},
            "g2_eligible_v2": {f: payload["gates"][f]["g2_registration_v2"]["eligible_v2"]
                                for f in payload["gates"]},
            "family_pbo": {fam: payload["family_matrices"][fam]["pbo_cscv"]["pbo"]
                           for fam in ("old", "tail")},
            "d6_reject": {f: payload["d6"]["max_abs_corr_by_face"][f] is not None
                           and payload["d6"]["max_abs_corr_by_face"][f] >= D6_REJECT
                           for f in SHORTLIST},
            "null_p95_abs_mean_ic": payload["nulls"]["p95_abs_mean_ic"],
        },
        "budget_elapsed_s": elapsed,
        "note": "stage-2 registration-caliber verdict (judge-only; registration execution = hr.py promotion pipeline; monthly-translation lineage)",
    })
    with open(ATTR_JSON, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)


def cmd_run():
    if os.path.exists(OUT_JSON):
        _fail("refuse-if-exists: %s already present (single-shot rerun ban; "
              "engineering-fix rerun needs dual-run evidence + fresh prereg "
              "note)" % OUT_JSON)
    t0 = time.time()
    panel = build_panel()
    ok, g, fails, probe, roster, sha, fams, classes = run_gates(panel["facts"])
    print("[g2slotmonp2] gates: %s %s" % ("PASS" if ok else "FAIL", g), flush=True)
    if not ok:
        _fail("data gates failed: %s" % fails)
    if time.time() - t0 > GATES_PREBURN_CAP_S:
        _fail("over-budget abort (panel+gates > %ds); nothing finalized"
              % GATES_PREBURN_CAP_S, code=3)
    assert_carrier_zero_engine("pre-pipeline")
    parent_census = json.load(open(PARENT_CENSUS_JSON, encoding="utf-8"))
    payload, extras = run_pipeline(panel, fams, K_NULLS, parent_census,
                                   want_d6=True, want_chain=True, ledger=True)
    elapsed = extras["elapsed"]
    if elapsed > BUDGET_CAP_S:
        _fail("over-budget abort (%.1fs > %ds cap); nothing finalized"
              % (elapsed, BUDGET_CAP_S), code=3)
    if extras["ic_drift"]:
        _fail("parent-IC anchor drift (mechanical fault, fail-closed): %s"
              % extras["ic_drift"])
    for fam, cr in extras["fam_cross"].items():
        if cr is not None and cr["n_drift"]:
            _fail("family-matrix parent cross-check drift (%s): %s"
                  % (fam, cr["drift"][:5]))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    d6w = dict(extras["d6_full"])
    d6w["batch"] = BATCH
    d6w["evidence_cutoff"] = CUTOFF
    with open(D6_JSON, "w", encoding="utf-8") as fh:
        json.dump(d6w, fh, ensure_ascii=False, indent=1)
    with open(IC_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("face,family,class,ic5_mean,ic5_std,ic5_ir,ic5_n,ic1_mean,"
                 "x1_ann,x1_sharpe,x2_ann,x2_sharpe,x2_beat_rate,verdict\n")
        for f in SHORTLIST:
            r = payload["faces"][f]
            if not isinstance(r, dict):
                continue
            ic = r["ic"]
            fh.write("%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s\n" % (
                f, FACE_FAMILY[f], "volume_price", ic["ic5_mean"], ic["ic5_std"],
                ic["ic5_ir"], ic["ic5_n"], ic["ic1_mean"], r["x1"]["ann"],
                r["x1"]["sharpe"], r["x2"]["ann"], r["x2"]["sharpe"],
                r["x2"]["beat_rate"], payload["face_verdicts"][f]["verdict"]))
    for fam in ("old", "tail"):
        extras["fam_mats"][fam]["matrix"].to_csv(FAM_CSV[fam], float_format="%.10f")

    _attr_row(payload, elapsed)

    print("[g2slotmonp2] verdict done: nulls=%d months=%d elapsed=%.1fs" %
          (payload["nulls"]["k"], payload["panel"]["grid"]["n_signal_days"], elapsed), flush=True)
    for f in SHORTLIST:
        v = payload["face_verdicts"][f]
        print("[g2slotmonp2] %s -> %s failed=%s" %
              (f, v["verdict"], v.get("failed_lines")), flush=True)
    print("[g2slotmonp2] family PBO: old=%s tail=%s" %
          (payload["family_matrices"]["old"]["pbo_cscv"]["pbo"],
           payload["family_matrices"]["tail"]["pbo_cscv"]["pbo"]), flush=True)
    print("[g2slotmonp2] ledger total=%s" %
          payload.get("trials_ledger", {}).get("total"), flush=True)
    print("[g2slotmonp2] products: %s | %s | %s | %s | %s" %
          (OUT_JSON, D6_JSON, IC_CSV, FAM_CSV["old"], FAM_CSV["tail"]), flush=True)
    return 0


def cmd_selftest():
    fails = []
    t0 = time.time()
    # L1 shortlist + family integrity (probe + roster sha + 18/27 counts)
    probe, roster, sha, fams, classes, short = shortlist_and_families()
    l1 = (short == SHORTLIST and sha.startswith(ROSTER_SHA16)
          and len(fams["old"]) == 18 and len(fams["tail"]) == 27
          and SHORTLIST[1] in fams["old"] and SHORTLIST[0] in fams["tail"]
          and classes == {"best_016": "volume_price", "old_032": "volume_price"})
    print("L1 shortlist {old_032,best_016} + roster sha + 18/27 families: %s" %
          ("PASS" if l1 else "FAIL"))
    if not l1:
        fails.append("L1")

    # L2+L3 real panel: cutoff truncation + mask gate
    panel = build_panel()
    f = panel["facts"]
    l2 = f["union_last"] == CUTOFF and f["union_first"] == PANEL_START
    l3 = (f["n_members"] == 48 and not f["bad_columns_members"]
          and not f["dup_date_members"] and f["min_valid_per_member"] >= 100
          and 0.90 <= f["mask_fraction"] <= 0.999)
    print("L2 cutoff truncation (%s..%s): %s" %
          (f["union_first"], f["union_last"], "PASS" if l2 else "FAIL"))
    print("L3 mask gate (48 members, mask_frac %.4f, min_valid %d): %s" %
          (f["mask_fraction"], f["min_valid_per_member"], "PASS" if l3 else "FAIL"))
    if not l2:
        fails.append("L2")
    if not l3:
        fails.append("L3")

    # L4 monthly grid count (81 +/- 2)
    gp = monthly_grid(panel["idx"])
    l4 = 79 <= len(gp) <= 83 and gp[0][1] == gp[0][0] + 1
    print("L4 monthly grid count=%d (81+/-2): %s" % (len(gp), "PASS" if l4 else "FAIL"))
    if not l4:
        fails.append("L4")

    # L5 seed band registered + disjoint
    own = sg.SEED_REGISTRY.get("g2_slot_mon_p2_nulls")
    overlap = []
    for k, v in sg.SEED_REGISTRY.items():
        if k == "g2_slot_mon_p2_nulls":
            continue
        try:
            iv = int(v)
        except (TypeError, ValueError):
            continue
        if SEED_NULLS <= iv < SEED_NULLS + K_NULLS:
            overlap.append(k)
    l5 = own == SEED_NULLS and not overlap
    print("L5 seed registered=%s band [%d,%d) disjoint=%s: %s" %
          (own, SEED_NULLS, SEED_NULLS + K_NULLS, not overlap,
           "PASS" if l5 else "FAIL"))
    if not l5:
        fails.append("L5")

    # L6 cost single-source + vendor HEAD anchor
    l6 = abs(COST_X1 - COST_X1_EXPECT) < 1e-12 and vendor_head() == ANCHOR_HEAD
    print("L6 COST_X1 single-source + vendor HEAD anchor: %s" %
          ("PASS" if l6 else "FAIL"))
    if not l6:
        fails.append("L6")

    # L7 closed-family open + data gates green
    okg, gg, failsg, *_ = run_gates(panel["facts"])
    l7 = okg and not failsg
    print("L7 full data-gates face (12 legs): %s %s" %
          ("PASS" if l7 else "FAIL", failsg if failsg else ""))
    if not l7:
        fails.append("L7")

    # L10 zero-engine carrier: static AST scan (import nodes only -- string
    # literals/docstrings never trip) + runtime assert BEFORE the L8 mini
    # (the D6 member leg loads the read-only ew6 canon graph afterwards --
    # rev_osc_stock_p1 r281 finalized precedent, disclosed in audit).
    import ast
    tree = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    bad = []
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or ""]
        bad += [m for m in mods if m == "engine" or m.startswith("engine.")]
    static_ok = not bad
    try:
        assert_carrier_zero_engine("selftest-pre-mini")
        runtime_ok = True
    except SystemExit:
        runtime_ok = False
    l10 = static_ok and runtime_ok
    print("L10 zero-engine carrier (static=%s, runtime-pre-mini=%s): %s" %
          (static_ok, runtime_ok, "PASS" if l10 else "FAIL"))
    if not l10:
        fails.append("L10")

    # L8 deterministic double-run byte identity (mini pipeline, real panel;
    # nulls K=30 = frozen band prefix, family slice = shortlist + 2 per family)
    fam_slice = {"old": [SHORTLIST[1]] + [x for x in fams["old"] if x != SHORTLIST[1]][:2],
                 "tail": [SHORTLIST[0]] + [x for x in fams["tail"] if x != SHORTLIST[0]][:2]}
    parent_census = json.load(open(PARENT_CENSUS_JSON, encoding="utf-8"))
    p1r, e1 = run_pipeline(panel, fams, 30, parent_census, want_d6=True,
                           want_chain=True, ledger=False, fam_slice=fam_slice)
    p2r, e2 = run_pipeline(panel, fams, 30, parent_census, want_d6=True,
                           want_chain=True, ledger=False, fam_slice=fam_slice)
    b1 = json.dumps(p1r, ensure_ascii=False, sort_keys=False)
    b2 = json.dumps(p2r, ensure_ascii=False, sort_keys=False)
    l8 = (b1 == b2 and len(p1r["faces"]) == 2 and p1r["nulls"]["k"] == 30
          and all(v["verdict"] in ("judged-negative", "eligible-for-registration",
                                   "consumption-blocked")
                  for v in p1r["face_verdicts"].values()))
    print("L8 double-run byte identity + verdict three-state (2 faces/30 nulls): %s" %
          ("PASS" if l8 else "FAIL"))
    if not l8:
        fails.append("L8")

    # L9 parent-IC anchor identity + family cross-check + exit census
    l9 = (not e1["ic_drift"] and not e2["ic_drift"]
          and all(abs(p1r["faces"][x]["ic"]["ic5_mean"] - PARENT_IC_ANCHORS[x]) <= PARENT_IC_TOL
                  for x in SHORTLIST)
          and all(cr["n_drift"] == 0 for cr in e1["fam_cross"].values())
          and all(ec["n_exits_other"] == 0 and ec["other_share"] == 0.0
                  and not ec["blocked"] and len(ec["exit_log"]) == ec["n_rebal"]
                  for ec in p1r["exit_census"].values()))
    print("L9 parent-IC anchors + family-matrix parent identity + exit census "
          "(rank-rotation only, constructive): %s" % ("PASS" if l9 else "FAIL"))
    if not l9:
        fails.append("L9")

    print("selftest: %s fails=%s elapsed=%.1fs" %
          ("PASS" if not fails else "FAIL", fails, time.time() - t0))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
