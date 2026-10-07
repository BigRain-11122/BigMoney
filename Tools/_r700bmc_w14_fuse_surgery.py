"""r700 bm-c W14-JUDGE fuse surgery (r389/r625 precedent family):
the 20:02 GM kill (O-20261008-1300 enforcement) registered as a crash
on the CURRENT healthy runner version -> autofill 20:10 tick refused
relaunch (fuse_refused_crash_loop). Root cause = external enforcement
kill + launch-path violation (FIXED on origin: autofill.py
CREATE_NO_WINDOW). Surgery clears the W14 judge sig in BOTH fuse faces
with the autofill code_changed-clear tombstone shape (r389/r504 lane-
union resurrection guard). Next autofill tick relaunches under the
hidden-console path; r699 park law still gates on RAM."""
import datetime
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = [os.path.join(ROOT, "results", "crash_fuse.json"),
         os.path.join(ROOT, "results", "crash_fuse.bm-c.json")]
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

runner = os.path.join(ROOT, "scripts", "trial_labor_w14.py")
with open(runner, "rb") as fh:
    runner_sha = hashlib.sha256(fh.read()).hexdigest()

receipt = {"ts": NOW, "law": "O-20261008-1300 knife-3 resume + r389/r625 "
            "fuse-surgery precedent", "runner_sha256": runner_sha,
            "reason": "external_kill_gm_o1300 (visible-console enforcement; "
            "tree was CPU-active burning per r700 20:00-20:05 probes); "
            "launch-path root FIXED on origin (autofill.py CREATE_NO_WINDOW, "
            "origin commit chain r700); burn resumes from fill_ladder "
            "checkpoint (zero N_eff loss, r250 one-shot law)",
            "faces": []}

for path in FACES:
    with open(path, encoding="utf-8") as fh:
        fuse = json.load(fh)
    hit = [s for s in fuse.get("sigs", {})
           if "trial_labor_w14" in s and "judge" in s]
    face_rec = {"face": os.path.basename(path), "sigs_found": hit,
                "cleared": []}
    for sig in hit:
        rec = fuse["sigs"][sig]
        fuse.setdefault("cleared", {})[sig] = {
            "cleared_ts": NOW, "cleared_by": "bm-c",
            "reason": "external_kill_gm_o1300_launch_path_fixed",
            "crashes": int(rec.get("count", 0)),
            "old_code_sha256": rec.get("code_sha256"),
        }
        del fuse["sigs"][sig]
        face_rec["cleared"].append(sig)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(fuse, fh, ensure_ascii=False, indent=1)
    # reparse post-validate
    json.load(open(path, encoding="utf-8"))
    receipt["faces"].append(face_rec)

RP = os.path.join(ROOT, "results", "_r700bmc_w14_fuse_surgery.json")
with open(RP, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=False, indent=1))
