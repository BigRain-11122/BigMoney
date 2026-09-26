"""r283 bm-a rebase conflict resolver: results/autofill_state.json (mixed-dict+ledger).

Law chain: r203/R208 (union zero-loss) + r215 (launches cap-50 rolling) + r220
(last_tick whole-dict compare, same-second tie -> HEAD) + r245 (write-back
re-sorted ts ascending, producer append-order format face) + r223/r234 (mirror
base blob EOL=CRLF) + r185 (parse-verify before write-back).

Context: bm-a R283 S3 push window; bm-b r286 tick-tail commit landed between my
amend and push; both machines' 01:20 ticks rewrote the shared state -> UU.
Resolution: launches = full-content union (52 unique) -> newest 50 kept -> ts
ascending write-back; last_tick = same-second tie (both 01:20:01) -> HEAD
(origin side) whole dict.
"""
import json
import subprocess

PATH = "results/autofill_state.json"


def blob(ref: str) -> dict:
    raw = subprocess.run(["git", "show", ref], capture_output=True).stdout
    return json.loads(raw.decode("utf-8-sig"))


ours = blob(":2:" + PATH)      # rebase: HEAD = origin side (bm-b landed)
theirs = blob(":3:" + PATH)    # my replayed tick-tail commit

# launches union, dedup by canonical record content (zero-loss face)
o_l = ours.get("launches", [])
t_l = theirs.get("launches", [])
seen = {}
for rec in o_l + t_l:
    key = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    seen[key] = rec
union = list(seen.values())
assert len(union) == len({json.dumps(r, sort_keys=True, ensure_ascii=False) for r in union})

# cap 50 newest by ts (r215), then re-sort ascending for write-back (r245)
union.sort(key=lambda r: r["ts"], reverse=True)
kept = union[:50]
kept.sort(key=lambda r: r["ts"])

# last_tick: compare inner ts; same-second tie -> HEAD/origin side (r140/r220)
lt_o = ours.get("last_tick") or {}
lt_t = theirs.get("last_tick") or {}
ts_o, ts_t = lt_o.get("ts", ""), lt_t.get("ts", "")
last_tick = lt_o if ts_o >= ts_t else lt_t  # tie or newer -> ours(HEAD); else theirs
assert isinstance(last_tick, dict), "last_tick must remain a dict (r220 law)"

out = {"last_tick": last_tick, "launches": kept}
json.dumps(out)  # parse-verify gate before write (r185)

# write-back mirroring producer format (r223/r234 probe: CRLF, indent=1,
# no BOM, no trailing newline, ASCII)
text = json.dumps(out, ensure_ascii=False, indent=1)
raw = text.replace("\r\n", "\n").replace("\n", "\r\n")
assert not raw.endswith("\n")  # producer blob has no trailing newline
with open(PATH, "wb") as f:
    f.write(raw.encode("utf-8"))

print(f"union={len(union)} kept={len(kept)} last_tick.ts={last_tick.get('ts')} (origin-side tie)")
print(f"zero-loss: ours={len(o_l)} theirs={len(t_l)} union={len(union)} (expected 52)")
