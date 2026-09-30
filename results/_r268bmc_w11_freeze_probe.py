# -*- coding: utf-8 -*-
"""_r268bmc_w11_freeze_probe.py -- MOM-TIMING-P1 freeze-window probe:
G-ANCHOR face re-verification (prereg s9 step 2) + threshold-constant
zero-drift assertion (step 4) + D6 cells corr FULL protocol (step 5,
prereg s1 high-risk pair VOLATILITY-CE-01 return-face MUST-CHECK).

Read-only, zero engine/admission/REGIME_GUARD touch. Persists NO
performance metric of the batch cells (W9/W10 probe discipline: the
D6 face uses state indicators and return series ONLY for the
preregistered correlation protocol -- no Sharpe, no score, no line).

Single-source law (r456 paradigm): all faces re-derived via verbatim
import from results/_r267bmc_w11_berth_probe.py (build_faces_510300 +
author-verbatim constants MOMENT_WINDOW/EMA_ALPHA/STOP/ORDERS) -- the
same construction face the step-6 runner (next round) verbatim-imports
and parity-asserts (zero re-implementation drift).

Faces:
  A  G-ANCHOR re-verify : panel anchors + cells_state_stats +
                          batch-internal variant corr (state face) +
                          d6_signal_face (vs REGIME_GUARD width /
                          #87 nhnl / VSTD20 second-moment proxy) +
                          extreme_days, compared face-by-face vs
                          frozen berth facts (one-face-off = VOID).
                          Berth probe re-run git-face zero-diff done
                          same window (round report; bit-exact proof).
  T  threshold constants: author-verbatim constants (zero calibration)
                          asserted via import (code defaults) + prereg
                          text tokens (window 20, EMA alpha=2/91,
                          stop -0.10, orders {3,4,5}, K2000 nulls,
                          K1000 starts, 100 splits, N_eff 2003,
                          seed 20327000).
  D  D6 cells full protocol: batch-internal MOM3/4/5 return-face
                          mutual corr (moment-order axis = variant
                          axis: burn-both per family rule, merge
                          clause NOT applicable, berth state-face
                          anchor re-verified in A) + vs registered six
                          daily-return faces (timing batch HAS
                          return-series cells -> no protocol
                          substitution needed, W10 IC-batch contrast
                          honestly noted) + vs T33 in-book rotation
                          cells + vs repo stress state + month-end
                          adjacency faces (W1/W2 calendar neighbors) +
                          berth signal-face max; merge clause at
                          |corr| >= 0.7.

Output: results/_r268bmc_w11_freeze_probe_facts.json
Exit 0 normal / 2 drift or mechanism fault (honest, no masking).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)                             # live.paper import face
sys.path.insert(0, os.path.join(ROOT, "results"))    # probe family
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from _r267bmc_w11_berth_probe import (          # single source (r456)
    build_faces_510300, MOMENT_WINDOW, EMA_ALPHA, STOP, ORDERS)
from _r259bmc_w9_crowding_probe import (         # W9 in-tree faces
    load_core48, below_ma20_share, nhnl_b20)
from _r264bmc_w10_berth_probe import (          # W10 in-tree faces
    load_csv_series, pearson_ind, pct_rank_state, REPO_GC001)
from _r265bmc_w10_freeze_probe import (          # W10 freeze helpers
    _panel_calendar_union)

OUT = os.path.join(ROOT, "results", "_r268bmc_w11_freeze_probe_facts.json")
BERTH_FACTS = os.path.join(
    ROOT, "results", "_r267bmc_w11_berth_probe_facts.json")
PREREG = os.path.join(ROOT, "research", "INNOVATION_QUOTA_W11_PREREG.md")
D6_REJECT = 0.7
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8",
                 "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]
NULLS_K = 2000                    # prereg s0 (occupancy-matched nulls)
STARTS_K = 1000                   # prereg s0 (vstarts band)
SPLITS_K = 100                    # prereg s0 (random half-splits)
BATCH_CELLS = 2003                # prereg s0 N_eff counting law
SEED_INTENDED = 20327000          # prereg s0, registered this window
EVIDENCE_CUTOFF = "2026-09-29"    # prereg s0 as-of face


def _corr2(a: pd.Series, b: pd.Series):
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return None, int(len(j))
    c = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    return (round(c, 4) if np.isfinite(c) else None), int(len(j))


def run() -> int:
    try:
        with open(BERTH_FACTS, encoding="utf-8") as fh:
            berth = json.load(fh)

        # ---------- A G-ANCHOR re-verify (verbatim berth computation) ----------
        s, ret, faces, ind_dicts, stats, date_strs = build_faces_510300()
        derived_panel = {
            "rows": len(date_strs),
            "first_date": date_strs[0],
            "last_date": date_strs[-1],
            "moment_window": MOMENT_WINDOW,
            "ema_alpha": EMA_ALPHA,
            "stop": STOP,
        }
        mism = []
        for k, v in derived_panel.items():
            if berth["panel_510300"].get(k) != v:
                mism.append("panel.%s: %r != frozen %r"
                            % (k, v, berth["panel_510300"].get(k)))
        for n in ORDERS:
            b = berth["cells_state_stats"][str(n)]
            for k, v in stats[n].items():
                if b.get(k) != v:
                    mism.append("stats.MOM%s.%s: %r != frozen %r"
                                % (n, k, v, b.get(k)))

        # batch-internal variant corr (state face -- berth anchor)
        bi = {}
        for a in (3, 4, 5):
            for b_ in (3, 4, 5):
                if a < b_:
                    bi[f"MOM{a}_vs_MOM{b_}"] = round(
                        float(np.corrcoef(faces[a].values,
                                          faces[b_].values)[0, 1]), 4)
        for k, v in bi.items():
            if berth["d6_signal_face"]["batch_internal"].get(k) != v:
                mism.append("bi.%s: %r != frozen %r"
                            % (k, v,
                               berth["d6_signal_face"]["batch_internal"].get(k)))

        # d6 signal faces (berth anchor set)
        c48, _c = load_core48()
        below = below_ma20_share(c48)
        nhnl = nhnl_b20(c48)
        vstd20 = ret.rolling(MOMENT_WINDOW).std()

        def to_dict(ser):
            return {d.strftime("%Y-%m-%d"): float(v)
                    for d, v in ser.dropna().items()}

        d6_anchor = {}
        for name, ser in (
            ("vs_regime_guard_width_below_ma20", below),
            ("vs_87_nhnl_b20", nhnl),
            ("vs_vstd20_second_moment_proxy", vstd20),
        ):
            ser_d = to_dict(ser)
            d6_anchor[name] = {}
            for n in ORDERS:
                r_, n_common = pearson_ind(sorted(ind_dicts[n].keys()),
                                           ind_dicts[n], ser_d)
                d6_anchor[name][f"MOM{n}"] = {"pearson": r_,
                                              "n_common": n_common}
                fb = berth["d6_signal_face"][name][f"MOM{n}"]
                if fb.get("pearson") != r_ or fb.get("n_common") != n_common:
                    mism.append("d6.%s.MOM%s: %r/%r != frozen %r/%r"
                                % (name, n, r_, n_common,
                                   fb.get("pearson"), fb.get("n_common")))

        # extreme-day face (berth anchor)
        absr = ret.abs().sort_values(ascending=False)
        extreme = []
        for dt, v in absr.head(8).items():
            extreme.append({
                "date": str(dt.date()),
                "ret": round(float(ret.loc[dt]), 6),
                "mom5_state": (float(faces[5].loc[dt])
                              if dt in faces[5].index else None),
                "mom3_state": (float(faces[3].loc[dt])
                               if dt in faces[3].index else None),
            })
        for i, (m, b) in enumerate(zip(extreme, berth["extreme_days"])):
            if m != b:
                mism.append("extreme[%d]: %r != frozen %r" % (i, m, b))

        panel_moved = derived_panel["last_date"] != EVIDENCE_CUTOFF
        if berth.get("evidence_cutoff_asof", "").find(EVIDENCE_CUTOFF) < 0:
            mism.append("berth evidence_cutoff drift: %r"
                        % berth.get("evidence_cutoff_asof"))

        # ---------- T threshold-constant zero-drift (step 4) ----------
        th_cmp = {
            "moment_window": MOMENT_WINDOW,
            "ema_alpha": EMA_ALPHA,
            "ema_alpha_is_exact_2_over_91": EMA_ALPHA == 2.0 / 91.0,
            "stop": STOP,
            "orders": list(ORDERS),
            "nulls_K": NULLS_K,
            "starts_K": STARTS_K,
            "splits_K": SPLITS_K,
            "batch_cells_N_eff": BATCH_CELLS,
            "seed_registered": SEED_INTENDED,
        }
        prereg_text = open(PREREG, encoding="utf-8").read()
        th_tokens = {
            "20-day moment window": ("20 交易日矩窗" in prereg_text
                                     and "rolling(20)" in prereg_text),
            "EMA90 alpha=2/91 author-verbatim": ("EMA90" in prereg_text
                                                 and "2/91" in prereg_text),
            "stop -0.10 single line": (("−0.10" in prereg_text)
                                       or ("-0.10" in prereg_text)),
            "orders {3,4,5} three-leg full spectrum": "{3,4,5}" in prereg_text,
            "K2000 occupancy-matched nulls": "K2000" in prereg_text,
            "starts K1000": "K1000" in prereg_text,
            "splits 100": "splits 100" in prereg_text,
            "BATCH_CELLS 2003": "2003" in prereg_text,
            "seed 20327000": "20327000" in prereg_text,
        }
        th_mism = []
        if th_cmp["moment_window"] != 20:
            th_mism.append("moment_window %r" % th_cmp["moment_window"])
        if not th_cmp["ema_alpha_is_exact_2_over_91"]:
            th_mism.append("ema_alpha %r" % th_cmp["ema_alpha"])
        if th_cmp["stop"] != -0.10:
            th_mism.append("stop %r" % th_cmp["stop"])
        if tuple(th_cmp["orders"]) != (3, 4, 5):
            th_mism.append("orders %r" % (th_cmp["orders"],))
        for tok, ok in th_tokens.items():
            if not ok:
                th_mism.append("prereg token missing: %s" % tok)
        import science_gates as sg
        if sg.SEED_REGISTRY.get("innovation_quota_w11_momtiming") != SEED_INTENDED:
            th_mism.append("SEED_REGISTRY key != %r" % SEED_INTENDED)

        if mism or th_mism:
            for m in (mism + th_mism)[:12]:
                print("  drift:", m)
            print("GATE-REFUSE(exit2): freeze-window re-verify drift "
                  "(%d anchor faces, %d constants) vs frozen berth facts"
                  % (len(mism), len(th_mism)))
            return 2
        print("G-ANCHOR re-verify: ALL faces bit-exact vs berth facts "
              "(panel %s..%s %d rows; state stats 3/4/5 = %d/%d/%d long "
              "days, entries %s; batch-internal state-face %s; "
              "cutoff %s, panel last %s unmoved, zero incremental segment)"
              % (derived_panel["first_date"], derived_panel["last_date"],
                 derived_panel["rows"],
                 stats[3]["long_days"], stats[4]["long_days"],
                 stats[5]["long_days"],
                 [stats[n]["entries"] for n in ORDERS], bi,
                 EVIDENCE_CUTOFF, derived_panel["last_date"]))

        # ---------- D D6 cells face FULL protocol (step 5) ----------
        # cell return faces: r_cell(t) = pos(t-1) * r(t)  (lag-1 exposure,
        # close-to-close; runner T+1-open fills differ only at sub-day
        # granularity -- immaterial for a daily corr face, honest note)
        cell_rets = {}
        for n in ORDERS:
            cell_rets[n] = (faces[n].shift(1) * ret).dropna()

        bi_ret = {}
        for a in (3, 4, 5):
            for b_ in (3, 4, 5):
                if a < b_:
                    c, _ = _corr2(cell_rets[a], cell_rets[b_])
                    bi_ret[f"MOM{a}_vs_MOM{b_}"] = c

        t33_idx = _panel_calendar_union("2026-09-24")   # T33 own cutoff face
        vs_registered = {}
        registered_max = {}
        try:
            gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
            reg_rets = gates.get("registered_rets", {})
            for rid, rl in reg_rets.items():
                rs = pd.Series(rl, index=t33_idx[1:len(rl) + 1])
                vs_registered[rid] = {}
                for n in ORDERS:
                    c, nc = _corr2(cell_rets[n], rs)
                    vs_registered[rid][f"MOM{n}"] = {"corr": c, "n_common": nc}
        except FileNotFoundError:
            vs_registered = {"note": "t33 gates json absent"}

        t33_rows = {}
        with open(T33_CELLS_PATH, encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if r.get("status") == "ok" and r.get("face") == "base" \
                        and r.get("cand") in T33_ROT_CELLS and "rets" in r:
                    t33_rows[r["cand"]] = pd.Series(
                        r["rets"], index=t33_idx[1:len(r["rets"]) + 1])
        vs_t33 = {}
        for cid in T33_ROT_CELLS:
            if cid not in t33_rows:
                vs_t33[cid] = None
                continue
            vs_t33[cid] = {}
            for n in ORDERS:
                c, nc = _corr2(cell_rets[n], t33_rows[cid])
                vs_t33[cid][f"MOM{n}"] = c

        # W1/W2 calendar-neighbor state faces (repo stress + month-end
        # adjacency), state-day indicator protocol (W10 analog)
        repo = load_csv_series(REPO_GC001, "date", "close")
        rd = sorted(repo)
        rstate = pct_rank_state(rd, [repo[x] for x in rd])
        stress_face = {d: (1.0 if v[0] else 0.0) for d, v in rstate.items()}
        me_face = {d: (1.0 if (d[8:10] >= "28" or d[8:10] <= "03") else 0.0)
                   for d in ind_dicts[3]}
        cal_neighbors = {}
        for label, sface in (("vs_repo_stress_state", stress_face),
                             ("vs_month_end_adjacent_calendar", me_face)):
            cal_neighbors[label] = {}
            for n in ORDERS:
                r_, n_common = pearson_ind(sorted(ind_dicts[n].keys()),
                                           ind_dicts[n], sface)
                cal_neighbors[label][f"MOM{n}"] = {"pearson": r_,
                                                   "n_common": n_common}

        # merge-clause decision: cross-family faces only
        merge_clause_applied = []
        clause_vals = []
        for rid, per in vs_registered.items():
            if isinstance(per, dict):
                for k, v in per.items():
                    if isinstance(v, dict) and v.get("corr") is not None:
                        clause_vals.append((abs(v["corr"]), f"registered.{rid}.{k}"))
        for cid, per in vs_t33.items():
            if isinstance(per, dict):
                for k, v in per.items():
                    if v is not None:
                        clause_vals.append((abs(v), f"t33.{cid}.{k}"))
        for label, per in cal_neighbors.items():
            for k, v in per.items():
                if v.get("pearson") is not None:
                    clause_vals.append((abs(v["pearson"]),
                                        f"calendar.{label}.{k}"))
        for label, per in d6_anchor.items():
            for k, v in per.items():
                if v.get("pearson") is not None:
                    clause_vals.append((abs(v["pearson"]),
                                        f"anchor_signal.{label}.{k}"))
        for cval, tag in clause_vals:
            if cval >= D6_REJECT:
                merge_clause_applied.append({"tag": tag, "abs_corr": cval})
        clause_eligible_max = round(max([c for c, _ in clause_vals] + [0.0]), 4)

        # high-risk pair extraction (prereg s1 MUST-CHECK)
        hz = vs_registered.get("VOLATILITY-CE-01", {})
        hz_face = {k: (v["corr"] if isinstance(v, dict) else None)
                   for k, v in hz.items()} if isinstance(hz, dict) else None

        facts = {
            "probe": "MOM-TIMING-P1 freeze-window G-ANCHOR re-verify + "
                     "threshold constants + D6 cells FULL protocol",
            "machine": "bm-c", "round": "r268",
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "panel": {"rows": derived_panel["rows"],
                      "first_date": derived_panel["first_date"],
                      "last_date": derived_panel["last_date"],
                      "incremental_segment": ("NONE -- panel last date "
                                              "2026-09-29 unmoved vs berth "
                                              "facts" if not panel_moved
                                              else "MOVED")},
            "g_anchor_reverify": {
                "pass": True,
                "reference": "results/_r267bmc_w11_berth_probe_facts.json "
                             "(berth frozen facts; berth probe re-run "
                             "git-face zero-diff same window, bit-exact "
                             "proof in round report)",
                "n_face_checks": (len(derived_panel)
                                  + 9 * len(ORDERS) + len(bi)
                                  + 2 * len(ORDERS) * len(d6_anchor)
                                  + len(extreme)),
                "panel_510300": derived_panel,
                "cells_state_stats": stats,
                "batch_internal_state_face": bi,
                "d6_signal_face_anchors": d6_anchor,
                "extreme_days": extreme,
                "note": "one-face-off = config mismatch VOID per prereg "
                        "G-ANCHOR law (s9 step 2)",
            },
            "threshold_constants_zero_drift": {
                "pass": True,
                "compared": th_cmp,
                "prereg_tokens": th_tokens,
                "note": "author-verbatim constants, zero calibration "
                        "(moment orders {3,4,5} = r263 param-freeze "
                        "candidate carried verbatim; window 20 / EMA "
                        "alpha=2/91 / stop -0.10 = author-verbatim, no "
                        "threshold search); code defaults asserted via "
                        "verbatim import from berth probe + prereg text "
                        "tokens + SEED_REGISTRY live view",
            },
            "d6_cells_full_protocol": {
                "batch_internal_return_face": bi_ret,
                "batch_internal_note":
                    "MOM3/4/5 = variant faces of ONE construction axis "
                    "(moment order, r263 full-spectrum burn) -- variant "
                    "pairs burn-both per family rule (W8/W9 precedent); "
                    "merge clause NOT applicable to variant axis "
                    "(prereg s1); state-face anchor 0.7403 MOM3-MOM5 "
                    "re-verified bit-exact in g_anchor",
                "return_face_note":
                    "r_cell(t) = pos(t-1) * r(t) lag-1 close-to-close "
                    "exposure map; runner T+1-open fills differ only at "
                    "sub-day granularity (honest approximation for the "
                    "daily corr face); timing batch HAS return-series "
                    "cells -> registered-six return-face corr measured "
                    "directly, NO W10 IC-batch protocol substitution "
                    "needed",
                "vs_registered_six_return_face": vs_registered,
                "vs_t33_rotation_cells_return_face": vs_t33,
                "vs_calendar_neighbor_state_faces": cal_neighbors,
                "berth_signal_face_anchors": d6_anchor,
                "high_risk_pair_volatility_ce_01": hz_face,
                "clause_eligible_max_abs_corr": clause_eligible_max,
                "merge_clause_threshold": D6_REJECT,
                "merge_clause_applied": merge_clause_applied,
            },
            "single_source_note": "construction single source = "
                                  "results/_r267bmc_w11_berth_probe.py "
                                  "(build_faces_510300 + constants) -- "
                                  "the step-6 runner verbatim-imports and "
                                  "parity-asserts (r456 zero-drift paradigm)",
        }
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, ensure_ascii=False, indent=1)
        print("threshold constants: zero-drift PASS (author-verbatim, "
              "code defaults + prereg tokens + registry live view)")
        print("D6 batch-internal return-face:", bi_ret)
        print("D6 vs registered six:",
              {rid: {k: (v["corr"] if isinstance(v, dict) else None)
                     for k, v in per.items()}
               for rid, per in vs_registered.items()
               if isinstance(per, dict)})
        print("D6 vs T33 cells:", vs_t33)
        print("D6 calendar neighbors:", cal_neighbors)
        print("D6 HIGH-RISK PAIR VOLATILITY-CE-01 return face:", hz_face)
        print("D6 clause-eligible max |corr| =", clause_eligible_max,
              "< 0.7:", clause_eligible_max < D6_REJECT)
        print("D6 merge clause applied:", merge_clause_applied or "NONE")
        return 0
    except Exception as exc:            # honest fault, no masking
        import traceback
        traceback.print_exc()
        print("PROBE FAULT: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
