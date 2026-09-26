# r234 bm-b bookkeeping (house pattern r76/r92/r93 lineage; R230 indent/EOL law, R170/R178 epoch-int law)
import ctypes
import io
import json
import time

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---- 1. state.json (bm-b: logs/iteration-loop/state.json, indent=1 house format) ----
SP = "logs/iteration-loop/state.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 233, f"unexpected round_no {st['round_no']}"
st["round_no"] = 234
st["did"] = ("r234: maintenance+readiness round (board 23 tickets all claimed, advisory all time-gated; "
             "09-28 Monday new-bar full-chain readiness probe READY 6/6 faces incl. REGIME_GUARD v3 trio "
             "approval+2026-10-01 frozen+regime fresh, paper state 6-trader shape, prospect/aggr/alloc/export/daily-head lanes; "
             "probe schema-mirror self-catch cutoff/date -> data_cutoff/export_date+mtime per r157; "
             "_r234 prefix taken by bm-a R234 x4 -> machine-prefixed _r234bmb_; conflict-resolve skill src==binding SYNC; "
             "T-72 sina first-pull in-flight observation only (bm-a lane); S6 24 legs all green weekend口径)")
with io.open(SP, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---- 2. round report line (append; EOL mirror producer per R230/r223 law) ----
RP = "logs/iteration-loop/round_reports.md"
with io.open(RP, "rb") as fh:
    tail = fh.read()[-400:]
eol = "\r\n" if b"\r\n" in tail else "\n"
line = (
    "[2026-09-26 08:3x | r234 | bm-b OS loop] 水位判定：绿——red=false@08:30:13 lane healthy（next_pick mf-IC "
    "claimed/parked=bm-a 数据面 EM 阻断自愈窗续）；probe 08:33:30 py_low_board_clear=合法 idle 白名单（票 0 open"
    "+bandit 0+池 0 ready+bars 在位）；audit 08:33:24 CLEAN flags=[]（pool_starvation_candidate=true=P1E 车道收线后池空 "
    "supply-gap 面如实非饿）。S0：轮首谶=自家 watchdog tick 漂移两件（autofill_state 08:30 tick+p1d_gates 08:30 再生）"
    "→定向提交 1fb09d51（r213 先例）→fetch 实证 HEAD==origin/main 零新提交免 stash 舞步。S0.5：orders 74/74 轮首扫描零未回执"
    "（差集=README.md 非令件 r220 全名口径）+decisions.md 候选根全缺位诚实 no-op（十二连先例）+P-32 零动作。S1：smoke 25/25。"
    "S2：双板=job_list 空+tasks 23 票全 claimed 零 open。S3 主交付：**09-28 周一新 bar 全链就绪前置探针=READY 六面全绿**"
    "（results/_r234bmb_monday_ready_probe.py+_r234bmb_monday_ready.json；A=REGIME_GUARD v3 三重门批准件在位+"
    "ENFORCE_ACTIVE_FROM 2026-10-01 冻结+regime_state 当日鲜；B=paper state 6 员 open_positions/cost_price shape 全对；"
    "C=prospect 23 件；D=aggr 20+alloc 7 车道在位；E=export 09-24 6 员；F=daily 头 data_cutoff 09-24 当日更新）——探针首版两处 "
    "schema 假读（cutoff/date 臆键名）fail-closed 假红自捕→按 r157 镜像律改真键 data_cutoff/export_date+mtime 判鲜重跑 READY；"
    "r221 撞车律先查 git ls-files=_r234* 前缀已被 bm-a R234 工占 4 件→本机件带机前缀 _r234bmb_。技能维护腿=conflict-resolve "
    "源↔装订 md5 SYNC OK（R219 律）。观察面：T-72 sina 首拉 in-flight（universe 5228·mirror ts 07:40:44·bm-a 车道零触碰）；"
    "moneyflow EM 53/5222 源阻断同域维持；池 42 entries 零 ready/running/waiting。S4：记忆四问门=探针 schema 假读属 r157 "
    "镜像律既有族复用无新维→零 append（r217/r227 先例）。S6：24 腿全 exit 0 周末口径（cutoff 09-24→下 bar 09-28：audit CLEAN/"
    "probe py_low_board_clear/daily 0 新行/regime ORANGE d2 shadow 八连（hs300<MA200+breadth 0.77）/lhb 30min 节流 no-op/"
    "heat 周末 no-op/futures 零网络 no-op/options+mf+ths+ah=bm-a 车道+fp=bm-c 车道 stdout 诚实 no-op/fundamental 11.4h fresh "
    "skip/blf 再生 OK/scorecard 6 员/build_status 432combos 5/7/token delta=0；paper 族七腿无新 bar 合法跳过 r197 先例；月度三件套"
    "非月首轮跳过）。S7：schtasks 双任务健在（IterationLoop 正在运行=本实例/Watchdog 09:00 就绪·R49 口径）+orders 收尾双扫零差集"
    "+state 233→234+心跳 epoch int 自证。下轮指针：①09-28 周一新 bar 全链接续（update_daily→live.paper REGIME_GUARD v3 enforce "
    "日期门→t35verify→t24×2→aggr/alloc→export/scorecard——就绪探针 READY 已背书）②南向 re-probe 白日窗 12:00-13:40（循环自然命中）"
    "③10 月首轮=月度三件套④T-72 sina 首拉完成观察+mf-IC advisory 认领态维持（bm-a 数据面）⑤board/bandit 时间门控候选继续观察"
    "（O-1819 持住）。"
)
with io.open(RP, "a", encoding="utf-8", newline="") as fh:
    fh.write(eol + line + eol)

# ---- 3. heartbeat (bm-b.json, indent=2 house format, epoch int law) ----
class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = MS(); ms.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
free_ram_gb = round(ms.ullAvailPhys / 1073741824, 1)
gpu_free = None
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                           "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    tot, used = [float(x) for x in out.stdout.strip().split(",")]
    gpu_free = round((tot - used) / 1024.0, 1)
except Exception:
    gpu_free = None

HP = "fleet/machines/bm-b.json"
d = json.load(open(HP, encoding="utf-8-sig"))
ack_before = d.get("orders_ack")
assert isinstance(ack_before, str) and ack_before, "orders_ack must be non-empty string (r33 pit)"
d["last_seen"] = now_iso
d["current_task"] = ("r234 done: maintenance+readiness round (09-28 Monday new-bar chain readiness probe READY "
                     "6/6 faces: REGIME_GUARD v3 trio/paper-state shape/prospect+aggr+alloc+export+daily-head; "
                     "board 23 all claimed, advisory time-gated; S6 24 legs green weekend); "
                     "southbound daylight window 12:00-13:40; 09-28 Monday chain probe-backed")
d["round_no"] = 234
d["cores"] = 16
d["free_ram_gb"] = free_ram_gb
d["gpu_free_vram_gb"] = gpu_free
d["verdict"] = "healthy"
d["heartbeat_epoch_utc"] = int(time.time())
d["clock_read"] = now_iso
assert d["orders_ack"] == ack_before
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch must be python int (R170/R178 double-violation law)"
with io.open(HP, "w", encoding="utf-8", newline="") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)

# ---- 4. self-verify (all three files json.loads + epoch type re-read) ----
for p in (SP, HP):
    json.load(open(p, encoding="utf-8-sig"))
hb = json.load(open(HP, encoding="utf-8-sig"))
assert hb["round_no"] == 234 and isinstance(hb["heartbeat_epoch_utc"], int)
print(f"bookkeeping ok | state r{st['round_no']} | freeRAM={free_ram_gb}GB gpuFree={gpu_free}GB "
      f"epoch={hb['heartbeat_epoch_utc']} (int) | report eol={'CRLF' if eol == chr(13)+chr(10) else 'LF'}")
