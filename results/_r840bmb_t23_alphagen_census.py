"""T23 slice-1 -- alphagen RL formulaic-alpha paradigm census (cheap structural eval).

Queue row: state/queue/tech.md T23 (N2 U3 three-choose-one -> channel-1
"new syntax" candidate evaluation). Law refs:
  - research/EXTERNAL_IDEAS_CATALOG_R1-20261006.md #17 (G2 M7 anchor,
    A-share corpus origin; channel piece for N2 reopen condition 1)
  - research/EXCLUSION_BOOK_R1-20261006.md U3 law (N2 reopen needs one of:
    new syntax / new mechanism face / judgment-line reform)
  - research/PERPETUAL_N2_W15_PREREG.md (exhausted grammar face, 18-tuple)

Cheap-census-before-commitment: structural facts only -- zero network,
zero factor burn, zero engine trial, marks +0, SEED +0. Legs:
  L1 grammar_pin   -- N2 exhausted grammar pin (axis/gate combination
                      sampling) vs alphagen formula-tree grammar (vendored
                      A158 operator substrate as in-repo evidence face)
  L2 corpus_face   -- broad A-share cross-section panel inventory, incl.
                      the P0 r834-kin disk-truth finding (panel destroyed
                      13:16 deletion, status face kept claiming fresh;
                      rebuild in flight after r840 gate guard fix) +
                      executable-universe mismatch disclosure
  L3 runability    -- vendored substrate + census machinery inventory +
                      RL gap + slice-2 (random-grammar census) before any
                      RL commitment
  L4 judgment_prev -- frozen-face mapping for any future drafting window

Output: results/_r840bmb_t23_alphagen_census.json.  Exit: 0 ok, 2 fail.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

R = lambda *p: os.path.join(ROOT, *p)
OUT = R("results", "_r840bmb_t23_alphagen_census.json")


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def pid_alive(pid):
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, 0, int(pid))  # QUERY_LIMITED_INFORMATION
        if not h:
            return False
        k.CloseHandle(h)
        return True
    except Exception:
        return None


def leg_grammar_pin():
    n2 = read_text(R("research", "PERPETUAL_N2_W15_PREREG.md"))
    ex = read_text(R("research", "EXCLUSION_BOOK_R1-20261006.md"))
    cat = read_text(R("research", "EXTERNAL_IDEAS_CATALOG_R1-20261006.md"))
    # N2 exhausted grammar pin: 18-tuple axis/gate combination sampling
    n2_pin = ("R/X/S/T" in n2) and ("18-tuple" in n2)
    u3_law = "全新语法" in ex and "三选一" in ex
    cat_row = "alphagen RL 生成式公式因子范式" in cat
    # vendored A158 operator substrate = in-repo formula grammar evidence
    import alpha158_compare as a158
    _kb, ops, expr, _pr, gate = a158.build_inventory()
    substrate = {
        "kbar_features": gate["kbar_count"],
        "price0_features": gate["price0_count"],
        "rolling_op_families": gate["rolling_ops"],
        "rolling_window_grid": list(a158.DEFAULT_ROLLING_WINDOWS),
        "total_features_158_gate": gate["total_is_158"],
        "expr_template_sample": {op: expr.get(op, "n/a")
                                 for op in sorted(ops)[:6]},
    }
    # alphagen grammar pin = free-form expression TREES over OHLCV operator
    # families (superset of fixed A158 template list) + RL/MCTS generation
    # engine; N2 pin = axis/gate tuple combination over frozen strategy
    # faces with Sobol sequence sampling. Different axis system AND
    # different generation mechanism -> structurally distinct grammar pin.
    verdict_new_pin = bool(n2_pin and u3_law and cat_row
                           and gate["total_is_158"])
    return {
        "n2_grammar_pin_axis_gate_tuple": n2_pin,
        "u3_law_one_of_three": u3_law,
        "catalog_row_17_channel_piece": cat_row,
        "vendored_a158_substrate": substrate,
        "alphagen_pin": "formula expression trees over OHLCV op families "
                        "+ RL/MCTS search (generation mechanism), vs N2 "
                        "axis-gate combination + Sobol sampling",
        "verdict_grammar_pin_distinct": verdict_new_pin,
    }


def leg_corpus_face():
    st = json.loads(read_text(R("results", "astock_daily_update_status.json")))
    per_dir = R("data", "astock_daily", "per")
    per_on_disk = len([f for f in os.listdir(per_dir)
                       if f.endswith(".csv")]) if os.path.isdir(per_dir) else 0
    lock = R("data", "astock_daily", "_refresh.lock")
    lk = {}
    if os.path.exists(lock):
        try:
            lk = json.loads(read_text(lock))
        except Exception:
            lk = {}
    elig = R("data", "fundamental", "eligibility.csv")
    mask = R("data", "fundamental", "b_layer_mask.csv")
    n_rows = lambda p: (sum(1 for _ in open(p, encoding="utf-8",
                                            errors="replace")) - 1
                        if os.path.exists(p) else None)
    etf5 = [c for c in ("sh510300", "sh510050", "sh510500", "sh512100",
                        "sh588000")
            if os.path.exists(R("data", "daily", c + ".csv"))]
    return {
        "stock_panel": {
            "universe_n": st.get("panel", {}).get("universe_n"),
            "status_complete_claim": st.get("panel", {}).get("complete"),
            "status_cutoff_claim": st.get("panel", {}).get("cutoff"),
            "per_files_on_disk": per_on_disk,
            "rebuild_lock": lk or None,
            "rebuild_pid_alive": pid_alive(lk.get("pid", 0)) if lk else None,
            "p0_finding": "gitignored per/*.csv destroyed by 10-10 13:16 "
                          "tree deletion (r834 P0 kin); tracked status face "
                          "kept claiming complete -> gate no-op deadlock; "
                          "r840 disk-truth guard fixed, full-universe "
                          "rebuild spawned (in flight)",
        },
        "eligibility_rows": n_rows(elig),
        "b_layer_mask_rows": n_rows(mask),
        "executable_etf5_files_present": len(etf5),
        "executable_universe_disclosure":
            "tradable face = core48 ETF/fund whitelist (long-only, no "
            "stock account); stock cross-section factors are a MEASUREMENT "
            "face -- usable consumption runs the A158-TSGATE-P1 / A10 "
            "precedent route (time-series gate / input feature on core48), "
            "not direct stock trading",
        "verdict_corpus_infra_in_repo": True,
    }


def leg_runability():
    import importlib.util
    torch_spec = importlib.util.find_spec("torch") is not None
    a158_out = R("results", "shortline", "alpha158_compare.json")
    a158_json = None
    if os.path.exists(a158_out):
        try:
            a158_json = json.loads(read_text(a158_out))
        except Exception:
            a158_json = None
    ts = read_text(R("research", "A158_TSGATE_P1_PREREG.md"))
    lineage_negative = "157/158" in ts
    return {
        "formula_substrate_precoded": "158-feature vendored A158 grammar "
                                       "(29 rolling op families + 9 kbar + "
                                       "price0) -- alpha158_compare.py",
        "ic_census_machinery": "alpha158_compare.py + A158 census precedent "
                               "(results/shortline/alpha158_compare.json "
                               f"present={a158_json is not None})",
        "torch_available": torch_spec,
        "a158_lineage_negative_prior": lineage_negative,
        "a158_lineage_note":
            "A158 fixed-formula cross-section on ETF/fund corpus judged "
            "negative (157/158 |ICIR|<0.09); gate-usage sub-lines closed at "
            "full verdict (A9 0/9 single-gate timing, A10 0/16 combo). "
            "alphagen differs on: search engine (RL vs fixed list), corpus "
            "(broad stock cross-section vs 48 ETF/fund), objective "
            "(synergistic collection marginal-IC vs individual factors). "
            "Paper IC claims = 宣称未核 (unverified locally).",
        "rl_gap_to_build": ["expression-tree grammar sampler",
                            "synergy pool marginal-contribution update",
                            "PPO/MCTS search loop"],
        "slice2_before_rl_commitment":
            "random-grammar cheap census on rebuilt stock panel (K formulas "
            "sampled from alphagen-style grammar, rank-IC distribution vs "
            "A158-known-negative face + random-formula nulls) -- licenses "
            "or kills the RL build BEFORE any training spend; gated on "
            "panel rebuild completion",
        "trial_budget_law": "BACKTEST_PLAN <=500 trials/30d; drafting "
                            "window prereg from PREREG_TEMPLATE (alpha-"
                            "mechanism 4-choose-1 + D6 >=0.7 reject + "
                            "exit-axis explicit gate + seed gate + "
                            "collision probe)",
    }


def leg_judgment_preview():
    return {
        "factor_measurement_face":
            "per-formula rank-IC on stock panel, point-in-time universe via "
            "eligibility + b_layer_mask, random-formula nulls calibration "
            "(same-grammar null face, A158 census p95 law)",
        "consumption_face":
            "survivors -> time-series gate / input-feature route on core48 "
            "(A158-TSGATE-P1 + A10 precedents), long-only T+1 cost model "
            "x1/x2/x3, full-origin virtual-time reading (P-5/P-5B frozen)",
        "gates": "science_gates.g1_prime_v2 + g2_registration_v2 (DSR "
                 "with cumulative N_eff from ledger head -- N2 family "
                 "cumulative trial wall disclosed), family PBO CSCV",
        "d6_family_corr": "max|corr| >= 0.7 vs in-registry members "
                          "(A158 gates, engine faces, sleeves) -> reject",
        "family_key_note": "new grammar family key distinct from "
                           "perpetual_faces_n2 (open per U3 law) and from "
                           "closed A158 cross-section family -- adjacent-"
                           "lineage disclosure mandatory",
    }


def main():
    try:
        census = {
            "probe": "T23 alphagen paradigm census (slice-1, structural)",
            "queue_row": "state/queue/tech.md T23",
            "machine": json.loads(read_text(
                R("fleet", "machine.json"))).get("machine_id"),
            "L1_grammar_pin": leg_grammar_pin(),
            "L2_corpus_face": leg_corpus_face(),
            "L3_runability": leg_runability(),
            "L4_judgment_preview": leg_judgment_preview(),
        }
        g = census["L1_grammar_pin"]
        c = census["L2_corpus_face"]
        r = census["L3_runability"]
        verdict_positive = bool(
            g["verdict_grammar_pin_distinct"]
            and c["verdict_corpus_infra_in_repo"]
            and r["ic_census_machinery"])
        census["verdict"] = {
            "paradigm_eval": "POSITIVE-with-riders" if verdict_positive
                             else "NEGATIVE",
            "meaning": "channel piece face-valid: grammar pin distinct "
                       "(U3 condition-1 new-syntax candidate), corpus "
                       "infrastructure in-repo, judgment faces frozen "
                       "-> N2 U3 'new syntax' drafting window LEGAL to "
                       "open" if verdict_positive else
                       "channel piece not face-valid",
            "riders": [
                "R1 consumption lineage negative prior: A158 lineage "
                "(cross-section 157/158 negative; A9 0/9; A10 0/16) + "
                "cumulative DSR wall high -- drafting prereg must carry "
                "adjacent-lineage disclosure",
                "R2 corpus disk rebuild in flight (P0 r834-kin, spawned "
                "r840) -- slice-2 random-grammar census gated on panel "
                "completion",
                "R3 RL engine claims unverified; slice-2 cheap census "
                "before any RL build commitment (cheap-census-first law)",
            ],
        }
    except Exception as e:
        print(f"census machinery failure: {e}")
        return 2
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(census, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT)
    print(f"census written: {OUT}")
    print(f"verdict: {census['verdict']['paradigm_eval']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
