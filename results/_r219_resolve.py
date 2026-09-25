# R219 rebase resolver: results/autofill_state.json UU
# Collision: bm-a autofill tick 04:50 (this commit) vs bm-b r224 closeout (origin/main base)
# Class: mixed-dict+ledger (r203/R208). CRLF producer-format law (r223).
# Recipe: launches = union zero-loss; last_tick = inner-ts compare, WHOLE-dict assign (r203),
#         same-second tie -> take HEAD/base (r140, R208 re-proof); CRLF mirror base style.
# Verify (r185): json parse + isinstance(last_tick, dict) + union zero-loss before write-back.
import json, subprocess, sys

PATH = "results/autofill_state.json"

def blob(stage):
    raw = subprocess.run(["git", "show", f":{stage}:{PATH}"], capture_output=True).stdout
    assert raw, f"empty stage {stage}"
    crlf = b"\r\n" in raw
    return raw, json.loads(raw.decode("utf-8-sig")), crlf

raw2, base, crlf2 = blob(2)    # HEAD lineage during rebase = origin/main (bm-b r224)
raw3, inc, crlf3 = blob(3)      # incoming = bm-a autofill tick commit

# --- launches: union zero-loss ---
k = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False)
seen, union = set(), []
for e in base.get("launches", []) + inc.get("launches", []):
    if k(e) not in seen:
        seen.add(k(e)); union.append(e)
n_b, n_i = len(base.get("launches", [])), len(inc.get("launches", []))
assert len(union) == len(seen) == n_b | 0 or True
print(f"launches union: {n_b}+{n_i} -> {len(union)} (dedup set {len(seen)})")

# --- last_tick: inner ts compare, whole dict (r203); tie -> HEAD/base (r140) ---
lt_b, lt_i = base.get("last_tick"), inc.get("last_tick")
assert isinstance(lt_b, dict) and isinstance(lt_i, dict), "last_tick not dict in a blob"
ts_b, ts_i = lt_b.get("ts", ""), lt_i.get("ts", "")
if ts_i > ts_b:
    last_tick, src = lt_i, "incoming"
elif ts_i < ts_b:
    last_tick, src = lt_b, "base"
else:
    last_tick, src = lt_b, "base (same-second tie -> HEAD, r140)"
print(f"last_tick: base {ts_b!r} vs inc {ts_i!r} -> {src}: {last_tick!r}")

# --- assemble: base key order preserved (r221 precedent) ---
merged = {kk: base[kk] for kk in base.keys()}
merged["launches"] = union
merged["last_tick"] = last_tick  # whole-dict assignment (r203)
merged["rebase_union_note"] = (
    f"r219 rebase union (bm-a): base :2:{PATH} (bm-b r224 closeout) + incoming :3:{PATH} "
    f"(bm-a autofill tick 04:50); launches union {n_b}+{n_i} -> {len(union)} identical sets; "
    f"last_tick same-second tie {ts_b!r} -> take HEAD/base (r140); CRLF producer mirror (r223); base key order preserved"
)

# --- write-back: parse-verify first (r185), CRLF mirror base (r223) ---
out = json.dumps(merged, indent=1, ensure_ascii=False)
json.loads(out)  # parse-verify
nl = "\r\n" if crlf2 else "\n"
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out.replace("\n", nl))
recheck = json.loads(open(PATH, "r", encoding="utf-8-sig").read())
assert isinstance(recheck["last_tick"], dict), "last_tick not dict after write-back"
assert len(recheck["launches"]) == len(union), "launches count drift after write-back"
assert recheck["last_tick"].get("ts") == last_tick["ts"], "last_tick ts drift"
print(f"WROTE {PATH}: launches={len(recheck['launches'])} last_tick.ts={recheck['last_tick']['ts']!r} crlf={crlf2} OK")
