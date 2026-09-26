"""R242 bm-a push-collision resolver: results/autofill_state.json (rebase step 6).

Conflict class (classifier): mixed-dict+ledger.
Recipe (skill canonical, r203/R208/r215/r220/r223):
  - launches = union of both blobs' entries -> sort by ts -> cap 50 (R215)
  - last_tick = compare INNER ts then assign WHOLE dict (no str()), same-second
    tie -> HEAD side (r140; in rebase HEAD-context = :2 ours = upstream/origin)
  - parse-verify before write-back (r185); isinstance(last_tick, dict) assert
  - mirror working-tree CRLF (producer format, r223 law) -- probe base blob
Zero-loss law: pre-cap union entry count must equal |ours-entries u theirs-entries|
by identity set.
"""

import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(rev):
    return subprocess.run(["git", "show", rev], capture_output=True,
                          check=True).stdout


def parse(b):
    return json.loads(b.decode("utf-8-sig"))


ours_b = blob(":2:" + PATH)   # rebase: ours = upstream (bm-b origin side)
theirs_b = blob(":3:" + PATH)  # rebase: theirs = my replayed commit
ours = parse(ours_b)
theirs = parse(theirs_b)

# --- launches: union by exact-dict identity, sort by ts, cap 50 ---
lo, lt = ours.get("launches", []), theirs.get("launches", [])
seen = set()
union = []
for e in lo + lt:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(e)
union.sort(key=lambda e: str(e.get("ts", "")))
pre_cap = len(union)
capped = union[-50:]
lost_to_cap = pre_cap - len(capped)

# --- last_tick: whole-dict by inner ts; tie -> ours (:2 = upstream, r140) ---
to, tt = ours.get("last_tick"), theirs.get("last_tick")
if not isinstance(to, dict):
    last_tick = tt
elif not isinstance(tt, dict):
    last_tick = to
else:
    ts_o, ts_t = str(to.get("ts", "")), str(tt.get("ts", ""))
    if ts_t > ts_o:
        last_tick = tt
    else:
        last_tick = to  # includes tie (r140: same-second -> HEAD)

assert isinstance(last_tick, dict), "last_tick must stay a dict (r203 law)"

# --- merge remaining scalar/state keys: take per-key "newer or either" ---
merged = dict(ours)
for k, v in theirs.items():
    if k in ("launches", "last_tick"):
        continue
    if k not in merged:
        merged[k] = v

merged["launches"] = capped
merged["last_tick"] = last_tick

# --- zero-loss assertions (pre-cap union == |A u B| by identity) ---
ident_o = {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in lo}
ident_t = {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in lt}
assert pre_cap == len(ident_o | ident_t), (pre_cap, len(ident_o | ident_t))
assert len(capped) == min(pre_cap, 50)

# --- write back mirroring producer EOL (probe base blob bytes) ---
base_b = blob(":1:" + PATH) if True else b""
crlf = base_b.count(b"\r\n") > 0 and base_b.count(b"\n") == base_b.count(b"\r\n")
if not crlf:
    # also probe the working-tree file's pre-conflict style via ours blob
    crlf = ours_b.count(b"\r\n") > 0 and ours_b.count(b"\n") == ours_b.count(b"\r\n")
out = json.dumps(merged, indent=1, ensure_ascii=False)
nl = "\r\n" if crlf else "\n"
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(nl.join(out.split("\n")))

# --- parse-verify the written file (r185 law) ---
back = json.loads(open(PATH, encoding="utf-8-sig").read())
assert isinstance(back["last_tick"], dict)
assert back["launches"] == capped
print(json.dumps({
    "ours_entries": len(lo), "theirs_entries": len(lt),
    "union_pre_cap": pre_cap, "cap_lost": lost_to_cap,
    "final_launches": len(capped),
    "last_tick_from": "theirs(mine)" if last_tick is tt else "ours(upstream)",
    "last_tick_ts": last_tick.get("ts"),
    "crlf_mirror": bool(crlf),
}, ensure_ascii=False))
print("resolver OK: parse-verified, zero-loss pre-cap asserted")
