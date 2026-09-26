# r284 bm-a T-87 ticket progress write-back (r255/r257 byte-face mirror:
# no BOM / CRLF / trailing newline PRESENT / indent=1 / ensure_ascii face
# probed). Field name = progress_r<writer-round>_<machine> (r262 law).
import json

TP = "fleet/tasks/T-2026-09-26-87-P1.json"
raw = open(TP, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
crlf = b"\r\n" in raw
end_nl = raw.endswith(b"\n")
non_ascii = any(b > 127 for b in raw)
src = raw.decode("utf-8-sig" if bom else "utf-8")
lines = src.split("\r\n" if crlf else "\n")
indent = len(lines[1]) - len(lines[1].lstrip())
d = json.loads(src)

field = "progress_r284_bma"
assert field not in d, "field already present"
d[field] = (
    "T-87 s2 queue #2 CN_SOE_ETF_P1 runner built + pooled (bm-a R284): "
    "scripts/cn_soe_etf_p1.py per frozen prereg ba54b43f -- selftest 34/34 "
    "(r263 law; r286 family legs: np-native coercion + _compute_cells "
    "assembly glue + div-cross dated reconstruction) + real-data gate probe "
    "PASS (T=2445 N=8 == frozen roster, sse_cover 1.0, SOE_HOLD x2 sharpe "
    "0.3915 entries=8 structural, SOE_REPAIR 13 entries 3 episodes "
    "2020-03/2022-04/2022-10, LOWVOL3 30 entries) + pool entry ready "
    "cnsoe-0of1 (workers_plan 4 BelowNormal, F-04 MSG-20260927-0135 "
    "declared R283); autofill tick to burn; next = harvest + prereg s7 "
    "backfill (D6 cross legs vs DIV/TREND) after run lands")

out = json.dumps(d, ensure_ascii=not non_ascii, indent=indent)
if end_nl and not out.endswith("\n"):
    out += "\n"
data = out.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
json.loads(data.decode("utf-8" if not bom else "utf-8-sig"))
with open(TP, "wb") as fh:
    fh.write(data)
print("ticket updated: %s added (indent=%d crlf=%s end_nl=%s "
      "ensure_ascii=%s)" % (field, indent, crlf, end_nl, not non_ascii))
