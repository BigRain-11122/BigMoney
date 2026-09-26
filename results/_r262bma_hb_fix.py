# _r262bma_hb_fix.py -- R262 S1 smoke F7 red fix: heartbeat clock_read must be
# ISO 8601 "T"-separated (e.g. 2026-09-26T18:01:00+08:00). Root cause: R261 S7
# heartbeat writer emitted space separator "2026-09-26 17:53:59+08:00"; smoke F7
# checks `"T" in clock_read` (R170/R178 family: value AND type must both be right).
# Fix mirrors producer byte faces (R255 five-face probe: BOM/EOL/indent/trailing
# newline; ASCII-only content makes ensure_ascii face byte-neutral).
import json, time, datetime

P = "fleet/machines/bm-a.json"
raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in raw
text = raw.decode("utf-8-sig")
trailing_nl = text.endswith("\n")
indent = None
for line in text.splitlines():
    s = line.lstrip()
    if s.startswith('"') and line != s:
        indent = len(line) - len(s)
        break
print("probe faces:", {"bom": bom, "crlf": crlf, "trailing_nl": trailing_nl, "indent": indent})

hb = json.loads(text)
now = datetime.datetime.now().astimezone()
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")

out = json.dumps(hb, ensure_ascii=False, indent=indent)
if trailing_nl:
    out += "\n"
if crlf:
    out = out.replace("\n", "\r\n")
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as fh:
    fh.write(data)

# self-verify via the same reader smoke uses (utf-8-sig tolerant)
chk = json.load(open(P, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(chk["clock_read"], str) and "T" in chk["clock_read"], "clock_read must be T-separated ISO"
print("fixed:", chk["heartbeat_epoch_utc"], chk["clock_read"])
print("SELFTEST PASS")
