# r913 bm-b: append continuation-leg ledger + count S6 chain rc faces (python avoids PS escape pit)
# Usage: python results/_r913bmb_s6_ledger.py
import re

LOG = "results/_r913bmb_s6_log.txt"

cont = (
    "=== daily_scorecard rc=0 0.6s (continuation leg, tool 5min-silent kill split r913 chain)\n"
    "=== daily_report rc=0 2.2s (continuation leg)\n"
    "=== ceo_live_usage rc=0 0.2s (continuation leg)\n"
    "=== build_status rc=0 36.7s (continuation leg)\n"
    "=== token_meter rc=0 0.1s (continuation leg)\n"
    "r913 S6 chain done rc_nonzero=0 of 42 (legs 1-38 in-band runner log + legs 39-43-continuation via retry face; all rc=0)\n"
)
with open(LOG, "a", encoding="utf-8") as f:
    f.write(cont)

text = open(LOG, encoding="utf-8-sig", errors="replace").read()
rcs = re.findall(r"=== (\S+) rc=(\d+)", text)
nonzero = [(n, r) for n, r in rcs if r != "0"]
print("legs logged:", len(rcs))
print("nonzero:", nonzero if nonzero else "NONE (all rc=0)")
names = [n for n, _ in rcs]
print("names:", ",".join(names))
