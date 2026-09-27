"""R312 bm-a resolve: results/autofill_state.json UU (mixed-dict+ledger recipe).

launches = union(ours, theirs) dedup by (ts,machine,shard) -> sort ts ASC
(canon: cap 50 keep newest 50, then write back re-sorted ascending; producer
format = append order). last_tick = compare inner ts, assign WHOLE dict (no
str()), same-second tie -> HEAD(ours during rebase). CRLF mirror detection.
Law: r203/R208/r215/r220/r245.
"""
import json
import subprocess

ROOT = __file__.rsplit("\\", 2)[0]


def stage_blob_bytes(stage):
    return subprocess.run(
        ["git", "cat-file", "blob", stage],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout


raw_ours = stage_blob_bytes(":2:results/autofill_state.json")
raw_theirs = stage_blob_bytes(":3:results/autofill_state.json")
ours = json.loads(raw_ours.decode("utf-8"))
theirs = json.loads(raw_theirs.decode("utf-8"))

la_o = ours.get("launches", [])
la_t = theirs.get("launches", [])
seen = {}
for e in la_o + la_t:
    key = (e.get("ts"), e.get("machine"), e.get("shard"), e.get("pid"))
    if key not in seen:
        seen[key] = e
merged = sorted(seen.values(), key=lambda e: e.get("ts", ""))
merged = merged[-50:] if len(merged) > 50 else merged
merged.sort(key=lambda e: e.get("ts", ""))  # write-back order = ascending (r245)

lt_o, lt_t = ours.get("last_tick"), theirs.get("last_tick")


def ts_of(x):
    return x.get("ts", "") if isinstance(x, dict) else ""


if isinstance(lt_o, dict) and isinstance(lt_t, dict):
    last_tick = lt_o if ts_of(lt_o) >= ts_of(lt_t) else lt_t  # tie -> HEAD/ours (r140)
else:
    last_tick = lt_o if isinstance(lt_o, dict) else lt_t

out = {"launches": merged, "last_tick": last_tick}
assert isinstance(out["last_tick"], dict), "last_tick must stay dict"

path = ROOT + "\\results\\autofill_state.json"
crlf = b"\r\n" in raw_ours  # mirror producer format (r223/r234)
with open(path, "wb") as f:
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        txt = txt.replace("\r\n", "\n").replace("\n", "\r\n")
    f.write((txt + "\n").encode("utf-8"))

chk = json.load(open(path, encoding="utf-8"))
ls = chk["launches"]
assert ls == sorted(ls, key=lambda e: e.get("ts", "")), "launches not ascending"
print(f"resolved launches={len(ls)} (ours {len(la_o)} + theirs {len(la_t)} union-dedup) "
      f"last_tick.ts={ts_of(chk['last_tick'])} crlf={crlf}")
