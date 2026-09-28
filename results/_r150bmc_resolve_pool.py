# -*- coding: utf-8 -*-
"""r150 bm-c pool rebase-conflict resolver (r344/r366 union canon).

Conflict shape: whole-file UU on results/runnable_pool.json vs bm-b tick
keepalive commit c6b9346a (census W2B owner refresh). Resolution = union:
origin/HEAD side VERBATIM (newer authoritative: keepalive refresh + all
harvest flips) + my sole delta (TRIAL-LABOR-W3-SCREEN entry append +
updated_at). Assertion-guarded; refuses anything beyond the declared
delta faces. Resolver evidence in-tree per r120 precedent (single-file
routine storm; deleted after commit per r149 law if replay-blocks)."""
import io
import json

SRC = "results/runnable_pool.json"
MY_ID = "TRIAL-LABOR-W3-SCREEN"

raw = io.open(SRC, "r", encoding="utf-8", newline="").read()
lines = raw.replace("\r\n", "\n").split("\n")
idx = {}
for i, ln in enumerate(lines):
    if ln.startswith("<<<<<<<"):
        idx["ours"] = i
    elif ln.startswith("|||||||"):
        idx["base"] = i
    elif ln.startswith("======="):
        idx["sep"] = i
    elif ln.startswith(">>>>>>>"):
        idx["theirs"] = i
assert len(idx) == 4, f"marker scan incomplete: {idx}"

ours_txt = "\n".join(lines[idx["ours"] + 1: idx["base"]]) + "\n}"
base_txt = "\n".join(lines[idx["base"] + 1: idx["sep"]]) + "\n}"
mine_txt = "\n".join(lines[idx["sep"] + 1: idx["theirs"]]) + "\n}"
# shared tail after >>>>>>> = the top-level closing brace only; assert it
tail = "\n".join(lines[idx["theirs"] + 1:]).strip()
assert tail == "}", f"shared tail beyond '}}' not expected: {tail[:60]!r}"

ours = json.loads(ours_txt)
base = json.loads(base_txt)
mine = json.loads(mine_txt)

# --- face 1: my side == base + exactly ONE appended entry (+ updated_at)
assert [e["id"] for e in base["entries"]] == \
       [e["id"] for e in mine["entries"]][:-1], "mine!=base+append(id order)"
added = mine["entries"][-1]
assert added["id"] == MY_ID, f"appended id {added['id']} != {MY_ID}"
base_keys = {k: v for k, v in base.items() if k not in ("entries", "updated_at")}
mine_keys = {k: v for k, v in mine.items() if k not in ("entries", "updated_at")}
assert base_keys == mine_keys, "mine touched non-entry fields beyond updated_at"
print(f"[1] mine == base + 1 appended {MY_ID} (+updated_at): OK")

# --- face 2: ours == base with per-entry status/owner refresh only
ours_ids = [e["id"] for e in ours["entries"]]
base_ids = [e["id"] for e in base["entries"]]
assert ours_ids == base_ids, "ours id set drifted from base (unexpected)"
diffs = []
for o, b in zip(ours["entries"], base["entries"]):
    if o != b:
        d = {k for k in set(o) | set(b) if o.get(k) != b.get(k)}
        diffs.append((o["id"], sorted(d)))
print("[2] ours vs base entry-level drift faces:",
      diffs if diffs else "NONE (byte-identical)")
ours_keys = {k: v for k, v in ours.items() if k not in ("entries", "updated_at")}
assert ours_keys == base_keys, "ours touched schema/law fields"

# --- face 3: census W2B keepalive = the ONLY allowed drift face
allowed = {"CENSUS-FUS-S2-W2B"}
assert all(eid in allowed for eid, _ in diffs), \
       f"drift outside keepalive face: {diffs}"

# --- resolve: ours VERBATIM + my entry appended + updated_at from mine
assert not any(e["id"] == MY_ID for e in ours["entries"]), "double-append"
res = dict(ours)
res["entries"] = list(ours["entries"]) + [added]
res["updated_at"] = mine.get("updated_at", ours.get("updated_at"))

# --- write back: LF lineage (git-side canonical), indent=1, no BOM
with io.open(SRC, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

chk = json.load(io.open(SRC, encoding="utf-8"))
ids = [e["id"] for e in chk["entries"]]
assert ids.count(MY_ID) == 1
assert len(ids) == len(ours_ids) + 1
w2b = [e for e in chk["entries"] if e["id"] == "CENSUS-FUS-S2-W2B"][0]
print(f"[3] RESOLVED: {len(ids)} entries; {MY_ID} present once; "
      f"census W2B keepalive carried: "
      f"{json.dumps({k: w2b[k] for k in ('status','lane_owner')}, ensure_ascii=False)}")
print("resolver OK")
