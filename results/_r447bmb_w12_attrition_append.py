# r447 bm-b: append TRIAL_LAB_W12_SCREEN + TRIAL_LAB_W12_JUDGE attrition rows
# (W11 _r444bmb_w11_attrition_append.py precedent schema verbatim-mirrored;
#  append-only to history chain in both faces: shared results/gate_attrition.json
#  + lane results/gate_attrition.bm-b.json)
# All numbers live-read from results/trial_labor_w12/*.json -- zero hand-copy.
import json, os

R = "results/trial_labor_w12"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


screen = load(f"{R}/w12_screen.json")
judge = load(f"{R}/w12_judge.json")
intake = load(f"{R}/w12_intake.json")
nf = screen["null_family"]

sl = screen["trials_ledger"]
jl = judge["trials_ledger"]
assert sl["total"] == 355083 and sl["batch_trials"] == 1059, (sl,)
assert jl["prev_total"] == sl["total"], "ledger chain broken"
assert jl["batch_trials"] == judge["n_judged_cells"] == 188, (jl,)

rsqr_seg = screen["rsqr_segmented_survival"]
std_seg = screen["std_segmented_survival"]
mom_seg = screen["mom_segmented_survival"]


def rate(seg, k):
    return seg[k]["survival_rate"]


def ratio(seg, k, base="none"):
    return rate(seg, k) / rate(seg, base)


screen_row = {
    "batch": "TRIAL_LAB_W12_SCREEN",
    "ts": screen["generated"],
    "kind": "measurement",
    "retro_fill": False,
    "cells_ledger_delta": sl["batch_trials"],
    "ledger_total_after": sl["total"],
    "gates": {
        "screen_pass": {
            "n_candidates": screen["n_distinct"],
            "n_survivors": screen["n_survivors"],
            "line": ("beat6m_rate > null_p95 strictly-greater "
                     f"(null_p95={nf['p95_line']}, prereg sec.3 frozen)"),
        },
        "null_face": {
            "p50": nf["median"],
            "p95": nf["p95_line"],
            "n": screen["k_nulls"],
            "note": ("K=200 fifteen-tuple axis nulls with mom+std+rsqr legs, "
                     f"seed {nf['seed']}; p50 {nf['median']} within prereg "
                     "sec.5.2 band [0.50,0.52] (seventh consecutive wave "
                     ">0.50 drift-lineage continuation); p95 "
                     f"{nf['p95_line']} within twelve-wave band; screen "
                     "survival line = program-frozen null p95 (W2-W11 "
                     "identical law)"),
        },
        "rsqr_face": {
            "segmented_survival": rsqr_seg,
            "note": ("RSQR new face direction intel (W12 true question, "
                     "adopted from bm-a r447 probe package): rsqr10_hi "
                     f"{rate(rsqr_seg,'rsqr10_hi'):.5f} = "
                     f"{ratio(rsqr_seg,'rsqr10_hi'):.2f}x vs none -- BELOW "
                     "prereg sec.5.1 >=1.3x prediction (enrichment MISS); "
                     "rsqr20_hi "
                     f"{rate(rsqr_seg,'rsqr20_hi'):.5f} = "
                     f"{ratio(rsqr_seg,'rsqr20_hi'):.2f}x STRONG "
                     "anti-enrichment (first RSQR-axis screen face, "
                     "10/20 asymmetry mirrors STD W11 lineage); RSQR axis "
                     "family fails supply-line promotion on screen "
                     "evidence"),
        },
        "std_face": {
            "segmented_survival": std_seg,
            "note": ("STD carried face replication (W11 1.40x/0.72x "
                     "asymmetry): std10_hi "
                     f"{rate(std_seg,'std10_hi'):.5f} = "
                     f"{ratio(std_seg,'std10_hi'):.2f}x vs none "
                     f"{rate(std_seg,'none'):.5f}; std20_hi "
                     f"{rate(std_seg,'std20_hi'):.5f} = "
                     f"{ratio(std_seg,'std20_hi'):.2f}x -- 10d-positive/"
                     "20d-flat asymmetry replicated"),
        },
        "mom_face": {
            "segmented_survival": mom_seg,
            "note": ("MOM carried face enrichment decay lineage third "
                     "reading: mom_oversold "
                     f"{rate(mom_seg,'mom_oversold'):.5f} vs none "
                     f"{rate(mom_seg,'none'):.5f} = "
                     f"{ratio(mom_seg,'mom_oversold'):.2f}x -- W10 1.88x -> "
                     "W11 1.25x -> W12 "
                     f"{ratio(mom_seg,'mom_oversold'):.2f}x cross-wave "
                     "decay continuation (twelve-source exclusion book "
                     "accumulation)"),
        },
    },
    "eliminated": screen["n_distinct"] - screen["n_survivors"],
    "refs": {
        "prereg": "research/TRIAL_LABOR_W12_PREREG.md",
        "results": f"{R}/w12_screen.json",
        "ticket": "T-2026-09-30-124",
    },
}


def face_g1(facejudg):
    return {k: v.get("n_g1_pass", 0) for k, v in facejudg.items()}


best = max(judge["cells"],
           key=lambda c: c.get("legL_sharpe_full")
           if isinstance(c.get("legL_sharpe_full"), (int, float)) else -9)
g1b = best["g1_prime_v2"]
line = g1b["skill_line"]
best_dsr = max(judge["cells"],
               key=lambda c: (c.get("dsr") or {}).get("dsr")
               if isinstance((c.get("dsr") or {}).get("dsr"),
                            (int, float)) else -1)
faces = {
    "gate": face_g1(judge["gate_face_judgment"]),
    "vol": face_g1(judge["vol_face_judgment"]),
    "yang": face_g1(judge["yang_face_judgment"]),
    "vconf": face_g1(judge["vconf_face_judgment"]),
    "streak": face_g1(judge["streak_face_judgment"]),
    "tstate": face_g1(judge["tstate_face_judgment"]),
    "amp": face_g1(judge["amp_face_judgment"]),
    "mom": face_g1(judge["mom_face_judgment"]),
    "std": face_g1(judge["std_face_judgment"]),
    "rsqr": face_g1(judge["rsqr_face_judgment"]),
}
total_zero = all(v == 0 for f in faces.values() for v in f.values())

judge_row = {
    "batch": "TRIAL_LAB_W12_JUDGE",
    "ts": judge["generated"],
    "kind": "judgment",
    "retro_fill": False,
    "cells_ledger_delta": jl["batch_trials"],
    "ledger_total_after": jl["total"],
    "gates": {
        "g1_prime_v2": {
            "n": judge["n_judged_cells"],
            "n_pass": sum(1 for c in judge["cells"] if c.get("g1_pass")),
            "line": ("skill_line_v2 per-cell (ledger_head live read); top "
                     f"cell {best['candidate_id']} legL sharpe_full="
                     f"{best['legL_sharpe_full']} vs line={line['line']} "
                     f"(n_eff={line['n_eff']}) -- line_ok "
                     f"{bool(best.get('g1_pass'))}; ten-face "
                     "total (gate/vol/yang/vconf/streak/tstate/amp/mom/std/"
                     "rsqr); best-cell bootstrap ci95 "
                     f"[{g1b['bootstrap_ci']['ci95_low']},"
                     f"{g1b['bootstrap_ci']['ci95_high']}]"),
            "all_face_total_zero": total_zero,
            "faces": faces,
        },
        "g2_registration_v2": {
            "n_eligible": judge["n_eligible_g2"],
            "top_dsr": (best_dsr.get("dsr") or {}).get("dsr"),
            "top_dsr_cell": best_dsr.get("cell_id"),
            "n_trials": jl["prev_total"],
            "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25",
        },
        "e_fp_nominal_5pct": judge["n_wave_disclosure"]["E_FP_nominal_5pct"],
        "family_pbo": judge["family_pbo"],
    },
    "eliminated": judge["n_judged_cells"],
    "refs": {
        "prereg": "research/TRIAL_LABOR_W12_PREREG.md",
        "results": f"{R}/w12_judge.json",
        "intake": (f"{R}/w12_intake.json (lawful-zero n_eligible="
                   f"{intake['n_eligible']}, r447 harvest round)"),
        "ticket": "T-2026-09-30-124",
    },
}

for p in ("results/gate_attrition.json", "results/gate_attrition.bm-b.json"):
    d = load(p)
    hist = d["history"]
    have = {h.get("batch") for h in hist}
    for row in (screen_row, judge_row):
        if row["batch"] in have:
            print(f"SKIP {row['batch']} already in {p}")
            continue
        hist.append(row)
        print(f"APPEND {row['batch']} -> {p} (history "
              f"{len(hist)-1}->{len(hist)})")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

print("attrition append done: W12 SCREEN+JUDGE rows in both faces")
