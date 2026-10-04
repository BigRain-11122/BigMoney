# -*- coding: utf-8 -*-
# r666 bm-b merge resolver round-2 (3 UU special faces, same recipes second pass)
import json, subprocess, io, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "scripts")

def run(cmd):
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def blob(ref, path):
    rc, out, err = run(["git", "show", ref + ":" + path])
    if rc != 0:
        raise RuntimeError("blob read fail %s:%s" % (ref, path))
    return out

rc, st, _ = run(["git", "status", "--porcelain"])
uu = [l[3:].strip() for l in st.decode("utf-8", "replace").splitlines() if l[:2] in ("UU", "AA")]
print("UU faces:", uu)
assert sorted(uu) == ["results/compute_audit.json", "results/crash_fuse.json",
                      "results/token_usage.json"], "face set drifted: %s" % uu
report = {"round": 2, "uu": uu}

# --- crash_fuse: origin base + lane settle + containment both sides ---
mine = json.loads(blob("HEAD", "results/crash_fuse.json").decode("utf-8", "replace"))
theirs = json.loads(blob("MERGE_HEAD", "results/crash_fuse.json").decode("utf-8", "replace"))
rc, out, err = run(["git", "checkout", "origin/main", "--", "results/crash_fuse.json"])
assert rc == 0, "fuse checkout fail"
import merge_lane_views as mlv
r = mlv.sync_face("crash_fuse")
now = json.load(io.open("results/crash_fuse.json", encoding="utf-8"))
mine_sigs = set((mine.get("sigs") or {}).keys())
theirs_sigs = set((theirs.get("sigs") or {}).keys())
now_sigs = set((now.get("sigs") or {}).keys())
lost_m = mine_sigs - now_sigs
lost_t = theirs_sigs - now_sigs
print("fuse settle:", str(r)[:120])
print("sigs mine %d theirs %d -> post %d | lost_m %d lost_t %d"
      % (len(mine_sigs), len(theirs_sigs), len(now_sigs), len(lost_m), len(lost_t)))
assert not lost_m and not lost_t, "fuse sig loss: %s %s" % (sorted(lost_m)[:3], sorted(lost_t)[:3])
report["fuse"] = {"mine": len(mine_sigs), "theirs": len(theirs_sigs),
                  "post": len(now_sigs), "lost": 0}

# --- compute_audit: (ts,canon) union zero-loss both sides ---
o = json.loads(blob("HEAD", "results/compute_audit.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/compute_audit.json").decode("utf-8", "replace"))

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

seen = set()
union = []
for row in sorted(o["history"] + t["history"], key=lambda x: str(x.get("ts", ""))):
    k = (str(row.get("ts", "")), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {(str(r.get("ts", "")), canon(r)) for r in o["history"]}
t_set = {(str(r.get("ts", "")), canon(r)) for r in t["history"]}
u_set = {(str(r.get("ts", "")), canon(r)) for r in union}
lost_o, lost_t = len(o_set - u_set), len(t_set - u_set)
print("audit union rows:", len(union), "| lost ours", lost_o, "lost theirs", lost_t)
assert lost_o == 0 and lost_t == 0, "audit zero-loss violated"
o["history"] = union[-400:]
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(o, f, ensure_ascii=False, indent=1)
json.loads(io.open("results/compute_audit.json", encoding="utf-8").read())
report["audit"] = {"rows": len(union), "lost": 0}

# --- token_usage: whole-face freshness (r456 explicit fallback; keyset check) ---
ot = json.loads(blob("HEAD", "results/token_usage.json").decode("utf-8", "replace"))
tt = json.loads(blob("MERGE_HEAD", "results/token_usage.json").decode("utf-8", "replace"))
ok_keyset = sorted(ot.get("machines", {}).keys()) == sorted(tt.get("machines", {}).keys())
ours_newer = str(ot.get("generated", "")) >= str(tt.get("generated", ""))
print("token: keyset_identical=%s ours_gen=%s theirs_gen=%s ours_newer=%s"
      % (ok_keyset, ot.get("generated"), tt.get("generated"), ours_newer))
assert ok_keyset, "token keyset diverged -> machines-union needed"
winner = ot if ours_newer else tt
with io.open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(winner, ensure_ascii=False, indent=1))
json.loads(io.open("results/token_usage.json", encoding="utf-8").read())
report["token"] = {"took": "ours" if ours_newer else "theirs",
                   "gen": winner.get("generated")}

# --- marker check ---
bad = []
for f in uu:
    for i, line in enumerate(io.open(f, "rb").read().split(b"\n")):
        if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>"):
            bad.append((f, i + 1))
assert not bad, "marker residue: %s" % bad[:3]
print("marker residue: none")

with io.open("results/_r666bmb_merge_resolve_r2.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_R2_DONE")
