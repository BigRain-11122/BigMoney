"""r369 bm-a rebase resolver: results/autofill_state.json (mixed-dict+ledger).

Skill canon: launches = union both blobs -> composite-key (ts,machine,pid,
runner_sha256,entry,shard) dedup with content-parity check (r322: additive
field-set diff = merge keep one; true divergence = flag, no silent store)
-> sort ts -> cap 50 (keep newest, drop oldest only) -> write back re-sorted
ASCENDING (r245 producer-append order law); last_tick = inner-ts compare then
WHOLE-dict assign, no str() compare, same-second tie -> ours/HEAD (r140);
isinstance(last_tick, dict) assert; mirror producer line endings via newline
translation (r223/r234 CRLF producer-format law).
"""
import json
import subprocess
import sys

PATH = "results/autofill_state.json"
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")


def blob(stage):
    raw = subprocess.run(
        ["git", "show", f":{stage}:{PATH}"], capture_output=True,
        check=True).stdout
    return raw.decode("utf-8-sig"), raw


def kentry(e):
    return tuple(e.get(k) for k in KEY)


ours_raw, ours_bytes = blob(2)      # origin side (upstream)
theirs_raw, theirs_bytes = blob(3)  # my replayed commit
base_raw, base_bytes = blob(1)

ours = json.loads(ours_raw)
theirs = json.loads(theirs_raw)

lo, lt = ours.get("launches", []), theirs.get("launches", [])
print(f"launches ours={len(lo)} theirs={len(lt)}")

# union with composite-key dedup (r322)
by_key, flags = {}, []
for src_name, src in (("ours", lo), ("theirs", lt)):
    for e in src:
        k = kentry(e)
        if k in by_key:
            a, b = by_key[k], e
            if a == b:
                continue
            fa, fb = set(a), set(b)
            if fa <= fb or fb <= fa:      # additive field-set diff
                by_key[k] = a if len(fa) >= len(fb) else b
            else:
                flags.append(f"TRUE-DIVERGENCE {k}")
        else:
            by_key[k] = e
if flags:
    print("FLAGS:", flags)
    sys.exit(3)

merged = sorted(by_key.values(), key=lambda e: e.get("ts", ""))
merged = merged[-50:]                      # cap 50 = keep newest (r215)
merged.sort(key=lambda e: e.get("ts", ""))  # ascending write-back (r245)

# last_tick: inner-ts compare, whole-dict assign, tie -> ours (r140)
ot, tt = ours.get("last_tick") or {}, theirs.get("last_tick") or {}
pick = ours
if isinstance(tt, dict) and tt.get("ts", "") > (ot.get("ts", "") if isinstance(ot, dict) else ""):
    pick = theirs
last_tick = (pick.get("last_tick") if isinstance(pick.get("last_tick"), dict)
             else (tt if tt else ot))
assert isinstance(last_tick, dict), "last_tick must be dict"

out = {"last_tick": last_tick, "launches": merged}
print(f"union launches={len(merged)} (|A|={len(lo)} |B|={len(lt)} "
      f"|A u B| dedup={len(by_key)}) last_tick.ts={last_tick.get('ts')} "
      f"side={'theirs' if last_tick is tt and tt else 'ours'}")

# mirror producer line endings: newline translation per base/ours blob
crlf = b"\r\n" in base_bytes[:2000] or b"\r\n" in ours_bytes[:2000]
with open(PATH, "w", encoding="utf-8", newline=("\r\n" if crlf else "\n")) as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

v = json.load(open(PATH, encoding="utf-8"))
assert isinstance(v["last_tick"], dict) and len(v["launches"]) == len(merged)
ts_seq = [e.get("ts", "") for e in v["launches"]]
assert ts_seq == sorted(ts_seq), "launches not ascending (r245)"
print(f"WROTE {PATH}: launches={len(v['launches'])} ascending OK "
      f"last_tick.ts={v['last_tick'].get('ts')} crlf={crlf}")
