import json
import time
import datetime

P = "fleet/machines/bm-b.json"
raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw
d = json.loads(raw.decode("utf-8"))

epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["machine_id"] = "bm-b"
d["last_seen"] = time.strftime("%Y-%m-%d %H:%M")
d["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (smoke F7)
d["clock_read"] = clock                    # T-04 F5 drift-probe face
d["current_task"] = ("R259 done: T-80 slice-4 capacity face full arc "
                     "AGGR-CAPACITY-FACE-P1 (267/267 units, 9 unconstrained/"
                     "11 constrained, battery byte-frozen, attrition +0) + "
                     "T-82 deep-shard accept-ack replied; next=transfer "
                     "branch fetch+compare, 09-28 new-bar chain")
d["cpu_cores"] = 16
try:
    import psutil
    vm = psutil.virtual_memory()
    d["free_ram_gb"] = round(vm.available / (1024 ** 3), 1)
    d["total_ram_gb"] = round(vm.total / (1024 ** 3), 1)
    d["cpu_util_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    pass
d["round_no"] = 259
d["verdict"] = "GREEN"
# orders_ack regeneration: ALL order files, full names incl .md (r220 law)
import glob
import os
acks = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
d["orders_ack"] = " ".join(acks)
d["n_orders_ack"] = len(acks)

with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)

# self-verify (R170/R178 law: value AND type both checked)
chk = json.loads(open(P, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(
    chk["heartbeat_epoch_utc"])
print("heartbeat epoch:", chk["heartbeat_epoch_utc"], "(int verified)")
print("clock_read:", chk["clock_read"], "| orders_ack:", len(acks))
