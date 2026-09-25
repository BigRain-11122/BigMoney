# -*- coding: utf-8 -*-
"""R218 closeout: state round_no++ + heartbeat refresh (epoch MUST be JSON int, self-verified)."""
import io, json, subprocess, time
from datetime import datetime

now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json ---
sp = "state-bm-a.json"
state = json.load(io.open(sp, encoding="utf-8-sig"))
prev_ts = state.get("ts", "")
state["round_no"] = 218
state["did"] = ("R218: P-20260926-01 集团技能动员令回执全弧 (盘点/三问筛/建装/README 登记) = bigmoney-conflict-resolve "
                "技能建成 (SKILL.md 10 形态配方表 r161~r220 坑律族+classify_conflicts.py selftest 16/16·官方 "
                "package_skill 验证过·workspace 已装) + IntradayMarks STALE 自查=周末假阳性任务健康 (F-20260926-03 "
                "建议行) + T-72 s2 巡逻健康 (130/5228 in flight) + S6 20 腿全绿")
state["verdict"] = "GREEN"
state["next"] = ("T-72 s2 patrol: first-pull in flight (ETA ~08:35; on completion = acceptance derive coverage>=5000/5222 "
                 "+ law-zero-violation + idempotency rerun + num ceiling probe freeze + request budget account; s3 = S6 "
                 "wiring after s2); 09-28 Monday new-bar full chain relay; mf/AH EM-block self-heal windows; bm-c "
                 "rebuild-or-retire 09-26 11:52 GM face; 10-01 monthly trio + REGIME_GUARD v3 date gate; T-70 midterm 10-09")
state["last_round_ts"] = prev_ts
state["ts"] = now_iso
state["updated_at"] = now_iso
state["current_task"] = ("r218 done: skills mobilization receipt delivered (bigmoney-conflict-resolve built+installed, "
                         "P-20260926-01 in this commit); next: T-72 s2 acceptance derive on completion / 09-28 new-bar relay")
state["last_run"] = now_iso
state["last_round_at"] = now_iso
io.open(sp, "w", encoding="utf-8", newline="").write(json.dumps(state, ensure_ascii=False, indent=1) + "\n")

# --- fleet/machines/bm-a.json (heartbeat, own file only) ---
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8-sig"))
hb["last_seen"] = now_iso
hb["current_task"] = state["current_task"]
try:
    import psutil
    hb["cpu_cores"] = psutil.cpu_count(logical=True)
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    hb["free_ram_gb"] = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass  # keep previous sample on psutil failure
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    if out:
        hb["gpu_free_vram_gb"] = round(float(out[0]) / 1024, 1)
except Exception:
    pass
hb["verdict"] = "GREEN"
hb["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178 law)
hb["clock_read"] = now_iso                  # local clock ISO incl UTC offset (T-04 F5)
io.open(hp, "w", encoding="utf-8", newline="").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# --- self-verify: epoch int + parse-back ---
chk = json.load(io.open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(json.loads(json.dumps(chk["heartbeat_epoch_utc"])), int)
print("state round_no ->", state["round_no"])
print("heartbeat epoch ->", chk["heartbeat_epoch_utc"], "(int verified), clock_read ->", chk["clock_read"])
