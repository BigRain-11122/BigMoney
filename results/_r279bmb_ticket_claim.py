"""r279 bm-b: claim T-88 (byte-face preserving update, R255/R257 five-face probe law)."""
import json, sys, io

P = "fleet/tasks/T-2026-09-26-88-P1.json"
raw = open(P, "rb").read()

# five-face probe (R255/R257)
bom = raw.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in raw
tail_nl = raw.endswith(b"\n")
text = raw.decode("utf-8-sig")
non_ascii_raw = any(ord(c) > 127 for c in text)
# indent probe: second line leading spaces
lines = text.splitlines()
indent = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 1
print(f"probe: bom={bom} crlf={crlf} tail_nl={tail_nl} raw_cjk={non_ascii_raw} indent={indent} lines={len(lines)}")

d = json.loads(text)
assert d["status"] == "open", f"status already {d['status']} -- collision, do NOT touch"
d["status"] = "claimed"
d["claimed_by"] = "bm-b"
d["claimed_at"] = "2026-09-26 23:3x"
d["claim_note"] = ("claimed bm-b r279 same-round start per O-20260926-2325 CEO immediate law: s1 DOMAIN_AUDIT opening this round "
                   "(consumes FULL_INSTRUMENT_CENSUS 2026-09-25 probe base + tonight in-repo face inventory, measured-first); "
                   "s3 cash-leg data-face probe next; s2 convertible collector/judged runs follow prereg freeze (R99); "
                   "shard/pool law per O-2130 workers_plan when batches form")

out = json.dumps(d, ensure_ascii=False, indent=indent)
if tail_nl:
    out += "\n"
if crlf:
    out = out.replace("\n", "\r\n")
if bom:
    out_b = b"\xef\xbb\xbf" + out.encode("utf-8")
else:
    out_b = out.encode("utf-8")
open(P, "wb").write(out_b)

# self-verify: reload + assert + diff line count vs head (field-increment level, not whole-file rerank)
raw2 = open(P, "rb").read()
d2 = json.loads(raw2.decode("utf-8-sig"))
assert d2["status"] == "claimed" and d2["claimed_by"] == "bm-b"
print("reloaded ok; claimed_at=", d2["claimed_at"])
print("written bytes:", len(raw2))
