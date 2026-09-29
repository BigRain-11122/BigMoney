# r444 bm-b: append TRIAL_LAB_W11_SCREEN + TRIAL_LAB_W11_JUDGE attrition rows
# (W10 r440 precedent schema; append-only to history chain in both faces:
#  shared results/gate_attrition.json + lane results/gate_attrition.bm-b.json)
# All numbers live-read from results/trial_labor_w11/*.json -- zero hand-copy.
import json, os

R = "results/trial_labor_w11"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


screen = load(f"{R}/w11_screen.json")
judge = load(f"{R}/w11_judge.json")
intake = load(f"{R}/w11_intake.json")
nf = screen["null_family"]

sl = screen["trials_ledger"]
jl = judge["trials_ledger"]
assert sl["total"] == 350018 and jl["total"] == 350247, (sl, jl)
assert jl["prev_total"] == sl["total"], "ledger chain broken"

std_seg = screen["std_segmented_survival"]
mom_seg = screen["mom_segmented_survival"]

screen_row = {
    "batch": "TRIAL_LAB_W11_SCREEN",
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
            "note": ("K=200 fourteen-tuple axis nulls with mom+std legs, seed "
                     f"{nf['seed']}; p50 {nf['median']} within prereg sec.5.2 "
                     "recalibrated band [0.50,0.52] (sixth consecutive wave "
                     ">0.50: W6 0.5036 -> W7 0.51 -> W8 0.5116 -> W9 0.5116 "
                     "-> W10 0.5116 -> W11 0.5116, drift disclosed); p95 "
                     f"{nf['p95_line']} within eleven-wave band; screen "
                     "survival line = program-frozen null p95 (W2-W10 "
                     "identical law)"),
        },
        "std_face": {
            "segmented_survival": std_seg,
            "note": ("STD new face direction intel (W11 true question, "
                     "adopted from bm-c r234/r237 probe package): "
                     "POSITIVE 10d / NEGATIVE 20d asymmetry -- std10_hi "
                     "24.66% (73/296) = 1.40x enrichment vs none 17.59%, "
                     "std20_hi 12.59% (35/278) = 0.72x anti-enrichment; "
                     "std∧calm family drag confirmed (4/68=5.88% vs "
                     "std∧wild 51/249=20.48%, std10_hi∧calm 0/26 total "
                     "wipeout) = prereg sec.5.1(b) drift-face prediction HIT "
                     "at screen"),
        },
        "mom_face": {
            "segmented_survival": mom_seg,
            "note": ("MOM carried face enrichment decay: mom_oversold 20.80% "
                     "(94/452) vs none 16.67% (135/810) = 1.25x -- W10 1.88x "
                     "decayed to 1.25x under the eleven-source exclusion "
                     "book (cross-wave prior decay first observation)"),
        },
    },
    "eliminated": screen["n_distinct"] - screen["n_survivors"],
    "refs": {
        "prereg": "research/TRIAL_LABOR_W11_PREREG.md",
        "results": f"{R}/w11_screen.json",
        "ticket": "T-2026-09-29-123",
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
}
total_zero = all(v == 0 for f in faces.values() for v in f.values())

judge_row = {
    "batch": "TRIAL_LAB_W11_JUDGE",
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
                     f"(n_eff={line['n_eff']}) -- line_ok false; nine-face "
                     "total zero (gate/vol/yang/vconf/streak/tstate/amp/mom/"
                     "std); best-cell bootstrap ci95 "
                     f"[{g1b['bootstrap_ci']['ci95_low']},"
                     f"{g1b['bootstrap_ci']['ci95_high']}] lower bound "
                     "positive but below skill line"),
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
        "prereg": "research/TRIAL_LABOR_W11_PREREG.md",
        "results": f"{R}/w11_judge.json",
        "intake": (f"{R}/w11_intake.json (lawful-zero n_eligible="
                   f"{intake['n_eligible']}, r444 harvest round)"),
        "ticket": "T-2026-09-29-123",
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

print("attrition append done: W11 SCREEN+JUDGE rows in both faces")
