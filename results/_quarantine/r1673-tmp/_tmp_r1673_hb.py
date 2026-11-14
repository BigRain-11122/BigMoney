import json, time, sys, os, datetime
sys.path.insert(0, 'Tools')
import heartbeat_write as hw

now = datetime.datetime.now().astimezone()
now = now.replace(microsecond=0)
iso = now.isoformat()
epoch = int(time.time())

try:
    cpu = int(round(float(__import__('subprocess').check_output(
        ['powershell','-NoProfile','-Command',
         "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        creationflags=0x08000000).decode('utf-8','replace').strip())))
except Exception:
    cpu = None

fields = {
 "round_no": 1673,
 "activity": "product",
 "activity_now": "CEO 页新增机队实况节：哪台机自己在写心跳、它管的车道现在谁在跑",
 "activity_now_round": 1673,
 "ts": iso, "clock_read": iso, "last_seen": iso,
 "clock_read_source": "local", "clock_tz": "+08:00",
 "heartbeat_epoch_utc": epoch,
 "ahead_origin": 0, "behind_origin": 0,
 "watermark_verdict": "insufficient_history",
 "verdict": "insufficient_history",
 "chain_verdict": "4/4 rc0 (data_lane_freshness, etf_book_ceo_page, live_book_day_words, live_usage_day_words) + 3/3 rc0 (data_lane_freshness+page+section_bars)",
 "cur_task": "r1673: fleet block on the CEO page, verified and delivered",
 "current_task_short": "CEO page: fleet freshness row",
 "busy": False,
}
if cpu is not None:
    fields["cpu_pct"] = float(cpu)
    fields["cpu_util_pct"] = float(cpu)
    fields["cpu_total_pct"] = float(cpu)
res = hw.write(os.getcwd(), fields)
print("write ->", res)
h = json.load(open(os.path.join("fleet","machines","bm-c.json"), encoding="utf-8"))
print("ts", h.get("ts"), "round_no", h.get("round_no"), "epoch type", type(h.get("heartbeat_epoch_utc")).__name__, "cpu", h.get("cpu_pct"))
s = json.load(open("state-bm-c.json", encoding="utf-8"))
print("state round_no", s.get("round_no"), "epoch type", type(s.get("heartbeat_epoch_utc")).__name__ if "heartbeat_epoch_utc" in s else "n/a")

