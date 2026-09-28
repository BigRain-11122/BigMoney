"""r367 corrective: heal x2_watch_log.jsonl \r\r\n -> \r\n (wave-1 resolver join bug; content union already correct 1146 unique lines)."""
b = open("results/x2_watch_log.jsonl","rb").read()
def _strip(l):
    while l.endswith(b"\r"): l = l[:-1]
    return l
lines = [_strip(l) for l in b.split(b"\n") if l.strip()]
uniq = len(set(lines))
out = b"\r\n".join(lines) + (b"\r\n" if b.endswith(b"\n") else b"")
open("results/x2_watch_log.jsonl","wb").write(out)
nb = open("results/x2_watch_log.jsonl","rb").read()
assert nb.count(b"\r\r")==0 and nb.count(b"\r\n")==len(lines)==1146, "heal failed"
import json
for l in nb.decode("utf-8").splitlines():
    if l.strip(): json.loads(l)
print("x2 healed: %d lines, %d unique, terminators CRLF x%d, zero CRCR" % (len(lines), uniq, nb.count(b"\r\n")))
