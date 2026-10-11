"""r872 bm-b: append T-101-V4-A14-PREDFACE judgment row to gate_attrition.bm-b.json
(mirrors A13 r446 bm-a row schema; values pulled from results JSON zero hand-copy)."""
import json, time

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RES = ROOT + r"\results\t101_v4_a14_predface.json"
LED = ROOT + r"\results\gate_attrition.bm-b.json"

d = json.load(open(RES, encoding="utf-8"))
cells = {"%s|%s|%s" % (c["face"], c["member"], c["feature"]): c for c in d["cells"]}
pass_cells = d["fv_pass_cells"]
notes = d["reading_layer"]["supply_note_flags"]

def face(k):
    return cells[k]

ic_oos, z_oos, p_oos, ci_lines = {}, {}, {}, []
for k in pass_cells + notes:
    c = face(k)
    m = k.split("|")[1]
    ic_oos[k] = round(c["ic"]["oos"], 4)
    z_oos[k] = round(c["shift_null"]["oos"]["z"], 2)
    p_oos[k] = round(c["shift_null"]["oos"]["p_two"], 4)
for k in pass_cells:
    c = face(k)
    ci_lines.append("%s [%.3f,%.3f]" % (k, c["boot_ci"]["oos"]["lo"], c["boot_ci"]["oos"]["hi"]))

row = {
    "batch": "T-101-V4-A14-PREDFACE",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "host": "bm-b",
    "kind": "judgment",
    "n_cells": 30,
    "verdict": "FV_PASS_2of9_REPLICATION_HELD_EXTENSION_NEGATIVE",
    "line_action": "f_c2v4 (22-gate) + f_mp1 (MP1-5) predictor extension faces judged negative (7/9 FV cells fail); f_c2 anchor replication 2/2 held exact; MP1 predictor usage face tested-negative closed (was never-tested per DIGEST-w21 Q2); f_c2 named-supply to A1/C1 composite input roster continues (composite arm itself gated behind BAN-05 + sentiment-family double-negative)",
    "legs": {
        "fv_pass_cells": pass_cells,
        "supply_notes_oos_only": notes,
        "ic_oos": ic_oos,
        "shift_z_oos": z_oos,
        "p_oos": p_oos,
        "boot_ci_oos_excludes_zero": ci_lines,
        "family_coherence": "both FV hits = f_c2 (17-gate mean) replicating A13 cutoff-09-29 anchors to 4dp (+8td stride-20 no new OOS rebal points); new faces f_c2v4/f_mp1 same-sign positive OOS on 510050/510500 but z<2 + CI includes zero = FV fail; f_c2 raw|510300 near-zero negative",
        "e_fp_nominal": 0.45,
        "mechanism": "MP1 5-gate increment dilutes the 17-gate oversold-mean signal (f_c2v4 downshift) and MP1 gates alone carry weaker continuous information; second replication of gate-family info-exists-conversion-dies separation on the continuous face",
        "downstream": "f_c2 FV-pass pair fixed as named input feature for A1/C1 dual-thermometer composite arm (bm-b lane, roster supply face); re-open of f_c2v4/f_mp1 needs new data source + exception three-question per family-closure law",
        "ledger_total_after": d["trials_ledger"]["total"],
        "cells_ledger_delta": d["trials_ledger"]["batch_trials"],
        "evidence_cutoff": d["evidence_cutoff"],
        "results_ref": "results/t101_v4_a14_predface.json",
        "prereg_backfill": "research/T-101-V4_A14_PREDFACE_PREREG.md s7/s8",
        "engineering_note": "r872 predecessor session died mid-round; runner dec line missing .reindex(master_dates) in master reindex block (A13 verbatim has it) - surgical heal, selftest 16/16 x2, RAW 5 checkpoint records preserved, zero reburn zero double-count",
    },
}

led = json.load(open(LED, encoding="utf-8"))
assert not any(e.get("batch") == row["batch"] for e in led["entries"]), "dup row"
led["entries"].append(row)
with open(LED, "w", encoding="utf-8") as fh:
    json.dump(led, fh, ensure_ascii=False, indent=1)
print("appended; entries=%d ledger_total=%s" % (len(led["entries"]), d["trials_ledger"]["total"]))
