"""r483 bm-c: W3 checkpoint id-level keep-first dedup gate (r482 law).
1227 dup rows expected (bm-b shard-1 double-burn absorb face). Byte-level
line surgery: kept lines byte-identical to original; dropped rows must
differ from kept twin ONLY in elapsed_s (zero-information-loss assertion).
Atomic replace + full post-verification. Evidence JSON + stdout report."""
import json
import os
import sys

PATH = "results/mass_trial/w3_screen_checkpoint.jsonl"
EVID = "results/_r483bmc_ckpt_dedup.json"
ALLOWED_DIFF = {"elapsed_s"}

raw = open(PATH, "rb").read()
ends_nl = raw.endswith(b"\n")
lines = raw.split(b"\n")
if ends_nl:
    lines = lines[:-1]

kept = []          # (idx, bytes)
kept_by_id = {}    # id -> (idx, parsed, bytes)
dropped = []       # (idx, parsed, twin_idx)
diff_keys_all = set()
bad = []

for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    d = json.loads(ln.decode("utf-8"))
    rid = d["id"]
    if rid in kept_by_id:
        twin = kept_by_id[rid]
        diff = [k for k in set(d) | set(twin[1])
                if d.get(k) != twin[1].get(k)]
        diff_keys_all |= set(diff)
        if not set(diff) <= ALLOWED_DIFF:
            bad.append({"id": rid, "extra_diff": diff})
        dropped.append((i, d, twin[0]))
    else:
        kept_by_id[rid] = (i, d, ln)
        kept.append((i, ln))

if bad:
    print("ABORT: dup pairs differ beyond elapsed_s:", bad[:3])
    sys.exit(2)

n_dropped = len(dropped)
out_lines = [ln for _, ln in kept]
new_raw = b"\n".join(out_lines) + (b"\n" if ends_nl else "")

tmp = PATH + ".r483tmp"
with open(tmp, "wb") as f:
    f.write(new_raw)

# verify temp before replace
vrows = [json.loads(l) for l in open(tmp, encoding="utf-8") if l.strip()]
vids = [r["id"] for r in vrows]
cand_meta = json.load(open("results/mass_trial/w3_candidates.json",
                          encoding="utf-8"))
n_expected = cand_meta["n"]
cids = set(r["id"] for r in cand_meta["candidates"])
comp = {"candidate": 0, "control": 0, "null": 0}
for r in vrows:
    comp[r.get("row_type")] = comp.get(r.get("row_type"), 0) + 1
cand_ids = set(r["id"] for r in vrows if r.get("row_type") == "candidate")

assert len(vrows) == len(kept_by_id), "row count mismatch"
assert len(set(vids)) == len(vids), "dup ids remain"
assert comp["candidate"] == n_expected, (comp, n_expected)
assert cand_ids == cids, "candidate id tiling mismatch"
assert all(dd[1]["id"] in kept_by_id for dd in dropped), "dropped id lost"
assert n_dropped == len(dropped)

os.replace(tmp, PATH)

ev = {
    "round": "r483 bm-c", "path": PATH,
    "rows_before": len(lines), "rows_after": len(vrows),
    "dropped_dup_rows": n_dropped,
    "dup_diff_keys_seen": sorted(diff_keys_all),
    "diff_within_allowed": sorted(diff_keys_all) == ["elapsed_s"],
    "composition_after": comp, "n_expected": n_expected,
    "candidate_id_tiling_exact": cand_ids == cids,
    "kept_lines_byte_identical": True,
    "verdict": "OK" if (comp["candidate"] == n_expected
                        and len(set(vids)) == len(vids)) else "FAIL",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False, indent=1))
