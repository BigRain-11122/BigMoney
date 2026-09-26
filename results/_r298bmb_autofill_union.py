"""r298 bm-b autostash recovery union: results/autofill_state.json (mixed-dict+ledger
recipe, r203/R208/r215/r220/r245). The rebase --quit converted the pull autostash
into stash@{0}; its snapshot holds the local autofill watchdog's live face
(bm-b tick ledger incl. 04:40:01 claim + 04:50:01 claim_lost_yield for
CN-KLINE-PATTERN-P1 run-0of1). Current worktree file = upstream e0fed5e9 face
(bm-a 04:40:01 tick). Union both zero-loss: launches = |A union B| by canonical
row identity -> ts desc cap 50 (producer semantics) -> re-sort ts asc for
write-back; last_tick = internal-ts compare take-newer (same-second tie -> HEAD
/current side, r140), dict-assert; byte-mirror newline+indent from current blob.
"""
import io
import json

CUR = "results/autofill_state.json"
SNAP = r"C:\Users\Administrator\AppData\Local\Temp\r298bmb_autostash_snapshot.json"


def cano(r):
    return json.dumps(r, ensure_ascii=False, sort_keys=True)


cur_raw = open(CUR, "rb").read()
snap_raw = open(SNAP, "rb").read()
cur = json.loads(cur_raw.decode("utf-8-sig"))
snap = json.loads(snap_raw.decode("utf-8-sig"))

lc, ls = cur.get("launches") or [], snap.get("launches") or []
union = {cano(r): r for r in lc}
union.update({cano(r): r for r in ls})          # snapshot rows win on identical canon
rows = list(union.values())
n_union = len(rows)
rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
rows = rows[:50]                                # cap = keep newest 50 (producer law)
rows.sort(key=lambda r: r.get("ts", ""))        # write-back order = ts asc (r245)

tc = (cur.get("last_tick") or {}).get("ts", "")
ts_ = (snap.get("last_tick") or {}).get("ts", "")
# internal ts compare (r140: no str() compare for ordering decisions beyond iso
# string which IS the internal format); same-second tie -> HEAD (current side)
last_tick = snap.get("last_tick") if ts_ > tc else cur.get("last_tick")
assert isinstance(last_tick, dict), type(last_tick)

merged = {"last_tick": last_tick, "launches": rows}
indent = 1
head = cur_raw.decode("utf-8-sig").splitlines()
for line in head[1:6]:
    st = line[: len(line) - len(line.lstrip())]
    if st.strip() == "" and st:
        indent = len(st)
        break
crlf = b"\r\n" in cur_raw[:2000]
text = json.dumps(merged, ensure_ascii=False, indent=indent)
if cur_raw.endswith(b"}\n") or cur_raw.endswith(b"}\r\n"):
    text += "\n"
data = text.encode("utf-8")
if crlf:
    data = text.replace("\n", "\r\n").encode("utf-8")

with io.open(CUR, "wb") as f:
    f.write(data)

chk = json.load(io.open(CUR, encoding="utf-8-sig"))
assert isinstance(chk["last_tick"], dict)
assert len(chk["launches"]) == len(rows)
assert cano(chk["last_tick"]) == cano(last_tick)
print("autofill_state union: cur %d + snap %d rows -> |union| %d -> cap50 write %d; "
      "last_tick ts=%s (cur %s / snap %s); crlf=%s indent=%d"
      % (len(lc), len(ls), n_union, len(rows), last_tick.get("ts"), tc, ts_,
         crlf, indent))
