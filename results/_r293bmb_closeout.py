# -*- coding: utf-8 -*-
"""r293 bm-b closeout: round-report line + state.json round_no + heartbeat fields."""
import json, time, datetime, platform, subprocess, os

REPORT_LINE = (
    "2026-09-27T03:52:00 | r293 bm-b | dept:工程+舰队 | verdict: GREEN "
    "(WM 03:43:18 probe red=false lane=healthy·py 3.5% 周末合法 idle：板 0 open/池 54/54 done/bandit 0/"
    "供给 T-87 in-flight=算力外物理道；smoke 25/25；orders 91/91 轮首+收尾双扫零未回执) | "
    "did: S0 轮首脏（autofill 自有 3 件）阻塞 rebase→stash→pull fast-forward 7a021395→37487c72"
    "（bm-a R290-291：CN-TREND-ETF-P1 judged-negative 收割+CENSUS done-flip 补翻+post_review 5 热锚迁移）"
    "→pop 双 UU 正典解：autofill_state=mixed-dict 配方（launches union 50|50→cap50 ASC r245"
    "+last_tick 03:40:01>03:30:01 取新 r140+CRLF r223+解后显式 drop r291 律）"
    "+runnable_pool=UNKNOWN 手工定性（entry-id 集 54=54 相等+diff 仅 2 条 ready→done 时间演化"
    "=旧中间态⊂HEAD 新面→take-ours 整面零丢失·r290 pool-upstream-base 判别式补全）"
    "resolver _r293bmb_resolve.py 留痕+json parse 门全过 | "
    "S0.5: orders 91/91+decisions/集团直扫面 bm-b 不可达如实注记（R291 律·镜面 91/91 零缺口）| "
    "S1 smoke 25/25 | S2: job_list 0+板 30 票全 claimed+水位绿 | "
    "S3: post_review 今日两 NO（03:18 T-86-S3 dotted-key/03:35 T-86-S2 hot 锚）核=已被 bm-a 03:35/03:36 derive "
    "NO→YES 合法翻绿零 P0；队列点名项全闭合或 gated（Optuna 6<8 冻结/J13=bm-a 车道/J10/J18b 已交付/"
    "town r292 已对齐/J12 v0.7+ 反重复禁堆）→诚实维护轮 | "
    "S6: 30/30 legs rc=0（中秋+周末诚实 no-op 族+audit CLEAN+T-87 gate lock alive）| "
    "T-87 供给复探（r292 指针#2 兑现）: 2985/5228=57.1% @12.65/min·pid 29440 3.9h 龄"
    "·attempts 7 股零熔断零隔离·ETA ~06:41（与 r292 ETA~06:40 吻合）| "
    "S4: CODELY 坑律 append 7.3→7.9KB<10KB 硬线 | "
    "验证: resolver json parse 断言全过+双 UU 解后树净+orders 双扫零未回执 | "
    "下轮: T-87 pass-completion ~06:41 后复探（gate 自动探·面板 complete 翻面=bm-a wave-2 解锁）；"
    "09-28 周一开市新 bar 全链接力；迁移窗 v2.2 armed 至 09-29 12:00（执行器域勿动）"
)

# --- 1) round report line append (LF, file is LF-only per prior probes)
p = "logs/iteration-loop/round_reports.md"
with open(p, "a", encoding="utf-8", newline="") as f:
    f.write(REPORT_LINE + "\n")
print("report line appended, bytes:", len(REPORT_LINE.encode("utf-8")))

# --- 2) state.json round_no 292->293
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 293
st["did"] = ("r293: S0 dual-UU canonical resolve (autofill_state mixed-dict + runnable_pool take-ours "
             "subset-evolution) + S6 30/30 legs rc=0 + T-87 supply re-probe 2985/5228 ETA~06:41 "
             "+ orders 91/91 double-scan zero unacked")
st["verdict"] = "green maintenance round ok (board closed, pool 54/54 done, T-87 refresh in-flight)"
st["next"] = ("T-87 pass-completion re-probe after ~06:41 (gate auto; panel complete=bm-a wave-2 unlock); "
              "09-28 Mon open new-bar full-chain relay; migration window v2.2 armed to 09-29 12:00")
ts = "2026-09-27 03:52:00"
st["last_round_ts"] = ts; st["updated_at"] = ts; st["ts"] = ts
st["last_seen"] = "2026-09-27T03:52:00"
st["last_run"] = "r293 2026-09-27T03:52:00"
st["last_round_at"] = "2026-09-27T03:52:00"
st["updated"] = ts
st["current_task"] = ("r293 done: S0 dual-UU canonical resolve + S6 30/30 + T-87 supply re-probe "
                      "(2985/5228, ETA ~06:41)")
st["last_result"] = "ok"
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json round_no ->", json.load(open(sp, encoding="utf-8-sig"))["round_no"])

# --- 3) heartbeat fleet/machines/bm-b.json
def cpu_pct():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True, text=True)
    try: return round(float(r.stdout.strip()))
    except Exception: return None

def free_ram_gb():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
        "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        capture_output=True, text=True)
    try: return round(float(r.stdout.strip()), 1)
    except Exception: return None

hp = "fleet/machines/bm-b.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
now = datetime.datetime.now().astimezone().isoformat()
epoch = int(time.time())
hb["last_seen"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now
hb["round_no"] = 293
hb["round"] = 293
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 16
c = cpu_pct(); f_ = free_ram_gb()
if c is not None: hb["cpu_util_pct"] = c; hb["cpu_pct"] = float(c)
if f_ is not None: hb["free_ram_gb"] = f_; hb["idle_ram_gb"] = f_
hb["verdict"] = "healthy"
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print("heartbeat ok: epoch=%d (int) clock=%s round=%d cpu=%s ram=%s"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], chk["round_no"], c, f_))
