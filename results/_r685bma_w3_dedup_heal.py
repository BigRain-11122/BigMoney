"""r685 bm-a: W3 checkpoint id-dedup heal (r482 bm-c law, keep-first).

State: HEAD/origin checkpoint = 6136 rows, 4909 unique ids (1227 dup lines
appended by bm-b in-flight shard-1 re-burn; merged in via origin-only-modified
auto-take at 16:05). Keep-first by id = keeps the union/origin-verified rows,
drops trailing re-burn lines.

Assertions:
 - dropped == 1227, every dropped id remains exactly once in kept set
 - zero info loss: dropped vs kept same-id rows differ ONLY in elapsed_s
   (bm-c law's non-elapsed field-equality = zero-information-loss check)
 - final == 4909 rows, 4909 unique ids
"""
import json

PATH = r"results/mass_trial/w3_screen_checkpoint.jsonl"
OUT = r"results/_r685bma_w3_dedup_heal.json"

raw = open(PATH, "rb").read()
lines = [l for l in raw.split(b"\n") if l.strip()]
kept, seen = [], {}
dropped = []
for ln in lines:
    row = json.loads(ln.decode("utf-8"))
    jid = row["id"]
    if jid in seen:
        dropped.append((ln, row))
    else:
        seen[jid] = row
        kept.append(ln)

assert len(kept) == 4909, f"kept {len(kept)} != 4909"
assert len(dropped) == 1227, f"dropped {len(dropped)} != 1227"
diff_fields = set()
for ln, row in dropped:
    k = seen[row["id"]]
    for f in set(k) | set(row):
        if k.get(f) != row.get(f):
            diff_fields.add(f)
assert diff_fields <= {"elapsed_s"}, f"nondeterministic drift beyond elapsed_s: {diff_fields}"

out = b"\n".join(kept) + (b"\n" if raw.endswith(b"\n") else b"")
open(PATH, "wb").write(out)

# post-write reparse
rows2 = [json.loads(l) for l in open(PATH, encoding="utf-8") if l.strip()]
ids2 = [r["id"] for r in rows2]
assert len(rows2) == 4909 and len(set(ids2)) == 4909

report = {
    "round": 685, "machine": "bm-a", "law": "r482 bm-c keep-first id-dedup",
    "pre_rows": len(lines), "kept": len(kept), "dropped_dup_lines": len(dropped),
    "dropped_diff_fields": sorted(diff_fields),
    "post_rows": len(rows2), "post_unique": len(set(ids2)),
    "provenance": "dups = bm-b 53b9f3dec in-flight shard-1 re-burn lines (1227), "
                  "merged in at r685 auto-take (origin-only-modified face); "
                  "kept = union/origin-verified rows (bm-c r482 coverage-verified)",
}
json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False))
