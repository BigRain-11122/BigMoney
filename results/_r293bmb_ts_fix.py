# -*- coding: utf-8 -*-
"""r293 fix: R271 timestamp-family law self-catch -- hardcoded future 03:52:00 -> true clock, cpu re-sample."""
import json, datetime

now = datetime.datetime.now().astimezone()
ts_plain = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.isoformat()
print("true clock:", ts_plain)

# 1) round_reports.md line timestamp fix (the r293 line just appended)
p = "logs/iteration-loop/round_reports.md"
t = open(p, encoding="utf-8").read()
bad = "2026-09-27T03:52:00 | r293 bm-b |"
good = "%s | r293 bm-b |" % now.strftime("%Y-%m-%dT%H:%M:%S")
assert t.count(bad) == 1, "r293 line anchor not unique/found: %d" % t.count(bad)
open(p, "w", encoding="utf-8", newline="").write(t.replace(bad, good))
print("report line ts fixed ->", good)

# 2) state.json ts fields fix
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["last_round_ts"] = ts_plain; st["updated_at"] = ts_plain; st["ts"] = ts_plain
st["last_seen"] = ts_iso.split(".")[0] + ("+08:00" if now.utcoffset() is None else now.strftime("%z")[:5] and "")
st["last_seen"] = now.isoformat()
st["last_run"] = "r293 " + ts_iso
st["last_round_at"] = ts_iso
st["updated"] = ts_plain
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state ts fixed")

# 3) heartbeat cpu re-sample via psutil + clock sync
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    vm = psutil.virtual_memory()
    ram_gb = round(vm.available / (1024**3), 1)
except Exception as e:
    print("psutil fail:", e); cpu = None; ram_gb = None
hp = "fleet/machines/bm-b.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["clock_read"] = ts_iso
hb["heartbeat_epoch_utc"] = int(now.timestamp())
if cpu is not None:
    hb["cpu_util_pct"] = round(cpu); hb["cpu_pct"] = round(cpu)
if ram_gb is not None:
    hb["free_ram_gb"] = ram_gb; hb["idle_ram_gb"] = ram_gb
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat: cpu=%s ram=%s epoch=%d clock=%s" % (cpu, ram_gb, chk["heartbeat_epoch_utc"], chk["clock_read"]))
