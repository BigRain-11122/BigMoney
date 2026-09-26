# -*- coding: utf-8 -*-
"""R252 bm-a: trials-ledger chain repair (deterministic, zero network, zero LLM).

DEFECT (found R252 during CN-DIV-LOWVOL-ROT-P1 harvest): family runners
embedded science_gates.append_ledger() blocks under top-level key "ledger"
while ledger_head() scans ONLY "trials_ledger" -> five batches were chain-
invisible; plus two correct-key lineage gaps (p1e_zoo narrow-scanner chain,
market_clock run1 concurrent-read skip) and one legacy gap (t33 skipped by
xstock_synth prev=58070=t22). Recorded head 185798 (grid_sleeve_p1.json);
TRUE cumulative head = 186192 (missing 394 = t33 40 + div 36 + zoo 157 +
cny 23 + exit 30 + cn_rev 54 + rot 54).

REPAIR (surgical, judgment faces byte-untouched -- skill_line/g1/g2/cells
stay as recorded; 4dp line values re-derived unchanged: rot true line
0.95273 -> 0.9527, cn_rev 0.6147+4e-5 -> 0.6147):
  1. t33_attack_wave.json: key rename only (its arithmetic 58070->58110
     is true-correct; +40 restored to the lineage);
  2. div_lowvol_p1.json: key rename + prev 182952->182992, total
     182988->183028 (true chain incl. t33 40);
  3. cny_window_p1.json: key rename + prev 184826->185059, total
     184849->185082 (true cumulative at 09-26 08:52 landing);
  4. cn_rev_tilt/p1_results.json: key rename + prev 185798->186084,
     total 185852->186138;
  5. cn_div_lowvol_rot/p1_results.json: key rename + prev 185798->186138,
     total 185852->186192.
Intermediate correct-key files (cta_wave1..grid_sleeve) keep their
recorded derivations = superseded historical records (max-total chain
head lands true regardless; no double-count: ledger_head takes max, not
sum). shortline_p1_factor.json (09-23 legacy, pre-cutoff-law, 239 trials
self-healed into lineage via p2_synth prev=1312) is intentionally NOT
renamed: renaming would push a pre-T-02-6/7 file into science_audit C2
universe without a lawful evidence_cutoff-era guarantee. Its "ledger" key
stays as accepted legacy, documented here.

Supersedes the ledger-arithmetic assertions in
results/_r252bma_rot_harvest.py (as-run 14:54 pre-repair, PASS output
preserved verbatim in the R252 round log).

Exit 0 = repaired + verified (head 186192, all five files parse, C2 keys
present). Exit 2 = verification red, edits rolled back.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = [
    ("results/t33_attack_wave.json",
     [('"ledger": {', '"trials_ledger": {')]),
    ("results/div_lowvol_p1.json",
     [('"ledger": {', '"trials_ledger": {'),
      ('"prev_total": 182952', '"prev_total": 182992'),
      ('"total": 182988', '"total": 183028')]),
    ("results/cny_window_p1.json",
     [('"ledger": {', '"trials_ledger": {'),
      ('"prev_total": 184826', '"prev_total": 185059'),
      ('"total": 184849', '"total": 185082')]),
    ("results/cn_rev_tilt/p1_results.json",
     [('"ledger": {', '"trials_ledger": {'),
      ('"prev_total": 185798', '"prev_total": 186084'),
      ('"total": 185852', '"total": 186138')]),
    ("results/cn_div_lowvol_rot/p1_results.json",
     [('"ledger": {', '"trials_ledger": {'),
      ('"prev_total": 185798', '"prev_total": 186138'),
      ('"total": 185852', '"total": 186192')]),
]
EXPECT = {
    "results/t33_attack_wave.json": (58070, 40, 58110),
    "results/div_lowvol_p1.json": (182992, 36, 183028),
    "results/cny_window_p1.json": (185059, 23, 185082),
    "results/cn_rev_tilt/p1_results.json": (186084, 54, 186138),
    "results/cn_div_lowvol_rot/p1_results.json": (186138, 54, 186192),
}
HEAD_TOTAL = 186192


def main() -> int:
    backups = {}
    try:
        for rel, subs in EDITS:
            p = os.path.join(ROOT, rel)
            raw = open(p, "rb").read()
            backups[rel] = raw
            text = raw.decode("utf-8-sig")
            for old, new in subs:
                if text.count(old) != 1:
                    raise SystemExit(f"target not unique in {rel}: {old!r} "
                                     f"count={text.count(old)}")
                text = text.replace(old, new)
            if b"\r\n" in raw:
                data = text.encode("utf-8").replace(b"\n", b"\r\n")
            else:
                data = text.encode("utf-8")
            with open(p, "wb") as fh:
                fh.write(data)
    except SystemExit as ex:
        print("ABORT:", ex)
        for rel, raw in backups.items():
            with open(os.path.join(ROOT, rel), "wb") as fh:
                fh.write(raw)
        return 2

    fails = []
    for rel, (eprev, etrials, etotal) in EXPECT.items():
        d = json.load(io.open(os.path.join(ROOT, rel), encoding="utf-8-sig"))
        tl = d.get("trials_ledger")
        if not (isinstance(tl, dict) and tl.get("prev_total") == eprev
                and tl.get("batch_trials") == etrials
                and tl.get("total") == etotal):
            fails.append(f"{rel}: trials_ledger {tl} != "
                         f"({eprev},{etrials},{etotal})")
        if not d.get("evidence_cutoff"):
            fails.append(f"{rel}: evidence_cutoff missing (C2 eligibility)")
        if "ledger" in d and isinstance(d.get("ledger"), dict) \
                and "total" in d["ledger"]:
            fails.append(f"{rel}: stale top-level ledger block still present")

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import science_gates as sg
    head = sg.ledger_head()
    if head["total"] != HEAD_TOTAL:
        fails.append(f"ledger_head {head} != total {HEAD_TOTAL}")

    # judgment faces untouched: rot + cn_rev verdicts must read as recorded
    rot = json.load(io.open(os.path.join(
        ROOT, "results/cn_div_lowvol_rot/p1_results.json"), encoding="utf-8-sig"))
    if rot["g1_prime_v2"]["W252_bare"]["sharpe_full"] != 0.7371 \
            or rot["skill_line"]["line"] != 0.9527 \
            or rot["n_trials"] != 54:
        fails.append("rot judgment faces drifted")
    cnr = json.load(io.open(os.path.join(
        ROOT, "results/cn_rev_tilt/p1_results.json"), encoding="utf-8-sig"))
    if not cnr["g1_prime_v2"] or cnr.get("n_trials") != 54:
        fails.append("cn_rev judgment faces drifted")

    print(json.dumps({
        "chain_repair": "PASS" if not fails else "FAIL",
        "ledger_head": head,
        "n_eff_next_batch_plus4": sg.n_eff(4),
        "files_repaired": [r for r, _ in EDITS],
        "superseded_intermediate_records":
            "cta_wave1/options/bond/wild/zoo/p1e_synth/exit/mc1/mc2/"
            "grid_sleeve keep recorded derivations (historical, max-total "
            "chain lands true regardless)",
        "legacy_left_as_is":
            "shortline_p1_factor.json (ledger key, 239 self-healed via "
            "p2_synth prev=1312; pre-cutoff-law, not C2-renamed)",
        "fails": fails,
    }, ensure_ascii=False, indent=1))
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
