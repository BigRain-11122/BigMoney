# r358 bm-c S0 forensics part 2: untracked vs origin identity + burn state.
# Read-only. Encoding fix: stdout utf-8 (r291 U+2212 GBK face).
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def g(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    return r.stdout.decode("utf-8", "replace"), r.returncode


def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha16(b):
    return hashlib.sha256(b).hexdigest().upper()[:16] if b is not None else "ABSENT"


print("=== [3] UNTRACKED vs ORIGIN IDENTITY ===")
for p in ["research/PERPETUAL_N1_W63_PREREG.md",
          "results/perpetual_faces/n1_w62_results.json"]:
    lp = os.path.join(ROOT, p)
    lb = open(lp, "rb").read() if os.path.exists(lp) else None
    ob = blob("origin/main", p)
    print("%s: local=%s origin=%s identical=%s local_len=%s origin_len=%s" % (
        p, sha16(lb), sha16(ob), lb == ob,
        len(lb) if lb else None, len(ob) if ob is not None else None))

print("=== [4] R356/R357 TOOL INVENTORY: local vs origin ===")
for f in sorted(os.listdir(os.path.join(ROOT, "results"))):
    if f.startswith("_r356bmc") or f.startswith("_r357bmc"):
        p = "results/" + f
        lb = open(os.path.join(ROOT, p), "rb").read()
        ob = blob("origin/main", p)
        print("%s: local_sha=%s origin=%s identical=%s" % (f, sha16(lb), sha16(ob), lb == ob))

print("=== [5] W63/W64 SHARD FACE: local files vs origin ls-tree ===")
for wdir in ("n1_w63", "n1_w64"):
    d = os.path.join(ROOT, "results", "p2cal_ext", wdir)
    local_files = sorted(os.listdir(d)) if os.path.isdir(d) else []
    out, rc = g("ls-tree", "--name-only", "origin/main", "results/p2cal_ext/%s/" % wdir)
    origin_files = sorted(x for x in out.strip().splitlines() if x)
    print("%s: local_n=%d origin_n=%d local_only=%s origin_only=%s" % (
        wdir, len(local_files), len(origin_files),
        sorted(set(local_files) - set(origin_files)),
        sorted(set(origin_files) - set(local_files))))

print("=== [6] LANE-STATE M FACES diff stat (live-writer check) ===")
for f in ["results/autofill_state.bm-c.json", "results/dispatcher_state.bm-c.json",
          "results/saturation_engine_state.bm-c.json",
          "results/saturation_engine/face_bm-c.json",
          "results/fund_history_status.json"]:
    out, rc = g("diff", "--stat", "--", f)
    print("--- %s --- %s" % (f, out.strip()))

print("=== [7] ENGINE STATE SNAPSHOT ===")
sp = os.path.join(ROOT, "results", "saturation_engine_state.bm-c.json")
if os.path.exists(sp):
    raw = open(sp, "rb").read()
    d = json.loads(raw)
    keep = {k: d.get(k) for k in ("version", "queue", "active_burns",
                                  "shards_done_total", "last_tick", "status")}
    s = json.dumps(keep, ensure_ascii=False)
    print(s[:1500])

print("=== [7b] FUND_HISTORY (T-131) SNAPSHOT ===")
fp = os.path.join(ROOT, "results", "fund_history_status.json")
if os.path.exists(fp):
    d = json.loads(open(fp, "rb").read())
    print(json.dumps(d, ensure_ascii=False)[:900])

print("=== [8] merge-base + ahead/behind ===")
out, rc = g("merge-base", "HEAD", "origin/main")
print("merge-base:", out.strip())
out, rc = g("rev-list", "--count", "origin/main..HEAD")
print("ahead:", out.strip())
out, rc = g("rev-list", "--count", "HEAD..origin/main")
print("behind:", out.strip())
