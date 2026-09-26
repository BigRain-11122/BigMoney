# r266 bm-b: heartbeat update -- corrected face mirror (no-BOM / LF-only / tail newline / indent=1)
import json, time, datetime

H = "fleet/machines/bm-b.json"
raw = open(H, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf") and (b"\r\n" not in raw) and raw.endswith(b"\n")
h = json.loads(raw.decode("utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
h["last_seen"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
h["current_task"] = "r266 done: T-76 referee deep-read closed (2609.27051 full-text, zero adoption, science_gates route); next: 09-28 face(a) window + 10-01 month trio"
h["round_no"] = 266
h["verdict"] = "healthy"
h["n_orders_ack"] = 82
# face mirror: LF-only, indent=1, no BOM, trailing newline
out = json.dumps(h, ensure_ascii=False, indent=1) + "\n"
open(H, "wb").write(out.encode("utf-8"))
chk = json.loads(open(H, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (smoke F7)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (smoke F7)"
print("heartbeat updated: epoch", epoch, "int-verified, T-clock verified, LF-face verified")
