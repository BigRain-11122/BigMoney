# R279 bm-a orders_ack registration for O-2330/O-2335 (dead-R278 pre-decease duty, kill-insurance early write)
# r220 law: ack tokens = FULL filenames incl .md; single-writer: bm-a writes only fleet/machines/bm-a.json
# Byte-face mirror law (R255/R257 five faces): probe BOM/EOL/ensure_ascii/indent/trailing-newline before write.
import json
import time
import sys

PATH = "fleet/machines/bm-a.json"
NEW = ["O-20260926-2330-bm-a.md", "O-2026-09-26-2335-bm-a.md"]

raw = open(PATH, "rb").read()
face = {
    "bom": raw.startswith(b"\xef\xbb\xbf"),
    "crlf": b"\r\n" in raw,
    "ends_nl": raw.endswith(b"\n"),
}
head = raw[:400].decode("utf-8-sig", "replace")
lines = head.splitlines()
indent = 1
for ln in lines:
    if ln.startswith("  ") or ln.startswith("\t"):
        indent = 2 if ln.startswith("  ") else 1
        break
    if ln.startswith(" "):
        indent = len(ln) - len(ln.lstrip(" "))
        break

d = json.loads(raw.decode("utf-8-sig"))
ack_field = d.get("orders_ack")
assert isinstance(ack_field, str), "orders_ack must be space-joined string (r123 law)"
ack = ack_field.split()  # r123: split, never per-char iterate
for t in NEW:
    if t not in ack:
        ack.append(t)
d["orders_ack"] = " ".join(ack)
d["last_seen"] = "2026-09-27T00:0x"
d["heartbeat_epoch_utc"] = int(time.time())
d["clock_read"] = __import__("datetime").datetime.now().astimezone().isoformat()
assert isinstance(d["heartbeat_epoch_utc"], int)

body = json.dumps(d, ensure_ascii=False, indent=indent)
if face["crlf"]:
    body = body.replace("\n", "\r\n")
if face["ends_nl"]:
    body += "\n"
out = ("\ufeff" + body).encode("utf-8") if face["bom"] else body.encode("utf-8")
open(PATH, "wb").write(out)

d2 = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert isinstance(d2["heartbeat_epoch_utc"], int)
missing = [t for t in NEW if t not in d2["orders_ack"].split()]
assert not missing, missing
print(f"ack registered: {len(d2['orders_ack'].split())} tokens; new={NEW}; face={face} indent={indent} epoch_int={d2['heartbeat_epoch_utc']}")
sys.exit(0)
