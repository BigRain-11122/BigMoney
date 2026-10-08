"""W16 SCREEN+JUDGE attrition-row retro-fill (bm-a r873 closure round).

Debt: r860 screen-finalize (03:41) and r862 judge-finalize (04:48) landed
the products + trials_ledger blocks but the attrition history rows were
never appended (W16 runner carries no attrition writer leg -- the r722
dead-session adoption lost it along with the reform face; W1/W13
retro-fill precedent r417/r471 same debt class). Data verbatim from
results/trial_labor_w16/w16_screen.json + w16_judge.json; rows appended
chronologically at tail (newest batches); shared + bm-a lane double
write (r417 lane precedent).
"""
import io
import json

PATHS = [r"results\gate_attrition.json", r"results\gate_attrition.bm-a.json"]
SCREEN = r"results\trial_labor_w16\w16_screen.json"
JUDGE = r"results\trial_labor_w16\w16_judge.json"

screen_row = {
    "batch": "TRIAL_LAB_W16_SCREEN",
    "ts": "2026-10-08 03:41:47",
    "kind": "measurement",
    "retro_fill": True,
    "cells_ledger_delta": 373,
    "ledger_total_after": 802278,
    "gates": {
        "screen_pass": {
            "n_candidates": 173,
            "n_survivors": 40,
            "line": "beat6m_rate > null_p95 (prereg sec.3, frozen; null_p95=0.511572)"
        },
        "null_face": {
            "p50": 0.5116,
            "p95": 0.511572,
            "n": 200,
            "seed": 20593500,
            "note": "K=200 TWENTY-tuple axis nulls (max/rank legs included), seed 20593500; p50 0.5116 / p95 0.511572 within prereg sec.5.2 band [0.50,0.52] (ninth consecutive in-band wave); screen survival line = program-frozen null p95 (W2-W15 identical law)"
        },
        "max_face": {
            "segmented_survival": {
                "max30_q10": {"n_cells": 62, "n_survivors": 15, "survival_rate": 0.241935},
                "none": {"n_cells": 111, "n_survivors": 25, "survival_rate": 0.225225}
            },
            "note": "MAX30_q10 value-cell 0.241935 vs none base 0.225225 = 1.07x -- WITHIN prereg sec.5.1 [0.8x,1.6x] band (low end); collapse 173/10,000=1.73% distinct BELOW sec.5.1 [2%,12%] band = supply-weakening alert honestly reported (W14 2.93% -> further collapse on the twenty-tuple face)"
        },
        "rank_face": {
            "segmented_survival": {
                "rank30_q90": {"n_cells": 70, "n_survivors": 14, "survival_rate": 0.2},
                "none": {"n_cells": 103, "n_survivors": 26, "survival_rate": 0.252427}
            },
            "note": "RANK30_q90 value-cell 0.79x vs none base -- at/below the max30 band lower edge (thin-tail axis, 217 probe open-days; sample-sufficiency constraint predicted in sec.5.1, readout confirms)"
        }
    },
    "refs": {
        "screen": "results/trial_labor_w16/w16_screen.json",
        "prereg": "research/TRIAL_LABOR_W16_PREREG.md",
        "grammar_ledger": "research/TRIAL_GRAMMAR_LEDGER.md"
    },
    "note": "retro-fill by bm-a r873 closure round (r860 finalize window landed product without attrition row -- W16 runner carries no attrition writer leg, r722 dead-session adoption lineage gap); data verbatim from w16_screen.json (trials_ledger prev 801905 + batch 373 = 802278, linear to W16-JUDGE +40 = 802318)"
}

judge_row = {
    "batch": "TRIAL_LAB_W16_JUDGE",
    "ts": "2026-10-08 04:48:23",
    "kind": "judgment",
    "retro_fill": True,
    "cells_ledger_delta": 40,
    "ledger_total_after": 802318,
    "gates": {
        "g1_prime_v2": {"n": 40, "n_pass": 0, "line": 1.1437,
                        "best": {"candidate_id": "W16-B-8195", "sharpe": 0.7272}},
        "dsr": {"n": 40, "max_dsr": 0.017772, "n_trials": 802278},
        "family_pbo": {"patterns": 0.3, "momentum": 0.9571, "folk": 0.2571,
                       "n_a_below_8": "trend1/sentiment2/ta6/macro+rest honest n/a"},
        "g2_registration_v2": {"n_eligible": 0},
        "reform_face": {"status": "PENDING_DERIVE",
                        "note": "prereg sec.4 reform caliber (eligible_reform + composite top-3) NOT in the landed runner (r722 adoption lost the W14 reform block); verdict landed on the old G1'/G2-v2 caliber = conservative face; reform-face derive slice = r873 continuation (§8 prereg), batch_p_values = dual-nulls signflip_p per reform canon sec.5 P1"}
    },
    "refs": {
        "judge": "results/trial_labor_w16/w16_judge.json",
        "intake": "results/trial_labor_w16/w16_intake.json",
        "prereg": "research/TRIAL_LABOR_W16_PREREG.md"
    },
    "note": "retro-fill by bm-a r873 closure round (r862 finalize+intake landed without attrition row); 40/40 judged verdict=fail; intake lawful-zero n_eligible=0 (prereg sec.5.3 pred.3 modal zero); 48h CEO report clock started at judge-finalize 04:48 (due 2026-10-10 04:48)"
}


def main():
    s16 = json.load(io.open(SCREEN, encoding="utf-8"))
    tl = s16["trials_ledger"]
    assert tl["total"] == 802278 and tl["batch_trials"] == 373, "screen ledger drift"
    assert s16["n_survivors"] == 40 and s16["n_distinct"] == 173, "screen face drift"
    nf = s16["null_family"]
    assert nf["p95_line"] == 0.511572 and nf["median"] == 0.5116, "null face drift"
    assert s16["max_segmented_survival"]["max30_q10"]["survival_rate"] == 0.241935
    assert s16["rank_segmented_survival"]["rank30_q90"]["survival_rate"] == 0.2
    j16 = json.load(io.open(JUDGE, encoding="utf-8"))
    jt = j16["trials_ledger"]
    assert jt["total"] == 802318 and jt["batch_trials"] == 40, "judge ledger drift"
    assert j16["n_judged_cells"] == 40 and j16["n_eligible_g2"] == 0

    for PATH in PATHS:
        raw = io.open(PATH, encoding="utf-8").read()
        att = json.loads(raw)
        batches = [h.get("batch") for h in att["history"]]
        assert "TRIAL_LAB_W16_SCREEN" not in batches, "screen row already present"
        assert "TRIAL_LAB_W16_JUDGE" not in batches, "judge row already present"
        assert att["history"][-1]["batch"] == "THEME_DEEPEN_P1", "tail anchor drift"
        att["history"].append(screen_row)
        att["history"].append(judge_row)
        trailing_nl = raw.endswith("\n")
        with io.open(PATH, "w", encoding="utf-8", newline="") as f:
            json.dump(att, f, indent=1)
            if trailing_nl:
                f.write("\n")
        # post-write gates
        att2 = json.loads(io.open(PATH, encoding="utf-8").read())
        b2 = [h.get("batch") for h in att2["history"]]
        assert b2.count("TRIAL_LAB_W16_SCREEN") == 1 and b2.count("TRIAL_LAB_W16_JUDGE") == 1
        i_sc, i_jd = b2.index("TRIAL_LAB_W16_SCREEN"), b2.index("TRIAL_LAB_W16_JUDGE")
        sc, jd = att2["history"][i_sc], att2["history"][i_jd]
        assert sc["ledger_total_after"] + jd["cells_ledger_delta"] == jd["ledger_total_after"], \
            "chain linearity broken"
        print("appended:", PATH, "| history len:", len(b2), "| chain",
              sc["ledger_total_after"], "+", jd["cells_ledger_delta"], "=",
              jd["ledger_total_after"])
    print("BOTH FACES OK")


if __name__ == "__main__":
    main()
