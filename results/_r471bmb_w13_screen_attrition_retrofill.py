"""W13 SCREEN attrition-row retro-fill (bm-b r471 W14 freeze-window, checklist-1).

Debt: W13 prereg sec.8 + CEO-REPORT-WAVE13 disclosed the TRIAL_LAB_W13_SCREEN
attrition row as bm-a-lane debt (cross-machine no-double-write at the time).
The W14 draft freeze checklist item (1) requires its backfill verified before
the freeze trigger is satisfied. Backfill mirrors the bm-b r459 JUDGE-row
retro-fill precedent: data verbatim from w13_screen.json, row inserted at its
chronological position in history (between W12-JUDGE and W13-JUDGE), keyset
grows monotonically (r448 guard face).
"""
import io
import json

PATH = r"results\gate_attrition.json"
SCREEN = r"results\trial_labor_w13\w13_screen.json"

row = {
    "batch": "TRIAL_LAB_W13_SCREEN",
    "ts": "2026-09-30 11:06:33",
    "kind": "measurement",
    "retro_fill": True,
    "cells_ledger_delta": 593,
    "ledger_total_after": 359980,
    "gates": {
        "screen_pass": {
            "n_candidates": 393,
            "n_survivors": 99,
            "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.511572, prereg sec.3 frozen)"
        },
        "null_face": {
            "p50": 0.5116,
            "p95": 0.511572,
            "n": 200,
            "seed": 20323500,
            "note": "K=200 sixteen-tuple axis nulls with mom+std+rsqr+sumn legs, seed 20323500; p50 0.5116 within prereg sec.5.2 band [0.50,0.52] (eighth consecutive wave >0.50 drift-lineage continuation); p95 0.511572 within thirteen-wave band; screen survival line = program-frozen null p95 (W2-W12 identical law)"
        },
        "sumn_face": {
            "segmented_survival": {
                "sumn20_lo": {"n_cells": 49, "n_survivors": 6, "survival_rate": 0.122449},
                "sumn10_lo": {"n_cells": 48, "n_survivors": 4, "survival_rate": 0.083333},
                "none": {"n_cells": 296, "n_survivors": 89, "survival_rate": 0.300676}
            },
            "note": "SUMN new face direction intel (W13 true question, adopted from bm-a r456 probe package): sumn20_lo 0.12245 = 0.41x vs none -- BELOW prereg sec.5.1 >=1.3x prediction (enrichment MISS); sumn10_lo 0.08333 = 0.28x STRONG anti-enrichment (two-window concordant toxic, strongest axis-face miss of the supply-line family); SUMN axis family fails supply-line promotion on screen evidence (family hit rate now 1/3)"
        }
    },
    "refs": {
        "screen": "results/trial_labor_w13/w13_screen.json",
        "prereg": "research/TRIAL_LABOR_W13_PREREG.md",
        "grammar_ledger": "research/TRIAL_GRAMMAR_LEDGER.md"
    },
    "note": "retro-fill by bm-b r471 W14 freeze-window (draft checklist-1 attrition SCREEN row backfill verification); original lane bm-a r467 autofill lineage (GENERATE/SCREEN); debt disclosed in W13 prereg sec.8 + CEO-REPORT-WAVE13 (cross-machine lane no-double-write at run time); data verbatim from w13_screen.json (trials_ledger prev 359387 + batch 593 = 359980, linear to W13-JUDGE +99 = 362083)"
}


def main():
    # sanity: the row must not already exist (idempotency guard)
    raw = io.open(PATH, encoding="utf-8").read()
    att = json.loads(raw)
    batches_h = [h.get("batch") for h in att["history"]]
    assert "TRIAL_LAB_W13_SCREEN" not in batches_h, "row already present"
    s13 = json.load(io.open(SCREEN, encoding="utf-8"))
    tl = s13["trials_ledger"]
    assert tl["total"] == 359980 and tl["batch_trials"] == 593, "screen ledger drift"
    assert s13["n_survivors"] == 99 and s13["n_distinct"] == 393, "screen face drift"
    nf = s13["null_family"]
    assert nf["p95_line"] == 0.511572 and nf["median"] == 0.5116, "null face drift"
    seg = s13["sumn_segmented_survival"]
    assert seg["sumn20_lo"]["survival_rate"] == 0.122449, "sumn seg drift"
    assert seg["sumn10_lo"]["survival_rate"] == 0.083333, "sumn seg drift"

    # chronological insertion: right before W13 JUDGE (ts 12:28:02)
    idx = next(i for i, h in enumerate(att["history"])
               if h.get("batch") == "TRIAL_LAB_W13_JUDGE")
    assert att["history"][idx]["ts"] == "2026-09-30 12:28:02"
    assert att["history"][idx - 1]["batch"] == "TRIAL_LAB_W12_JUDGE"
    att["history"].insert(idx, row)

    trailing_nl = raw.endswith("\n")
    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        json.dump(att, f, indent=1)
        if trailing_nl:
            f.write("\n")

    # post-write self-checks: monotone keyset + linearity of the trial-labor chain
    att2 = json.loads(io.open(PATH, encoding="utf-8").read())
    b2 = [h.get("batch") for h in att2["history"]]
    assert b2.count("TRIAL_LAB_W13_SCREEN") == 1
    i_sc = b2.index("TRIAL_LAB_W13_SCREEN")
    assert b2[i_sc + 1] == "TRIAL_LAB_W13_JUDGE"
    sc, jd = att2["history"][i_sc], att2["history"][i_sc + 1]
    assert sc["ledger_total_after"] + jd["cells_ledger_delta"] == jd["ledger_total_after"], \
        "chain linearity broken"
    print("retro-fill landed: history idx", i_sc, "| chain",
          sc["ledger_total_after"], "+", jd["cells_ledger_delta"],
          "=", jd["ledger_total_after"])
    print("history len:", len(b2))


if __name__ == "__main__":
    main()
