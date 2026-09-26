"""r295 bm-b: surgically remove the phantom CN_TREND_ETF_P1 attrition row
(ts 2026-09-27 03:42:52, ledger_total_after 209432) -- the bookkeeping face of
the losing-side double finalize (r288 adjudication did not kill the local burn;
it re-appended +2,007 already counted by bm-a's canonical 03:27:59 row).

Byte-surgical: json.JSONDecoder.raw_decode for exact object bounds; removes the
entry together with its preceding newline and trailing comma so the remaining
bytes are unchanged. Assertions: exactly 1 entry removed, canonical row kept,
'209432' absent afterwards, full-file JSON still parses.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "results", "gate_attrition.json")

raw_bytes = open(PATH, "rb").read()
bom = raw_bytes.startswith(b"\xef\xbb\xbf")
raw = raw_bytes.decode("utf-8-sig" if bom else "utf-8")

anchor = '"ts": "2026-09-27 03:42:52"'
i = raw.find(anchor)
assert i >= 0, "phantom row anchor not found"
start = raw.rfind("{", 0, i)
assert start >= 0, "entry opening brace not found"
obj, end = json.JSONDecoder().raw_decode(raw, start)
assert obj.get("batch") == "CN_TREND_ETF_P1" and obj.get("ledger_total_after") == 209432, \
    "decoded entry is not the phantom row: %r" % (obj.get("batch"), obj.get("ledger_total_after"))

if raw[end + 1] == ",":
    # mid-list entry: drop it together with its preceding newline
    start_nl = raw.rfind("\n", 0, start)
    assert start_nl >= 0
    new = raw[:start_nl] + raw[end + 2:]
else:
    # last entry: drop it together with the preceding entry's trailing comma
    comma = raw.rfind(",", 0, start)
    assert comma >= 0, "no preceding comma for last-entry removal"
    new = raw[:comma] + raw[end + 1:]

parsed = json.loads(new)
entries = parsed["entries"]
assert "209432" not in new, "209432 still present after removal"
kept = [e for e in entries if e.get("batch") == "CN_TREND_ETF_P1"]
assert len(kept) == 1 and kept[0].get("ledger_total_after") == 207425, \
    "canonical row 53 not intact: %r" % (kept,)
print("entries: %d -> %d" % (len(entries) + 1, len(entries)))
print("kept canonical row: ts=%s ledger=%s" % (kept[0].get("ts"), kept[0].get("ledger_total_after")))

out = new.encode("utf-8")
if bom:
    out = b"\xef\xbb\xbf" + out
with open(PATH, "wb") as fh:
    fh.write(out)
print("OK: phantom attrition row removed, byte-surgical, file rewritten")
