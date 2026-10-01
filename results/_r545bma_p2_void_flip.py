# -*- coding: utf-8 -*-
"""r545 bm-a: T-142 ruling execution -- LOWAMP-P2 verdict flip to void-with-face-note
(O-20261001-2355 sec.1, GM P1 ruling). Pattern = T-140 action-2 (LOWAMP-P1 precedent,
commit c3c825c2a). Surgical: preserve original JSON byte-format (indent + EOL) per
r289/r509 law (probe first, assert after).

Faces:
1. results/lowamp_p2/lowamp_p2_results.json: verdict -> void-with-face-note + verdict_ruling block
2. results/lowamp_p2/lowamp_p2_void_compensation.json: new governance compensating entry
   (trials_ledger -2008 netting + ledger_voids active entry consumed by science_gates.active_voids)
3. post-write verification: ledger_head() derive == raw_head - 2008,
   active_voids contains LOWAMP-P2, json.loads green.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RES = "results/lowamp_p2/lowamp_p2_results.json"
COMP = "results/lowamp_p2/lowamp_p2_void_compensation.json"

# --- format probe (r289/r509 law): indent + EOL of the original product file
raw = open(RES, "rb").read()
crlf = raw.count(b"\r\n")
lf = raw.count(b"\n") - crlf
text = raw.decode("utf-8")
indent_probe = None
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith('"'):
        indent_probe = len(line) - len(line.lstrip())
        break
eol = "\r\n" if crlf > lf else "\n"
print(f"probe: indent={indent_probe} eol={'CRLF' if eol == chr(13) + chr(10) else 'LF'} crlf={crlf} lf={lf}")

r = json.loads(text)
assert r["verdict"] == "judged-negative", f"unexpected verdict: {r['verdict']}"

import scripts.science_gates as sg

head = sg.ledger_head()
raw_head_before = head["total"]
print("raw head before:", raw_head_before, "(", head["file"], ")")

# --- face 1: verdict flip + verdict_ruling block (verbatim pattern from P1)
r["verdict"] = "void-with-face-note"
r["verdict_ruling"] = {
    "ruling": "O-20261001-2355 sec.1 (T-142 GM P1 ruling, CEO direct order)",
    "ticket": "T-2026-10-01-142",
    "audit": "results/lowamp_p2/e1_three_leg.json (E1 four-leg, pre-consumption catch per r492 law)",
    "face_note": (
        "judged-negative stays recorded as the partially-neutralized hybrid measurement: the two "
        "non-bridged engine exit keys (loss_time_days/global_hard_limit) were written to the params "
        "channel = dead letters (backtester.py ExitConfig bridge reads only 6 kwargs), so the engine "
        "default stack (8d/25d) ejected 174/181 = 96% churn (108 loss_time_stop + 66 global_hard_limit, "
        "7 signal exits). The declared sec.0.6 HOLD-THROUGH face measures POSITIVE: engine+ExitPatch "
        "+15.88%/sharpe +1.158 (7 signal exits) ~ independent arithmetic leg +15.95%/+1.163 "
        "(T-136 Legs B/C precedent). Second same-family defect (P1 r301 root cause: fixture ExitPatch "
        "dual-key patch lost in copy-adapt). E1 exit-census caught it BEFORE consumption -- verdict face "
        "zero-loss, ledger compensating rollback -2,008 lands in lowamp_p2_void_compensation.json. "
        "The family re-opens supply via LOWAMP-P3 (ExitPatch channel for the two non-bridged keys + "
        "post-burn exit-reason census per O-20261001-2355 sec.1 law-A upgrade)."
    ),
}

out = json.dumps(r, ensure_ascii=False, indent=indent_probe) + eol
open(RES, "w", encoding="utf-8", newline="").write(out)
print("face 1 done: verdict flipped + verdict_ruling written")

# --- face 2: void compensation entry (append-only governance record)
comp = {
    "batch": "LOWAMP-P2-VOID-COMPENSATION",
    "kind": "governance-void-compensating-entry",
    "evidence_cutoff": "2026-09-22",
    "ruling": {
        "order": "O-20261001-2355",
        "section": "sec.1 (T-142 GM P1 ruling, CEO direct order)",
        "ticket": "T-2026-10-01-142",
        "audit": "results/lowamp_p2/e1_three_leg.json (E1 four-leg; pre-consumption catch, verdict face zero-loss)",
        "ruled_at": "2026-10-01 23:55",
        "executed_by": "bm-a",
        "executed_at": "2026-10-02 00:1x",
    },
    "trials_ledger": {
        "prev_total": raw_head_before,
        "batch_trials": -2008,
        "total": raw_head_before - 2008,
        "batch": "LOWAMP-P2-VOID-COMPENSATION",
        "file": "results/lowamp_p2/lowamp_p2_results.json",
        "note": (
            "LOWAMP-P2 verdict VOID compensating rollback (-2,008) per O-20261001-2355 sec.1; "
            "ruling-time chain head was 386,267 (P2 finalize r521); perpetual waves W3..W33 chained on top "
            "between finalize and this execution, so the -2,008 nets at the execution-time raw head "
            f"{raw_head_before} -> {raw_head_before - 2008} (cumulative as-if LOWAMP-P2 never burned, all else "
            "equal). Append-only discipline: the LOWAMP-P2 product's own trials_ledger block stays verbatim; "
            "the active void below makes every raw/downstream cumulative net of the 2,008 exactly once "
            "(ledger_head void face, science_gates T-140/T-142)."
        ),
        "evidence_cutoff": "2026-09-22",
        "voids_applied": ["LOWAMP-P1", "LOWAMP-P2"],
    },
    "ledger_voids": [
        {
            "batch": "LOWAMP-P2",
            "file": "results/lowamp_p2/lowamp_p2_results.json",
            "voided_trials": 2008,
            "active": True,
            "reason": (
                "verdict VOID-with-face-note: exit-neutralization dead-letter (loss_time_days/"
                "global_hard_limit written to params channel; engine ExitConfig bridge reads only "
                "6 kwargs) -> default stack 8d/25d ejected 174/181 = 96% churn (108 loss_time_stop "
                "+ 66 global_hard_limit, 7 signal exits); measured a partially-neutralized hybrid face, "
                "NOT the declared HOLD-THROUGH face (+15.88%/sharpe +1.158 ExitPatch-corrected ~ "
                "+15.95%/+1.163 independent arithmetic); second same-family defect (T-136/P1 r301 "
                "root cause = fixture ExitPatch dual-key patch lost in copy-adapt); E1 exit-census "
                "caught before consumption (exit-axis explicit gate O-20261001-1108 first application), "
                "ledger verdict face zero-loss, trials compensated here."
            ),
            "ruling": "O-20261001-2355",
            "ticket": "T-2026-10-01-142",
            "audit": "results/lowamp_p2/e1_three_leg.json",
        }
    ],
}
open(COMP, "w", encoding="utf-8", newline="").write(
    json.dumps(comp, ensure_ascii=False, indent=1) + "\n"
)
print("face 2 done: compensation entry written, total:", comp["trials_ledger"]["total"])

# --- verification: derive with active voids
head2 = sg.ledger_head()
print("post-flip ledger_head:", head2["total"], "voided:", [(v["batch"], v.get("voided_trials")) for v in head2.get("voided", [])])
assert head2["total"] == raw_head_before - 2008, "ledger head mismatch"
voids = sg.active_voids()
assert ("LOWAMP-P2", 2008) in [(v["batch"], v.get("voided_trials")) for v in voids]
rr = json.load(open(RES, encoding="utf-8"))
assert rr["verdict"] == "void-with-face-note"
print("VERIFICATION PASS: verdict=void-with-face-note, ledger head", head2["total"], ", active voids LOWAMP-P1+P2 both netted once")
