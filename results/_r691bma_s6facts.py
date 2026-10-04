"""r691 bm-a: extract key S6 log readings to a UTF-8 facts file (console-free per r458)."""
import re, json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
b = open("results/_r691bma_s6_log.txt", "rb").read()
t = b.decode("utf-8", "replace")
facts = {}
for pat in ["consecutive_green", "verdict", "flags", "CALL", "streak", "token", "L2", "zero-drift", "ZERO-DRIFT", "drift"]:
    hits = []
    for m in re.finditer(r"^.*" + pat + r".*$", t, re.M):
        s = m.group(0).strip()
        if len(s) < 250:
            hits.append(s)
    if hits:
        facts[pat] = hits[:6]
json.dump(facts, open("results/_r691bma_s6_facts.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("written", len(facts), "keys")
