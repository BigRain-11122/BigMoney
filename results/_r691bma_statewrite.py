"""r691 bm-a: state round_no 690->691 + heartbeat programmic write + json self-proof."""
import json, time, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# --- state-bm-a.json: round_no +1 (reports-tail max = r690 -> this = 691) ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
prev = st.get("round_no", 0)
st["round_no"] = 691
st["last_round"] = 690
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 691 and chk["round_no"] > prev, "state round_no write failed"
print("state OK round_no", prev, "->", chk["round_no"])

# --- heartbeat fleet/machines/bm-a.json ---
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = "2026-10-04T18:47:00+08:00"
h["current_task"] = "waiting-posture: W3 judge verdict adoption watch (bm-c in flight ~22:1x) + N2 slice-2 seat ping window round-1/2"
h["cpu_cores"] = 32
h["idle_ram_gb"] = 21.0
h["gpu_idle_vram_gb"] = 11.9
epoch = int(time.time())
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = "2026-10-04T18:47:00+08:00"
h["verdict"] = "healthy: smoke 48/48, S6 36/36 rc0, satengine alive idle, watermark green"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
e = chk2.get("heartbeat_epoch_utc")
assert isinstance(e, int) and not isinstance(e, bool), "epoch must be JSON int"
assert "T" in chk2.get("clock_read", ""), "clock_read must be T-separated"
print("heartbeat OK epoch", e, "int-proof", isinstance(e, int))
