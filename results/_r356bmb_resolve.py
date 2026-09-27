# -*- coding: utf-8 -*-
"""r356 bm-b S0 rebase UU resolver v2: results/autofill_state.json (mixed-dict+ledger).
Probed real structure: top keys = {last_tick, launches}; launch rows are EVENT records
(ts, machine, entry, shard, pid, ...) with NO identity field -> per r373 law, identity-less
rows go full-row append-log union (dedup identical rows). Cap 50 = rolling window keep-newest
(R215). Write-back order = ts ASC (r245). last_tick = inner-ts compare, whole dict, tie->HEAD
(r140; in rebase HEAD == upstream :2:, r352 side-map law).
"""
import json, subprocess, io

PATH = "results/autofill_state.json"

def show(spec):
    p = subprocess.run(["git", "show", spec], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git show {spec} failed rc={p.returncode}")
    return p.stdout.decode("utf-8")

s2_txt = show(f":2:{PATH}")
s3_txt = show(f":3:{PATH}")
up = json.loads(s2_txt)   # :2: = HEAD = upstream (r352 rebase map)
ours = json.loads(s3_txt) # :3: = replayed local commit

up_l = up.get("launches", [])
our_l = ours.get("launches", [])
print(f"upstream launches={len(up_l)} ts[{up_l[0]['ts']}..{up_l[-1]['ts']}] machine={up_l[0]['machine']}" if up_l else "upstream empty")
print(f"ours     launches={len(our_l)} ts[{our_l[0]['ts']}..{our_l[-1]['ts']}] machine={our_l[0]['machine']}" if our_l else "ours empty")

# full-row union, dedup identical event rows (r373 identity-less append-log)
seen = {}
for e in up_l + our_l:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    seen[key] = e
union_all = sorted(seen.values(), key=lambda e: str(e.get("ts", "")), reverse=True)
capped = union_all[:50]
capped.sort(key=lambda e: str(e.get("ts", "")))  # write back ts ASC

dropped = union_all[50:]
drop_ts = sorted({str(e.get("ts", "")) for e in dropped})
kept_min_ts = str(capped[0]["ts"]) if capped else ""
legal = all(t <= kept_min_ts for t in drop_ts)
print(f"union_unique={len(union_all)} capped=50 dropped={len(dropped)} drop_ts={drop_ts} kept_min_ts={kept_min_ts} legal_rolloff={legal}")
assert legal, "ILLEGAL drop: dropped row newer than kept minimum"

# last_tick: inner ts compare, whole dict, tie -> HEAD = upstream (r140+r352)
ut = up.get("last_tick") or {}
ot = ours.get("last_tick") or {}
assert isinstance(ut, dict) and isinstance(ot, dict), f"last_tick not dict: up={type(ut)} ours={type(ot)}"
last_tick = ot if str(ot.get("ts", "")) > str(ut.get("ts", "")) else ut
print(f"last_tick: up={ut.get('ts')}({ut.get('machine')}) ours={ot.get('ts')}({ot.get('machine')}) -> {last_tick.get('ts')}({last_tick.get('machine')})")

merged = {"last_tick": last_tick, "launches": capped}

# parse-verify before write (r185); assert last_tick dict (r220)
out = json.dumps(merged, ensure_ascii=False, indent=1)
json.loads(out)
assert isinstance(merged["last_tick"], dict)

# zero-loss: every kept row must exist verbatim in one of the two blobs
blob_rows = set()
for e in up_l + our_l:
    blob_rows.add(json.dumps(e, sort_keys=True, ensure_ascii=False))
for e in capped:
    assert json.dumps(e, sort_keys=True, ensure_ascii=False) in blob_rows, "zero-loss violation"

crlf = "\r\n" in s2_txt
data = out.replace("\n", "\r\n") if crlf else out
with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(data + ("\r\n" if crlf else "\n"))
print(f"written crlf={crlf} bytes={len(data.encode('utf-8'))}")
print("RESOLVE_OK v2")
