"""_r360bmb_resolve -- push-storm rebase conflict resolution (r360 bm-b).

Conflict: 1 UU results/autofill_state.json (mixed-dict+ledger, classifier
GREEN; recipe r203/R208/r215/r245). Ours(base)=bm-a r382 tick ts 04:50:01;
theirs(replayed tick)=bm-b tick ts 04:50:02 -> last_tick = inner-ts newer
(theirs, whole-dict assignment, no str()); launches identical on both
sides (50 rows, zero diff keys) -> union = same set, re-sorted ts asc
(producer append order, r245 law), cap 50. CRLF producer format + indent 1
mirrored from base blob (r223 law). Parse-verify before write-back (r185).
Closeout = r355-addendum direct connection (r358 law: win-git 2.55
rebase --continue EDITOR-refusal family): commit -F -> rebase --quit ->
cherry-pick remainder -> update-ref -> checkout.
"""
import json
import subprocess

PATH = "results/autofill_state.json"


def stage_blob(stage):
    b = subprocess.run(["git", "show", f":{stage}:{PATH}"],
                       capture_output=True).stdout
    return json.loads(b.decode("utf-8-sig")), b


ours, raw_ours = stage_blob(2)
theirs, _ = stage_blob(3)

# last_tick: inner-ts compare, newer wins (tie -> ours/HEAD, r140)
lt_o, lt_t = ours["last_tick"], theirs["last_tick"]
newer_is_theirs = str(lt_t.get("ts", "")) > str(lt_o.get("ts", ""))
last_tick = lt_t if newer_is_theirs else lt_o
print(f"last_tick: ours ts={lt_o.get('ts')!r} theirs ts={lt_t.get('ts')!r} "
      f"-> {'theirs' if newer_is_theirs else 'ours'} (whole dict)")

# launches: union both blobs (row identity), sort ts desc, cap 50,
# re-sort ascending (producer append order, r245)
seen, rows = set(), []
for blob in (ours, theirs):
    for r in blob.get("launches", []):
        key = json.dumps(r, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            rows.append(r)
rows.sort(key=lambda r: str(r.get("ts", "")), reverse=True)
rows = rows[:50]
rows.sort(key=lambda r: str(r.get("ts", "")))
print(f"launches: union {len(seen)} distinct rows -> cap 50 -> "
      f"kept {len(rows)} (ts asc)")

merged = {"last_tick": last_tick, "launches": rows}

# parse-verify (r185) + isinstance(last_tick, dict) (r215)
json.dumps(merged)
assert isinstance(merged["last_tick"], dict), "last_tick must be dict"

# write-back mirroring base blob: CRLF producer format, indent 1 (r223)
crlf = b"\r\n" in raw_ours[:200]
text = json.dumps(merged, ensure_ascii=False, indent=1)
with open(PATH, "w", encoding="utf-8", newline="" if crlf else "\n") as fh:
    fh.write(text + ("\r\n" if crlf else "\n"))

# verify round-trip from disk
back = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert back == merged, "disk round-trip mismatch"
assert isinstance(back["last_tick"], dict)
print(f"written+verified: last_tick ts={back['last_tick']['ts']} "
      f"launches={len(back['launches'])} crlf={crlf}")
