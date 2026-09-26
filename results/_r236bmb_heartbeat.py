import io, json, time, os, datetime

# ---- heartbeat bm-b ----
p = r"fleet/machines/bm-b.json"
h = json.load(open(p, encoding="utf-8-sig"))
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
h["last_seen"] = now
h["heartbeat_epoch_utc"] = epoch  # int, R170/R178 law
h["clock_read"] = datetime.datetime.now().astimezone().isoformat()
h["current_task"] = (
    "r236 done: board-clear maintenance + O-2115 registry row reconciled to d2 truth "
    "(3/4 delivered sub-items unmasked, genuine gap = cross-machine LLM re-review protocol dormant)"
)
h["round_no"] = 236
h["verdict"] = "py_low_board_clear legal idle (board 0 open + bandit 0 + pool 0 ready supply-gap, not violation)"
import psutil
h["cpu_util_pct"] = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["idle_ram_gb"] = round(vm.available / 1e9, 1)
h["idle_ram_mb"] = int(vm.available / 1e6)
try:
    import GPUtil
    g = GPUtil.getGPUs()[0]
    h["gpu_free_vram_gb"] = round((g.memoryTotal - g.memoryUsed) / 1024, 1)
    h["gpu_free_vram_mb"] = int((g.memoryTotal - g.memoryUsed))
    h["gpu_idle_vram_mb"] = int((g.memoryTotal - g.memoryUsed))
except Exception:
    pass
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    txt = json.dumps(h, ensure_ascii=False, indent=1)
    if crlf:
        txt = txt.replace("\n", "\r\n")
    fh.write(txt)
# self-verify epoch int (smoke F7 contract)
chk = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat ok:", chk["last_seen"], "epoch int:", chk["heartbeat_epoch_utc"])

# ---- orders double-scan (S7 re-scan) ----
ack = set(json.load(open(p, encoding="utf-8-sig"))["orders_ack"].split())
orders = set(f for f in os.listdir("fleet/orders") if f.startswith("O-") and f.endswith(".md"))
diff = sorted(orders - ack)
print("orders re-scan unacked:", diff if diff else "0 (all acked)")

# ---- inbox re-check ----
inbox = os.listdir("fleet/inbox") if os.path.isdir("fleet/inbox") else []
print("inbox unread:", inbox if inbox else "empty")
