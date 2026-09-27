"""R304 tail: O-20260927-0809 ack (S7 second-scan catch) + receipt line.
GM session executed the canon/spec faces itself (per order sec.3 本会话亲执,
evidence MSG-0814 ruling -> bm-b T-90 owner); bm-a OS-loop duty = ack +
zero-parallel-start (already honored)."""
import json
import os
import time
from datetime import datetime

iso = datetime.now().astimezone().isoformat()
epoch = int(time.time())
BID = "O-20260927-0809-bm-a"

hp = os.path.join("fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
acked = [t for t in (hb.get("orders_ack") or "").split() if t]
if BID not in acked:
    acked.append(BID)
hb["orders_ack"] = " ".join(acked)
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
json.dump(hb, open(hp + ".tmp", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
os.replace(hp + ".tmp", hp)

rp = os.path.join("logs", "iteration-loop", "round_reports-bm-a.md")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(
        f"{iso} | R304 bm-a TAIL: S7 second-scan caught mid-round CEO order "
        "O-20260927-0809 (chain large-scale backtest + iteration law, "
        "O-0758 scale-up) -- RECEIPT: order sec.3 assigns canon/spec "
        "execution to the GM session itself (done: DECISION_CHAIN v1.1 "
        "iteration law + T-90 spec full-grid upgrade + version ledger, "
        "MSG-0814 ruling handed to bm-b as T-90 owner for v1.1 prereg "
        "refreeze first action); bm-a OS-loop lane = ack + zero-parallel "
        "(CN_MKTNEUTRAL lane untouched, T-90 still bm-b owner per sec.4 "
        "yield) -- no parallel start, no re-draft; ack 97->98\n")

# self-verify gate (r302/R170 laws)
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int)
assert "T" in h2["clock_read"] and "+08:00" in h2["clock_read"]
assert BID in h2["orders_ack"].split()
print("ack ok:", BID, "| acks:", len(h2["orders_ack"].split()),
      "| epoch:", epoch)
