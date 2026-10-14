# r977 bm-a estate-absorb closeout: state advance 976->977 + heartbeat + round report line.
# Dead-r977 window estate (close_fds fix x7 + E64 card + P0 CEO report v1 + task lane note)
# verified and absorbed this window; chain products from unparked r976-origin chain (completed
# 08:29:15) ride along. D-19/ORD dual FALSE (dec sha256 86187eff == pin / ord sha1 348eaf34 == pin).
import json
import io
import subprocess
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- live machine stats ----
def cpu_pct():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True, text=True)
    try:
        return round(float(out.stdout.strip()))
    except Exception:
        return -1.0

def free_ram_gb():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except Exception:
        return -1.0

def free_vram_gb():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True)
        return round(float(o.stdout.strip().splitlines()[0]) / 1024.0, 2)
    except Exception:
        return -1.0

CPU = cpu_pct()
RAM = free_ram_gb()
VRAM = free_vram_gb()

# ---- state advance ----
sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
prev_round = st["round_no"]
assert prev_round == 976, prev_round
st["round_no"] = 977
st["last_decisions_seen"] = ("r977: DEC 86187eff UNCHANGED (raw-blob sha256 == watermark pin, zero re-consume)")
st["last_decisions_read_at"] = TS
st["last_orders_seen"] = ("r977: ORD 348eaf34 UNCHANGED (content sha1 == watermark pin, dual FALSE with DEC; "
                          "10-13 rows already consumed by r963-r976 era, zero new BigMoney directives)")
st["last_orders_read_at"] = TS
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state:", prev_round, "->", st["round_no"])

# ---- heartbeat merge ----
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["active"] = "r977 estate-absorb closeout: dead-r977 window products pushed origin (close_fds fix x7 + P0 CEO report v1)"
hb["current"] = "r977 closeout done"
hb["current_task"] = ("r977: dead-window estate absorbed (close_fds=True x7 gates LIVE-applied + E64 card + "
                      "P0-MATRIX-CEO-REPORT-V1.md) + moneyflow gate respawn (+238 then EM conn-block fuse stop, "
                      "checkpoint 2152 preserved, 30-min self-heal) + W238 freeze-prep waits W237 finalize (M12) "
                      "+ T22 next-pointer")
hb["did"] = ("r977: S0 absorb dead r977 estate + verify fix 7/7 zero residue + smoke 49/49 + attrition CLEAN "
             "+ satengine ALIVE idle + D-19/ORD dual FALSE (sha1 method catch: earlier sha256 miscompare corrected) "
             "+ inbox x2 self-pub MSGs processed")
hb["cpu_pct"] = CPU
hb["cpu_load_pct"] = CPU
hb["cpu_total_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["free_ram_gb"] = RAM
hb["free_vram_gb"] = VRAM
hb["gpu_free_vram_gb"] = VRAM
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_seen"] = TS
hb["clock_read"] = TS
hb["ts"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat: epoch", EPOCH, "cpu", CPU, "ram", RAM, "vram", VRAM)

# ---- round report line (root file, fresh-read-append) ----
rp = "round_reports-bm-a.md"
line = (
    f"{TS} | r977 | bm-a | dept:工程/数据-遗产吸收收口 | WM-VERDICT: green (red=false lane=healthy; "
    f"satengine ALIVE queue_depth=0 idle=W238 waits-upstream W237 finalize physical dep M12; "
    f"work_cand buckets 0/0/0/0, next_pick=moneyflow IC batch claimed, blocked on panel) | "
    f"当前活=dead-r977 窗遗产吸收收口 surgical push origin（close_fds=True 修复 7 gate spawner 根因=r976 链 pid130152 "
    f"leg-14 停车+链 08:27 解锁全 38 腿 08:29:15 完成） | "
    f"最近实物=research/P0-MATRIX-CEO-REPORT-V1.md（08:13 白话 CEO 报告 v1·10-16 交期·待 bm-c 会签）+ "
    f"scripts/ 7 件 close_fds=True（08:19·rg 验证 7/7 零残留）+ results/_r977bma_closefds_fix.py+E64 卡 | "
    f"下个里程碑=W238 freeze-prep 同窗触发（W237 finalize 落地即办·bm-c 在烧）；moneyflow 面板 EM 连接级阻断 30min "
    f"自愈至 complete 后 IC 批解锁（O-20261010-1825 §4）·窗=今晚~明晨 | "
    f"孤儿面=1（ComfyUI 空闲服务器误报类 killed=[] 不收编）| 本地未达 origin commit 数=0（surgical push 本窗收口）"
    "\n")
io.open(rp, "a", encoding="utf-8", newline="").write(line)
print("report line appended")
print("DONE r977 closeout bookkeeping")
