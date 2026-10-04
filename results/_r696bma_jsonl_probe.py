"""r696 bm-a: locate non-dict jsonl lines in merge sides (HEAD/MERGE_HEAD)."""
import json, subprocess, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FACES = ["results/x2_watch_log.jsonl", "results/pool_core_samples.jsonl",
         "results/pool_red_flags.jsonl"]

def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None

out = {}
for p in FACES:
    for rev in ("HEAD", "MERGE_HEAD", "WORKTREE"):
        if rev == "WORKTREE":
            try:
                raw = open(ROOT + "\\" + p.replace("/", "\\"), "rb").read()
            except OSError as e:
                out[p + ":" + rev] = "READ_FAIL " + str(e)
                continue
        else:
            raw = blob(rev, p)
            if raw is None:
                out[p + ":" + rev] = "BLOB_FAIL"
                continue
        bad = []
        lines = raw.decode("utf-8", errors="replace").splitlines()
        for i, ln in enumerate(lines):
            if not ln.strip():
                continue
            try:
                v = json.loads(ln)
                if not isinstance(v, dict):
                    bad.append((i, "non-dict: " + ln[:80]))
            except Exception as ex:
                bad.append((i, "%s: %s" % (type(ex).__name__, ln[:110])))
        out["%s:%s" % (p, rev)] = {"total": len(lines), "bad": bad[:5]}

with open(ROOT + r"\results\_r696bma_jsonl_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:2500])
