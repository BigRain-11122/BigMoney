import json

# r413 bm-b: T-117 progress note append (progress_rN_bmb convention)
P = "fleet/tasks/T-2026-09-29-117-P1.json"
with open(P, encoding="utf-8") as fh:
    d = json.load(fh)
assert d["status"] == "claimed" and "bm-c" in d["claimed_by"]
note = (
    "r413 bm-b: W6-SCREEN chain closed. Burn pid3984 complete 06:40:05 "
    "(4152/4152 cells, worker log 'shard 0of1 complete', normal exit -- "
    "screen-finalize = separate subcommand by design, no crash); "
    "screen-finalize executed in-round by lane owner bm-b (W5 bm-a r409 "
    "precedent): 3952 distinct + 200 nulls, null p95 0.5196 (json 6dp "
    "0.519553), survivors 293, ledger 328987+4152=333139 cross-wave linear "
    "(grammar 2d395f5f8e7d16cb anchor, evidence_cutoff 2026-09-22); "
    "judge-prep PASS (manifest 48 members, census L/D frozen, survivors "
    "293); W6-JUDGE pool entry submitted canonical (consumer_plan "
    "O-1820(3) + contract trio + inbox guard; lane_owner=null per prereg "
    "sec.9; deps MET: serial-position pool drained 109/109 + judge-prep "
    "PASS + RAM r354 3-sample 10.38/10.58/12.71GB@31s); V3-TOURNAMENT "
    "verdict done-flip same round (crash-fuse loop cleared). 48h CEO "
    "report clock starts at W6 judge-finalize (future round)."
)
assert "progress_r413_bm_b" not in d
d["progress_r413_bm_b"] = note
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
with open(P, encoding="utf-8") as fh:
    d2 = json.load(fh)
assert d2["progress_r413_bm_b"] == note
print("T-117 progress_r413_bm_b appended + reload-verified")
