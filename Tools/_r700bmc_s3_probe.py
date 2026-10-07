"""r700 bm-c S3 probe: judge-lane liveness + board + post_review + engine
verdict, compact facts -> stdout + results/_r700bmc_s3_facts.json."""
import glob
import json
import os
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {}


def load(p):
    try:
        with open(os.path.join(REPO, p), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        return {"_err": str(exc)}


# 1) saturation engine verdict (first lines only)
p = subprocess.run(["python", os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
head = "\n".join((p.stdout or "").splitlines()[:12])
facts["sat_rc"] = p.returncode
facts["sat_head"] = head
print("== satengine rc=%d" % p.returncode)
print(head)

# 2) autofill state (full)
af = load(r"results\autofill_state.bm-c.json")
facts["autofill"] = {k: af.get(k) for k in sorted(af) if k not in ("bands", "waves")}
print("== autofill keys:", sorted(af)[:20])
print(json.dumps(facts["autofill"], ensure_ascii=False)[:800])

# 3) crash fuse
cf = load(r"results\crash_fuse.json")
facts["crash_fuse"] = {k: cf.get(k) for k in ("state", "reason", "last_crash_ts", "code_sha", "code_changed", "ts", "updated")}
print("== crash_fuse:", json.dumps(facts["crash_fuse"], ensure_ascii=False)[:400])

# 4) judge runner liveness: any pythonw running trial_labor w14?
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                   "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe' or Name='python.exe'\" | "
                   "Where-Object {$_.CommandLine -match 'trial_labor|w14|judge'} | "
                   "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
                  capture_output=True, text=True, encoding="utf-8", errors="replace")
procs = []
try:
    obj = json.loads(r.stdout) if r.stdout.strip() else []
    if isinstance(obj, dict):
        obj = [obj]
    for o in obj:
        procs.append({"pid": o.get("ProcessId"),
                      "created": str(o.get("CreationDate")),
                      "cmd": (o.get("CommandLine") or "")[:160]})
except Exception:
    procs.append({"_parse_err": r.stdout[:200]})
facts["judge_procs"] = procs
print("== judge procs:", json.dumps(procs, ensure_ascii=False)[:600])

# 5) W14 judge progress faces
faces = {}
for pat in (r"results\trial_labor_w14*", r"results\trial_labor\w14*", r"results\w14*"):
    for f in glob.glob(os.path.join(REPO, pat)):
        try:
            st = os.stat(f)
            faces[os.path.relpath(f, REPO)] = {"size": st.st_size, "mtime": st.st_mtime}
        except OSError:
            pass
facts["w14_faces"] = {k: v for k, v in sorted(faces.items())[:20]}
print("== w14 faces:", json.dumps(facts["w14_faces"], ensure_ascii=False)[:600])
# checkpoint / ledger counts if present
for f in sorted(faces):
    if "judge" in f.lower() and f.endswith(".json"):
        d = load(f)
        if isinstance(d, dict):
            for key in ("judged", "cells_judged", "n_judged", "done", "history", "checkpoint"):
                if key in d:
                    v = d[key]
                    facts.setdefault("w14_progress", {})[os.path.basename(f) + "#" + key] = \
                        len(v) if isinstance(v, list) else v
print("== w14 progress:", json.dumps(facts.get("w14_progress", {}), ensure_ascii=False)[:400])

# 6) post_review last state
pr = load(r"results\post_review.jsonl_stats.json")
rr = None
try:
    with open(os.path.join(REPO, "results", "post_review.jsonl"), encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip()]
    last = json.loads(lines[-1])
    rr = {"total_lines": len(lines), "last_verdict": last.get("verdict"), "last_ts": last.get("ts")}
except Exception as exc:
    rr = {"_err": str(exc)}
facts["post_review"] = rr
print("== post_review:", json.dumps(rr, ensure_ascii=False)[:300])

# 7) tasks board
board = []
for f in sorted(glob.glob(os.path.join(REPO, "fleet", "tasks", "*.json"))):
    d = load(os.path.relpath(f, REPO))
    status = d.get("status")
    if status in ("open", "claimed", "in_progress"):
        board.append({"file": os.path.basename(f), "status": status,
                      "claimed_by": d.get("claimed_by"), "subject": (d.get("subject") or d.get("title") or "")[:80]})
facts["board"] = board
print("== board active:", json.dumps(board, ensure_ascii=False)[:900])

out = os.path.join(REPO, "results", "_r700bmc_s3_facts.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("== facts ->", out)
