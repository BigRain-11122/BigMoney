"""r696 bm-a: origin pool truth probe (N2-W15-GENERATE / CONTEST-RC) + local generate product check."""
import json, subprocess, os, glob, datetime

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
out = {}

def git_show(path):
    r = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")
    return r.stdout, None

# 1) origin pool truth for the two hot entries
raw, err = git_show("results/runnable_pool.json")
if raw is None:
    out["origin_pool_error"] = err
else:
    d = json.loads(raw.decode("utf-8"))
    es = [e for e in d["entries"] if e.get("id") in
          ("PERPETUAL-N2-W15-GENERATE", "CONTEST-YTD-P1-RC-0OF1")]
    out["origin_entries"] = [
        {"id": e.get("id"), "status": e.get("status"),
         "shards": [{"k": s.get("key"), "st": s.get("status"),
                     "own": s.get("owner"), "ts": s.get("owner_since"),
                     "ka": s.get("keepalive_at"), "pid": s.get("pid"),
                     "note": s.get("note")} for s in e.get("shards", [])],
         "runner": e.get("runner"), "args": e.get("args")}
        for e in es]

# 2) local lane mirror for the same entry (bm-a lane)
lane = os.path.join(REPO, "results", "runnable_pool.bm-a.json")
if os.path.exists(lane):
    d2 = json.load(open(lane, encoding="utf-8"))
    es2 = [e for e in d2.get("entries", []) if e.get("id") == "PERPETUAL-N2-W15-GENERATE"]
    out["lane_bma_n2"] = [
        {"shards": [{"k": s.get("key"), "st": s.get("status"),
                     "own": s.get("owner"), "ts": s.get("owner_since")} for s in e.get("shards", [])]}
        for e in es2]

# 3) local N2 product candidates: any file under results/perpetual_n2* / n2 candidates newer than 20:00
cands = []
for pat in ("results/perpetual_n2*", "results/n2*", "results/perpetual_faces_n2*"):
    cands.extend(glob.glob(os.path.join(REPO, pat)))
cands.extend(glob.glob(os.path.join(REPO, "results", "*n2*w15*")))
cands.extend(glob.glob(os.path.join(REPO, "results", "*w15*")))
for p in sorted(set(cands)):
    st = os.stat(p)
    if st.st_mtime > datetime.datetime(2026, 10, 4, 19, 0).timestamp():
        cands_info = {"path": os.path.relpath(p, REPO), "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(), "size": st.st_size}
        cands_info["isdir"] = os.path.isdir(p)
        if os.path.isdir(p):
            cands_info["files"] = []
            for f in sorted(os.listdir(p))[:20]:
                fs = os.stat(os.path.join(p, f))
                cands_info["files"].append({"f": f, "mtime": datetime.datetime.fromtimestamp(fs.st_mtime).isoformat(), "size": fs.st_size})
        out.setdefault("recent_n2_products", []).append(cands_info)

# 4) autofill daemon log tail: what did the 20:09:38 launch-claim burn do?
log_candidates = glob.glob(os.path.join(REPO, "results", "autofill*.log")) + \
                 glob.glob(os.path.join(REPO, "logs", "autofill*")) + \
                 glob.glob(os.path.join(REPO, "results", "_autofill*"))
out["autofill_log_files"] = [os.path.relpath(p, REPO) for p in sorted(set(log_candidates))]

with open(os.path.join(REPO, "results", "_r696bma_n2_truth.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("PROBE_DONE", json.dumps({k: out[k] for k in ("origin_entries", "lane_bma_n2") if k in out}, ensure_ascii=False)[:1500])
print("PRODUCTS:", json.dumps(out.get("recent_n2_products", []), ensure_ascii=False)[:1200])
print("LOGS:", out.get("autofill_log_files"))
