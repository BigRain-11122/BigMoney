# r628 bm-a: append settle-bug P0 fix entry to research/pit-pool.md
# (domain canon direct-write, r401/r417 bm-c precedent) with byte
# accounting header line. Byte-level discipline per pool-file edit law.
import datetime
import hashlib
import sys

P = "research/pit-pool.md"
raw = open(P, "rb").read()
assert raw.endswith(b"\n"), "file must end with newline (LF face)"

now = datetime.datetime.now()
tlabel = f"{now.hour:02d}:{now.minute // 10}x"

entry = (
    "- [2026-10-03 " + tlabel + " r628 bm-a] settle \u5199\u8def origin-tip \u8eab\u4efd\u65ad\u8a00\u843d\u5730"
    "\uff08r627 stale-settle P0 \u4fee\u590d\u4ef6\u00b7MSG-0612 \u65cf\u6839\u6cbb\u9762\uff09\uff1a"
    "sync_face\uff08\u552f\u4e00 settle \u5199\u8005\u00b7compute_audit S6 \u817f\u8c03\u7528\uff09\u6b64\u524d\u76f2\u5199\u5de5\u4f5c\u6811\u9762\u2014\u2014"
    "reland \u7a97 reset/checkout \u5e8f\u5217\u628a\u5de5\u4f5c\u6811 runnable_pool \u56de\u6eda\u5230\u9648\u65e7\u57fa\uff0814:41:08\uff09"
    "\u800c\u672c\u673a daemon \u5df2\u63a8\u9c9c claim\uff0814:54:07 c407bd9a8\uff09\u4e0a origin\uff0c"
    "settle \u7167\u65e7\u5e76=\u9c9c\u503c\u56de\u9000\u7834\u63a5\u7ba1\u95e8\uff08r627 \u5b9e\u5f39\u00b7heal 218d194a5 \u53cc\u9762\u4ece origin daemon \u771f\u503c\u6062\u590d\uff09\u3002"
    "\u4fee\u6cd5=settle \u5199\u524d _origin_shared_blob \u63a2\u9488\u8bfb\u672c\u5730 origin/main remote-tracking ref \u7684\u5171\u4eab\u9762 blob"
    "\uff08\u96f6\u7f51\u7edc\u00b7daemon push \u5373\u63a8\u8fdb\u672c\u5730 ref \u4e0e\u5de5\u4f5c\u6811\u56de\u6eda\u65e0\u5173\uff09\uff1a"
    "\u8eab\u4efd\u6052\u7b49\u2192\u65e7\u6cd5\u76f4\u901a\uff1b\u5931\u914d\u2192origin blob \u4f5c leading base source \u5e76\u5165 union"
    "\uff08newer-wins r311+marker \u5f8b\u4fdd daemon \u771f\u503c\uff09\uff1b\u6d3b ref \u4e0a\u63a2\u9488 fault\u2192fail-closed \u53cc\u9762\u96f6\u5199\u3002"
    "selftest 4 \u817f\u65b0\u589e\uff08r627 \u5b9e\u5f39\u5f62\u6001\u56de\u5f52\u817f 14:54:07 \u4fdd\u7559\u65ad\u8a00+\u8eab\u4efd\u6052\u7b49+hermetic no-origin+fault fail-closed\uff09\u3002"
    "How to apply\uff1a\u4e00\u5207\u300c\u4ece\u5de5\u4f5c\u6811\u8bfb\u5171\u4eab\u6d3b\u5199\u9762\u518d\u5199\u56de\u300d\u7684 settle/derive \u5199\u8def\uff08\u672c\u4ef6 sync_face \u65cf\uff09"
    "\u4e00\u5f8b\u5148\u8fc7 origin-tip \u8eab\u4efd\u63a2\u9488\uff1b\u8bca\u65ad\u300csettle \u540e\u65f6\u95f4\u6233\u56de\u9000\u300d\u5148\u7591 reland \u7a97\u5de5\u4f5c\u6811\u9648\u65e7\u9762\u52ff\u7591 daemon\u3002\n"
)
block = entry.encode("utf-8")
assert b"\r" not in block, "entry must be LF-only"
digest = hashlib.md5(block).hexdigest()
hdr = (
    "> \u76f4\u5199\u884c\uff08r628 bm-a\u00b7settle-bug P0 \u4fee\u590d\u4ef6\u843d\u4ef6\uff09\uff1a"
    "r627 stale-settle \u5b9e\u5f39\u4fee\u590d\u6761 1 \u6761\u76f4\u5165\u672c\u4ef6"
    "\uff08\u975e\u8fc1\u79fb\u00b7\u57df\u5185 direct-write\u00b7r401/r417 \u8303\u5f0f\uff09"
    "\u00b7\u8ffd\u52a0\u6838 " + str(len(block)) + " B\uff08LF blob \u9762\u00b7md5=" + digest + "\uff09\u3002\n"
)
hdr_block = hdr.encode("utf-8")
assert b"\r" not in hdr_block

lines = raw.split(b"\n")
# last header "> " line index (header block sits before first entry)
last_hdr = max(i for i, l in enumerate(lines) if l.startswith(b"> "))
first_entry = next(i for i, l in enumerate(lines) if l.startswith(b"- ["))
assert last_hdr < first_entry, "header block must precede entries"

new = b"\n".join(lines[:last_hdr + 1]) + b"\n" + hdr_block + \
    b"\n".join(lines[last_hdr + 1:])
if not new.endswith(b"\n"):
    new += b"\n"
new += block

open(P, "wb").write(new)

# verification pass: re-read, assert entry present + byte delta
raw2 = open(P, "rb").read()
assert raw2 == new
assert raw2.endswith(block), "entry must be the tail block"
delta = len(raw2) - len(raw)
assert delta == len(block) + len(hdr_block), (delta, len(block), len(hdr_block))
n_entries_before = sum(1 for l in lines if l.startswith(b"- ["))
n_entries_after = sum(1 for l in raw2.split(b"\n") if l.startswith(b"- ["))
assert n_entries_after == n_entries_before + 1
print(f"OK appended {len(block)}B entry (md5={digest}) + {len(hdr_block)}B "
      f"header line; entries {n_entries_before}->{n_entries_after}; "
      f"file {len(raw)}->{len(raw2)}B")
