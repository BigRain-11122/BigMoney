"""r596 bm-b: register LOWAMP-DEEP-P1 runnable-pool entries (10 units:
8 cell-faces + NULLS + SENS). Mirror of the LOWAMP-P3 registration shape
(r495 face); prereg FROZEN this round research/LOWAMP-DEEP-P1.md,
banned_direction_gate ADMIT rc0, probe PASS 12.9s (G-CENSUS deep 1506,
D6 0.1719 admit, sizing-axis differentiates 3126/3126 days, headline
reproduces the P3 exploration artifact bit-for-bit 0.604283/1.066348/67)."""
import json

P = "results/runnable_pool.json"
pool = json.load(open(P, encoding="utf-8"))

TICKET_REF = ("T-2026-10-02-147 (O-20261002-2115 sec.1 line-2 deep-axis "
              "low-amplitude NEW FAMILY at main-exam rank, 67-trade face "
              "LAD-EDGE as main judgment; prereg FROZEN bm-b r596; "
              "banned_direction_gate ADMIT rc0; sizing-axis dead-letter "
              "fix carried by the runner, true-eq faces first-measured)")
PREREG_REF = ("research/LOWAMP-DEEP-P1.md FROZEN (judged cells 4 x faces 2 "
              "+ deep same-mask hold-through nulls 2000 rng([20337500,k]) "
              "+ sens 500 rng([20337000,k]); evidence_cutoff 2026-09-22 "
              "P-lineage D2 lockbox; exit-axis dual gate: hold-through "
              "params-4-keys + ExitPatch-2-keys + law-A census block 20%; "
              "deterministic reproduction assert vs P3 deep artifacts)")
CKPT = ("results/lowamp_deep_p1/ JSONL checkpoint resume (t22 pattern, "
        "done-key skip)")

cells = [("LAD-EDGE", "invvol"), ("LAD-EDGE-EQ", "eq"),
         ("LAD-REP", "invvol"), ("LAD-REP-EQ", "eq")]
faces = ("base", "x2")

new = []
for cell, _sz in cells:
    for face in faces:
        cid = "LOWAMP-DEEP-P1-CELL-" + cell.replace("-", "").upper() \
              + "-DEEP-" + face.upper()
        new.append({
            "id": cid,
            "ticket_ref": TICKET_REF,
            "prereg_ref": PREREG_REF,
            "runner": "scripts/lowamp_deep_p1.py",
            "runner_args": ["run", "--cell", cell, "--axis", "deep",
                            "--face", face],
            "shards": [{"key": cid.lower() + "-0of1", "status": "ready",
                        "checkpoint": CKPT}],
            "workers_plan": {"workers": 12, "priority": "BelowNormal"},
        })
new.append({
    "id": "LOWAMP-DEEP-P1-NULLS",
    "ticket_ref": TICKET_REF,
    "prereg_ref": PREREG_REF,
    "runner": "scripts/lowamp_deep_p1.py",
    "runner_args": ["run", "--nulls"],
    "shards": [{"key": "lowamp-deep-p1-nulls-0of1", "status": "ready",
                "checkpoint": CKPT,
                "note": ("K=2000 deep-universe same-mask hold-through "
                         "nulls (headline W=104 mask, eq weights), "
                         "rng([20337500,k]); first deep-universe null "
                         "pool fleetwide; feeds skill_line_v2 null_pool")}],
    "workers_plan": {"workers": 12, "priority": "BelowNormal"},
})
new.append({
    "id": "LOWAMP-DEEP-P1-SENS",
    "ticket_ref": TICKET_REF,
    "prereg_ref": PREREG_REF,
    "runner": "scripts/lowamp_deep_p1.py",
    "runner_args": ["run", "--sensitivity"],
    "shards": [{"key": "lowamp-deep-p1-sens-0of1", "status": "ready",
                "checkpoint": CKPT,
                "note": ("N=500 space-filling draws over W77-104/N{2,3}/"
                         "{invvol,eq} on the deep panel, rng([20337000,k]); "
                         "descriptive face only; exit-axis hold-through "
                         "same face per prereg sec.3")}],
    "workers_plan": {"workers": 12, "priority": "BelowNormal"},
})

existing = {e["id"] for e in pool["entries"]}
dup = [e["id"] for e in new if e["id"] in existing]
assert not dup, f"already pooled: {dup}"
pool["entries"].extend(new)
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
print(f"registered {len(new)} pool entries; total {len(pool['entries'])}")
for e in new:
    print(" +", e["id"])
