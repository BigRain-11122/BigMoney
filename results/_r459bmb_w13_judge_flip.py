# r459 bm-b: TRIAL-LABOR-W13-JUDGE flip waiting->ready (W12-JUDGE r446 lineage precedent)
# Gates receipted this round on bm-b:
#  (1) serial-position re-confirm: W2-W12-JUDGE + MASS-W1-JUDGE all done; SLOT-10 entered
#      11:30:31 AFTER W13-JUDGE entry 11:2x = not ahead; no newly-entered verdict face ahead.
#  (2) judge-prep real-data first fire on deep-panel bm-b: PASS exit 0 (manifest 48 members
#      verdict PASS, census L/D == frozen {6m 1253/3104, 12m 1127/2978, 24m 875/2726},
#      grammar sha16 868cd0c6413636e6 == FROZEN pin, survivors 99, eleven-gate meta faithful
#      incl sumn face; r446 three-command real-data closure complete: screen-prep bm-a +
#      screen-finalize bm-a + judge-prep bm-b all green on real data).
#  (3) RAM three-sample r354: 6.59 / 6.57 / 6.76 GB free across 32s, all >= 4GB.
import json, io, datetime

POOL = "results/runnable_pool.json"

with io.open(POOL, encoding="utf-8") as f:
    pool = json.load(f)

target = None
for e in pool["entries"]:
    if e.get("id") == "TRIAL-LABOR-W13-JUDGE":
        target = e
        break
assert target is not None, "entry not found"
assert target["status"] == "waiting", "unexpected status: %s" % target["status"]

now = "2026-09-30T11:5x"
target["status"] = "ready"
target["entered_at"] = target.get("entered_at")  # unchanged, provenance preserved
target["data_gates"] = (
    "GATES ALL GREEN (direct-ready r459 bm-b, W12-JUDGE r446 lineage): "
    "(1) serial-position re-confirm at flip time -- W2/W3/W4/W5/W6/W7/W8/W9/W10/W11/W12-JUDGE + "
    "MASS-TRIAL-W1-JUDGE all done; INNOVATION-QUOTA-SLOT-10 (bm-c berth) entered 11:30:31 AFTER this "
    "entry 11:2x = not ahead, no re-queue; (2) judge-prep real-data first fire on deep-panel bm-b "
    "r459 exit 0 PASS: judge_state.json g_manifest verdict PASS 48 members, census L/D == frozen "
    "{6m 1253/3104, 12m 1127/2978, 24m 875/2726}, grammar sha16 868cd0c6413636e6 == FROZEN pin, "
    "survivors 99, eleven-gate meta faithful incl sumn (150open/1361closed decidable 1511 sumn10-open 144) "
    "-- r446 three-command real-data closure complete (screen-prep bm-a r467 + screen-finalize bm-a r467 + "
    "judge-prep bm-b r459); (3) RAM r354 three-sample 6.59/6.57/6.76 GB free across 32s all >=4GB "
    "(in-runner gate authoritative). Burn via autofill pool face; judge-finalize = lane-owner separate "
    "round work per W5-W12 precedent; 48h CEO report clock starts at judge-finalize."
)
for sh in target.get("shards", []):
    if sh.get("key") == "judge-0of1":
        sh["status"] = "ready"

pool["updated_at"] = "2026-09-30 11:5x"

with io.open(POOL, "w", encoding="utf-8", newline="\n") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")

# verify
with io.open(POOL, encoding="utf-8") as f:
    check = json.load(f)
for e in check["entries"]:
    if e["id"] == "TRIAL-LABOR-W13-JUDGE":
        print("FLIP VERIFIED:", e["status"], "| shard:", e["shards"][0]["status"])
