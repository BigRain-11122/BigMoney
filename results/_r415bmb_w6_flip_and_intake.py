"""r415 bm-b: TRIAL-LABOR-W6-JUDGE entry done-flip (dual-face) + intake zero-face.
Successor-session harvest: predecessor r415 session (died ~08:04 stream-timeout)
detached judge-finalize at 07:56:41; finalize survived the session and landed
08:14:22 -> results/trial_labor_w6/w6_judge.json. Pit-89 law: finalize landing
round MUST flip entry face same-round (shard done since r414).
Dual-face = runnable_pool.json + runnable_pool.bm-b.json (r407 W5 precedent).
Supersedes predecessor's _r415bmb_judge_entry_flip.py (single-face + ledger-file
assert compared basename vs full-path constant -> would fail; kept on disk as record).
Fail-closed receipt verification before any pool write; idempotent re-run safe.
"""
import json
import time

POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"
JUDGE = "results/trial_labor_w6/w6_judge.json"
INTAKE = "results/trial_labor_w6/w6_intake.json"
LANDED = "2026-09-29T08:14:22+08:00"
DEADLINE_48H = "2026-10-01 08:14"  # CEO report clock started at finalize landing

# ---- fail-closed receipt verification ----
with open(JUDGE, encoding="utf-8") as fh:
    j = json.load(fh)
assert j["n_judged_cells"] == 293, f"judged {j['n_judged_cells']} != 293 survivors"
assert j["n_eligible_g2"] == 0, "G2 eligible nonzero -- intake not zero-face, halt"
led = j["trials_ledger"]
assert led["prev_total"] == 333139, f"ledger prev {led['prev_total']} != 333139"
assert led["batch_trials"] == 293, "ledger batch != judged 293"
assert led["total"] == 333432, "ledger total mismatch (333139+293=333432)"
assert led["file"].endswith("w6_judge.json"), "ledger face mismatch: " + str(led["file"])
assert j["evidence_cutoff"] == "2026-09-22", "evidence_cutoff drifted"
assert j["grammar_sha256"] == "2d395f5f8e7d16cb", "grammar sha drifted"
def _g1(v):  # face value is {"n_cells":N,"n_g1_pass":X,"n_eligible_g2":Y}
    return v["n_g1_pass"] if isinstance(v, dict) else v
for face in ("gate_face_judgment", "vol_face_judgment", "yang_face_judgment", "vconf_face_judgment"):
    assert sum(_g1(v) for v in j[face].values()) == 0, f"{face} has G1 passes -- not total-zero, halt"
e_fp = j["n_wave_disclosure"]["E_FP_nominal_5pct"]
fam = {k: v["pbo"] for k, v in j["family_pbo"].items()}
print(f"receipt verified: 293 judged, ALL-face G1 zero (gate/vol/yang/vconf), "
      f"E[FP]={e_fp}, G2 eligible 0, ledger 333139+293={led['total']} linear")

DONE_NOTE = (
    "r415 bm-b successor harvest: judge-finalize detached by predecessor session "
    "07:56:41 (predecessor died ~08:04 stream-timeout; process pid2432 survived and "
    "landed 08:14:22) -> w6_judge.json: 293 judged cells (== w6_screen survivors 293), "
    "TOTAL-ZERO G1 across all four faces (gate none/bear/bull 0; vol none/calm/wild 0; "
    "yang none/first_yang 0; vconf none/volume_dry/volume_surge 0) -> G2 eligible 0 -> "
    "[] (even W5's single gate=none|vol=none|yang=none G1 pass absent this wave); "
    f"E[FP]={e_fp} at nominal 5% caliber (DSR>=0.95 gate IS the correction); family PBO "
    f"11 modules (patterns {fam['patterns']:.4f}/82c, seasonal {fam['seasonal']:.4f}/13c, "
    f"sentiment {fam['sentiment']:.4f}/29c, momentum {fam['momentum']:.4f}/25c lowest "
    f"quantified, event {fam['event']:.4f}/8c; trend 6c + macro 7c insufficient <8 "
    "disclosed); trials_ledger TRIAL_LAB_W6_JUDGE prev 333139 + 293 = 333432 "
    "cross-wave linear no-reset verified; evidence_cutoff 2026-09-22 lockbox; "
    "grammar 2d395f5f8e7d16cb (== r410 build anchor, append-only face); wave-6 funnel "
    "honest zero-registration. Intake zero-face landed same round: "
    "results/trial_labor_w6/w6_intake.json (prereg sec.6 s4 actual-count clause; zero "
    "eligible = D6/library/paper-desk all zero-surface). 48h CEO report clock started "
    f"at finalize landing {LANDED} (standing deadline {DEADLINE_48H})."
)

for path in (POOL, LANE):
    with open(path, encoding="utf-8") as fh:
        pool = json.load(fh)
    ent = next(e for e in pool["entries"] if e["id"] == "TRIAL-LABOR-W6-JUDGE")
    if ent["status"] == "done":
        print(f"{path}: entry already done -- idempotent no-op")
        continue
    assert ent["status"] == "ready", f"{path}: entry status {ent['status']} != ready"
    assert ent["shards"][0]["status"] == "done", f"{path}: shard not done (inconsistent)"
    ent["status"] = "done"
    ent["done_at"] = LANDED
    ent["result_ref"] = "results/trial_labor_w6/w6_judge.json"
    ent["done_note"] = DONE_NOTE
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(path, encoding="utf-8") as fh:  # round-trip reload assert
        p2 = json.load(fh)
    e2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W6-JUDGE")
    assert e2["status"] == "done" and e2["shards"][0]["status"] == "done"
    assert e2["done_at"] == LANDED and e2["result_ref"].endswith("w6_judge.json")
    print(f"{path}: W6-JUDGE entry ready->done OK (reload verified)")

# ---- intake zero-face (W5 r407 precedent shape, vconf face added) ----
intake = {
    "wave": "TRIAL_LABOR_W6",
    "stage": "intake",
    "prereg": "research/TRIAL_LABOR_W6_PREREG.md",
    "evidence_cutoff": "2026-09-22",
    "grammar_sha256": "2d395f5f8e7d16cb",
    "n_eligible": 0,
    "admitted": [],
    "rejected": [],
    "d6_binding": {},
    "intake": [],
    "note": ("zero G2-eligible survivors = lawful outcome, reported as-is (prereg sec.6 "
             "s4 actual-count clause; ALL-face G1 total-zero: gate-face none 0/bear 0/"
             "bull 0, vol-face none 0/calm 0/wild 0, yang-face none 0/first_yang 0, "
             "vconf-face none 0/volume_dry 0/volume_surge 0 -> 0/293 cells reached G1 "
             "at all, G2 trivially empty)"),
    "audit": {
        "n_engine_runs": 0,
        "ledger_trials_added": 0,
        "note": ("intake = judgment face, zero ledger rows; zero eligible -> D6 binding / "
                 "STRATEGY_LIBRARY registration / TRIAL-* paper-desk onboarding / smoke "
                 "anchor re-run all zero-surface per prereg sec.6 s4 (dead path this "
                 "wave); W6 runner has no intake subcommand (judge-finalize is the last "
                 "burn stage) -- zero survivors made the registration path dead code; "
                 "W2 runner cmd_intake (scripts/trial_labor_w2.py) is the reusable "
                 "precedent for any wave with survivors; 48h CEO report clock started "
                 f"at judge-finalize landing {LANDED} (standing deadline {DEADLINE_48H})"),
        "judge_receipt": ("results/trial_labor_w6/w6_judge.json (293 judged, E[FP]=14.65, "
                          "n_eligible_g2=0, family PBO 11 modules incl. patterns 0.7429/82c, "
                          "seasonal 0.8286/13c, sentiment 0.6714/29c; trend 6c + macro 7c "
                          "insufficient (<8) disclosed)"),
    },
    "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
}
with open(INTAKE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(intake, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
with open(INTAKE, encoding="utf-8") as fh:
    itk = json.load(fh)
assert itk["n_eligible"] == 0 and itk["wave"] == "TRIAL_LABOR_W6"
print("intake zero-face landed:", INTAKE)
print("W6-JUDGE full closure complete: dual-face flip + intake + 48h clock armed")
