# -*- coding: utf-8 -*-
# r666 bm-b push-race merge resolver (15 UU, r665 recipe adapted; r657 laws:
# full-count UU, surgery separate from add, reparse-before-add)
#   12 regen snapshot faces -> origin-verbatim (next S6 re-derives)
#   crash_fuse.json (POOL-family shared face) -> origin + sync_face settle
#     (merge_crash_fuse = per-sig newer-event-wins) + my-sig containment assert
#   compute_audit.json -> (ts, canonical) union + zero-loss containment
#   token_usage.json -> take-ours under premises (keyset identical + ours
#     generated newer + machines entries lack per-key ts -> r456 explicit
#     whole-face freshness fallback, side-pick documented)
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
uu = [l[3:].strip() for l in st.decode("utf-8", "replace").splitlines()
      if l[:2] in ("UU", "AA")]
print("UU faces:", len(uu))
assert len(uu) == 15, "expected 15 UU, got %d -- face set drifted, re-inspect" % len(uu)

FUSE = "results/crash_fuse.json"
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
special = {FUSE, AUDIT, TOKEN}
report = {"uu_n": len(uu), "checkout_origin": [], "fuse_settle": None,
          "audit_union": None, "token_takeours": None}

# --- 1) regen faces: take origin ---
for f in uu:
    if f in special:
        continue
    rc, out, err = run(["git", "checkout", "origin/main", "--", f])
    assert rc == 0, "checkout origin fail %s" % f
    report["checkout_origin"].append(f)
print("checkout origin (regen):", len(report["checkout_origin"]))
assert len(report["checkout_origin"]) == 12

# --- 2) crash_fuse: origin base + lane settle; my-sig containment ---
mine = json.loads(blob("HEAD", FUSE).decode("utf-8", "replace"))
rc, out, err = run(["git", "checkout", "origin/main", "--", FUSE])
assert rc == 0, "fuse checkout fail"
import merge_lane_views as mlv
r = mlv.sync_face("crash_fuse")
report["fuse_settle"] = str(r)[:220]
now = json.load(io.open(FUSE, encoding="utf-8"))
mine_sigs = set((mine.get("sigs") or {}).keys())
now_sigs = set((now.get("sigs") or {}).keys())
lost = mine_sigs - now_sigs
print("fuse settle:", str(r)[:140])
print("my sigs:", len(mine_sigs), "-> post:", len(now_sigs), "| lost:", len(lost))
assert not lost, "fuse sig loss after settle: %s" % sorted(lost)[:5]
report["fuse_pre_sigs"] = len(mine_sigs)
report["fuse_post_sigs"] = len(now_sigs)

# --- 3) compute_audit.json: (ts, canonical) union, zero-loss containment ---
o = json.loads(blob("HEAD", AUDIT).decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", AUDIT).decode("utf-8", "replace"))

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
assert lost_o == 0 and lost_t == 0, "audit union zero-loss violated"
o["history"] = union[-400:]
with io.open(AUDIT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(o, f, ensure_ascii=False, indent=1)
json.loads(io.open(AUDIT, encoding="utf-8").read())  # reparse gate
report["audit_union"] = {"rows": len(union), "lost_o": lost_o, "lost_t": lost_t}

# --- 4) token_usage.json: take-ours under premises (r456 explicit fallback) ---
ot = json.loads(blob("HEAD", TOKEN).decode("utf-8", "replace"))
tt = json.loads(blob("MERGE_HEAD", TOKEN).decode("utf-8", "replace"))
ok_keyset = sorted(ot.get("machines", {}).keys()) == sorted(tt.get("machines", {}).keys())
ok_newer = str(ot.get("generated", "")) >= str(tt.get("generated", ""))
report["token_takeours"] = {"keyset_identical": ok_keyset, "ours_newer": ok_newer,
                            "ours_gen": ot.get("generated"), "theirs_gen": tt.get("generated")}
print("token premises: keyset_identical=%s ours_newer=%s" % (ok_keyset, ok_newer))
assert ok_keyset and ok_newer, "take-ours premises failed -> needs machines-union, do not force"
with io.open(TOKEN, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(ot, ensure_ascii=False, indent=1))
json.loads(io.open(TOKEN, encoding="utf-8").read())  # reparse gate

# --- marker check on all resolved faces (r644: content check, not rc) ---
bad = []
for f in uu:
    try:
        b = io.open(f, "rb").read()
    except FileNotFoundError:
        continue
    for i, line in enumerate(b.split(b"\n")):
        if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>"):
            bad.append((f, i + 1))
assert not bad, "marker residue: %s" % bad[:5]
print("marker residue: none")

with io.open("results/_r666bmb_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_DONE (surgery only; add/commit/push = separate steps per r657-3)")
