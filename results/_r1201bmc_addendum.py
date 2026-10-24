"""r1201 addendum row: verifications run after the closeout commit (smoke/attrition/orphan/D-19/orders)."""
import json
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ROOT = "K:/Fluxgroup/FluxGroup/quant/bigmoney"

row = (
    f"| {ts} | r1201 addendum | verifications run post-closeout in the same window: S1 smoke 57/57 PASS; "
    "attrition guard 4 ledgers CLEAN (3 historical shrinks healed); round-zero orphan probe py_faces=7 orphans=0 "
    "resident_servers=1 killed=[]; D-19 watermark probe compare_mode=triple and BOTH digests unchanged "
    "(dec 3cfdec0c0a664129 / ord 8ff7de47df154ffa) => zero decision rows owed; orders difference set 109 files / "
    "234 acks / unacked=0; 30 dirty faces at round open were the dead window's S6-regenerated artifacts -> discarded "
    "per r1158 (chain not re-run this window, it runs next window). "
    "PIT (new): the finalize receipt keeps its anchors under science_gates.ledger.total and "
    "null_pool_cumulative.merged.n_values -- not at the top level; a closeout script that guesses top-level keys "
    "asserts None and dies after the row text is composed. Also: results/_r*.json receipts are gitignored, so "
    "receipt evidence must be staged with `git add -f`. | next = r1202 W312 prereg derive + five-face splice\r\n"
)

with open(f"{ROOT}/round_reports-bm-c.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(row)

hp = f"{ROOT}/fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["current"] = (
    "W311 CLOSED + pushed (finalize 1,108,541 / K=682,120; fivekeys 6/6; sixgate 74th ALL PASS); "
    "W312 seat ADMIT published; next = W312 prereg freeze + splice"
)
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)

chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("ADDENDUM OK", ts)