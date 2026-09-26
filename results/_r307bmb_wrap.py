# -*- coding: utf-8 -*-
"""r307 bm-b wrap: state.json round flip + round-report append + heartbeat
refresh. Lineage: r306 wrap (post-R302 astimezone/T-sep laws). Self-verify:
json re-parse of all three files, epoch isinstance(int), clock_read
'T'+offset (R170/R178/R262 laws)."""
import ctypes
import datetime as dt
import io
import json
import os
import time
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")   # +offset
EPOCH = int(time.time())
GPU_FREE_MB = 6935                                             # nvidia-smi 07:26
CPU_PCT = 4                                                    # Win32_Processor 07:26

# --- free RAM via GlobalMemoryStatusEx (authoritative avail phys) ---
class _MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = _MS()
ms.dwLength = ctypes.sizeof(_MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
FREE_MB = int(ms.ullAvailPhys // (1024 * 1024))
FREE_GB = round(FREE_MB / 1024.0, 1)
GPU_GB = round(GPU_FREE_MB / 1024.0, 1)

TASK = ("r307: honest-maintenance round + mid-round fold of bm-a r301 wrap "
        "collision (stash->pull--rebase->pop 28 UU resolved canonical: 23 "
        "take-new by ts with guard-face whitelist qualification, dashboard "
        "take-this-machine, compute_audit/x2 union, autofill cap50 + last_tick "
        "tie->HEAD) + S6 30/30 + orders 91/91 double-scan")

# --- 1) state.json round flip 306 -> 307 ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["round_no"] = 307
st["did"] = ("r307: 诚实维护轮=板 0 open+job_list 0+队列节点全闭合(r297 定谳 J12 "
             "反重复/J13 bm-a 车道/J10·J18b 已交付/town r292 对齐/Optuna 6<8 冻结)"
             "·轮首 pull fast-forward 3da540ba..758bf157 收编 bm-a autofill tick "
             "claim sectldr-0of1 owner=bm-a 07:20:04(CN-SECTOR-LEADER-P1 判决批 "
             "C8 watchdog 拥有 spawn·est 45-120min·bm-b 零触车道); S0.5 orders "
             "91/91 轮首+收尾双扫零未ack(_r305bmb_orders_diff 复用·decisions 直扫"
             "不可达 R291 如实注记·零新 O 件); S1 smoke 25/25; S2 post_review 开放"
             "负判定复扫 0 开口(census 2151Y/551W/13 历史NO 同 id 全翻绿·tail "
             "T-85/T-87 YES); S6 30/30 rc=0(_r307bmb_s6_chain.ps1 冻结血统 Copy-"
             "Item+轮号面·difflib delta=1 内容行 r298 坑律: audit v2.3 CLEAN "
             "flags=[]·probe 07:24:03 insufficient_history n=2 12.4min=15min 持续"
             "窗未满采样诚实态·update_daily 周末零新行·regime ORANGE shadow "
             "breadth 0.77·scorecard 6/28/7·clock CALL-2026-09-24 幂等·lhb "
             "min-interval·heat 周末·futures cutoff 覆盖零网络·options/mf/sina_mf/"
             "ths/ah=bm-a 车道 stdout-only·fundprem=bm-c 车道·astock panel fresh "
             "cutoff 2026-09-24 零网络(r305 首拉收口态持守)·fundamental 9.1h "
             "skip·b_layer 再 derive·live.paper OK·t35v PASS 零 pending·t24 22/22 "
             "drift 0·promo 0/22·aggr/alloc/grid 幂等 no-op·export 09-24 再生·"
             "daily_report faces=4 token=1·token L2 0 today); 轮中撞车=bm-a r301 "
             "wrap ecafdcc2 07:23:55 同窗落(判决批 C8 LAUNCH pid 64840 开烧+"
             "autofill _runner_alive explicit-null 守卫修复 T34)→本轮 S6 面 stash"
             "(r307-pres6-fold)→pull --rebase fast-forward→stash pop 28 UU→分类器 "
             "12 GREEN+16 UNKNOWN→冻结血统 resolver(_r306bmb_resolve 整件复制+语"
             "境面·白名单定性扩 7 键 guard/regime_guard/batch_in_flight/"
             "watermark_verdict/machines/per_round_context/total_report_tokens_est"
             "=REGIME_GUARD env 请求面 bm-a enforce+2026-10-01 vs 本机 no-env "
             "shadow 每 live_paper 再 derive 双面诚实+token 测量快照 R216+_r307bmb_"
             "dbg 残余 watermark_verdict 定谳)→28/28 全门 PASS(23 take-new 全本轮"
             "新面 07:24>07:21·dashboard x2 本机整字节 r301/r306 先例·compute_audit "
             "union 201|201->202 双机采样零丢 latest=07:23:56·x2_watch 546+12->"
             "558·autofill launches union51 cap50 仅丢最旧1+last_tick 同秒 tie->"
             "HEAD r140)·stash drop 76f22246 零残留·p1d_gates 后台写手 07:30 面 "
             "随 commit 收编(r290 律); inbox 零未读; schtasks 三任务在役 "
             "(IterationLoop running=本轮·Autofill/Watchdog 就绪·R49 CSV 路径); "
             "迁移 v2.2 journal 健康=每分钟 precheck waiting(Tuanjie 编辑器 x3+"
             "watcher-shell 28696 设计在役·T-87 cwd-holder 29440 已按设计自清·"
             "Bigmoney 树 cwd 阻塞面零·窗至 09-29 12:00 勿双 arm)")
st["verdict"] = "green"
st["next"] = ("09-28 周一首新 bar 全链(update_daily->live.paper(有新 bar 面设 env "
              "enforce)->t35v->t24x2->aggr->grid 5 账户首拍唤醒->export->"
              "scorecard->daily_report)+T-87 周一 15:30 后首次日续拉实弹(全宇宙分"
              "离 fetch by-design·settled 重载自愈)+CN-SECTOR-LEADER-P1 判决批 "
              "bm-a 烧批看护(45-120min wall·checkpoint 续跑安全跨轮·terminal "
              "p1_results.json 幂等·harvest 归 bm-a 车道)+10-01 月度三件套+"
              "REGIME_GUARD v3 日期门(10-01 起 v3 响应矩阵自动激活)+迁移窗 v2.2 "
              "armed 至 09-29 12:00 勿双 arm+R310 下次 5x 核对")
st["last_round_ts"] = NOW
st["last_result"] = "ok"
st["current_task"] = TASK
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 307 and "+" in chk["last_round_ts"]
print("state.json round 307 ok")

# --- 2) round report append (single line, fixed fields) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    NOW + " | r307 bm-b | dept:舰队/工程 | "
    "WM-VERDICT: 绿 red=false lane healthy(watermark_red 07:00:13 red=false; "
    "S6 probe 复跑 rc=0 verdict=insufficient_history n=2 span 12.4min=15min "
    "持续窗未满采样诚实态非违规; 池 CN-SECTOR-LEADER-P1 判决批 owner=bm-a "
    "07:20:04+C8 LAUNCH pid 64840 在烧(bm-a r301 ecafdcc2)·板清 0 open 全 "
    "claimed·bandit claimed/parked=合法 idle 白名单·batch 由 watchdog C8 拥有 "
    "spawn) | "
    "did: 诚实维护轮·板 0 open+job_list 0+队列节点全闭合(r297 定谳: J12 反重复"
    "禁碰/J13 bm-a 车道/J10·J18b 已交付/town r292 对齐/Optuna 6<8 冻结); S0 "
    "pull fast-forward 3da540ba..758bf157 收编 bm-a autofill tick claim 判决批 "
    "sectldr-0of1 owner=bm-a 07:20:04(bm-b 零触车道); S0.5 orders 91/91 轮首+"
    "收尾双扫零未ack(_r305bmb_orders_diff 复用·集团 decisions.md 直扫 bm-b 无"
    "集团仓 clone 不可达如实注记 R291=fleet/orders 镜面承接零差集·零新 O 件); "
    "S1 smoke 25/25; S2 post_review 开放负判定复扫 0 开口(_r305bmb_postreview_"
    "pool 复用·census 2151Y/551W/13 历史NO 同 id 后续 YES 全翻绿·tail T-85/T-87 "
    "YES 零 P0)+job_list 0+水位红牌 red=false; S6 30/30 legs rc=0(_r307bmb_s6_"
    "chain.ps1 冻结血统 Copy-Item+replace 轮号面·difflib delta=1 内容行 r298 坑"
    "律: audit v2.3 CLEAN flags=[] cpu9.0/py0.8·update_daily 周末零新行合法·"
    "regime ORANGE shadow breadth 0.77·scorecard 6/28/7·clock CALL-2026-09-24 "
    "幂等·lhb min-interval·heat 周末·futures cutoff 覆盖零网络·options/mf/"
    "sina_mf/ths/ah=bm-a 车道 stdout-only 诚实 no-op·fundprem bm-c 车道·astock "
    "panel fresh 零网络(r305 首拉收口态持守)·fundamental 9.1h 新鲜跳过·b_layer "
    "再 derive·live.paper OK·t35v PASS 零 pending·t24 22/22 drift 0·promo 0/22·"
    "aggr/alloc/grid 幂等 no-op·export 09-24 再生·daily_report faces=4 token=1·"
    "token L2 0 today); 轮中撞车=bm-a r301 wrap ecafdcc2 07:23:55 同窗落(判决批 "
    "C8 LAUNCH pid 64840+autofill runner=null 守卫修复)→S6 面 stash(r307-"
    "pres6-fold)→pull --rebase fast-forward 758bf157..ecafdcc2→stash pop 28 "
    "UU→skill 正典=分类器 12 GREEN+16 UNKNOWN fail-closed→冻结血统 resolver"
    "(_r306bmb_resolve 整件复制+语境面 replace·代码逻辑零改动复核)→首跑 fail-"
    "closed 拦 REPORT guard 面→_r307bmb_deepdiff 全批定性(REGIME_GUARD env 请求"
    "面 bm-a enforce+active_from 2026-10-01 vs 本机 no-env shadow·每 live_paper "
    "再 derive 双面诚实+batch_in_flight/watermark_verdict probe advisory+token "
    "测量快照 R216+纯 ts 族)→白名单定性扩 7 键带注释(_r307bmb_dbg 残余 "
    "watermark_verdict 定谳)→28/28 全门 PASS: 23 take-new 全本轮新面 07:24>"
    "07:21·dashboard x2 本机整字节(r301/r306 先例)·compute_audit union 201|201-"
    ">202 双机采样零丢 latest=07:23:56·x2_watch 546+12->558·autofill launches "
    "union51 cap50 仅丢最旧 2026-09-25 23:40:01+last_tick 同秒 07:20:01 tie->"
    "HEAD r140)→git add 28→stash drop 76f22246 零残留·p1d_gates 后台短命写手 "
    "07:30 面随 commit 收编(r290 律·r306 坑律已知族); inbox 零未读; schtasks "
    "三任务在役 CSV 路径(IterationLoop running=本轮·Autofill/Watchdog 就绪·"
    "R49); 迁移 v2.2 journal 健康=每分钟 precheck waiting(Tuanjie 编辑器 x3+"
    "watcher-shell 28696 设计在役·T-87 cwd-holder 29440 已按设计自清·Bigmoney "
    "树 cwd 阻塞面零·执行器域勿双 arm·窗至 09-29 12:00); CODELY 零新增坑律(常"
    "规绿轮无新教训·记忆入口四问门①不过) | "
    "evidence: _r307bmb_s6_chain.ps1+results/_r307bmb_s6_chain.log(30/30 rc=0)+"
    "_r307bmb_resolve.py(28/28 全门 PASS·白名单 7 键定性注释)+_r307bmb_deepdiff."
    "py(全批漂移定性)+_r307bmb_dbg.py(残余 watermark_verdict 定谳)+stash drop "
    "76f22246+pull 758bf157..ecafdcc2 fast-forward+_r305bmb_orders_diff 复用"
    "(91/91 双扫)+_r305bmb_postreview_pool 复扫(0 开口)+smoke 25/25+state/"
    "heartbeat 307 epoch int 自证 | next: 09-28 周一首新 bar 全链(update_daily->"
    "live.paper(有新 bar 面设 env enforce)->t35v->t24x2->aggr->grid 5 账户首拍"
    "唤醒->export->scorecard->daily_report)+T-87 周一 15:30 后首次日续拉实弹"
    "(全宇宙分离 fetch by-design·settled 重载自愈)+CN-SECTOR-LEADER-P1 判决批 "
    "bm-a 烧批看护(45-120min wall·checkpoint 跨轮续跑安全·terminal p1_results."
    "json 幂等·harvest 归 bm-a 车道)+10-01 月度三件套+REGIME_GUARD v3 日期门"
    "(10-01 起 v3 响应矩阵自动激活)+迁移窗 v2.2 armed 至 09-29 12:00 勿双 arm+"
    "R310 下次 5x 核对"
)
raw = io.open(RP, "r", encoding="utf-8").read()
add_nl = "" if (not raw or raw.endswith("\n")) else "\n"
with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(add_nl + line + "\n")
print("round_reports.md +1 line ok")

# --- 3) heartbeat fleet/machines/bm-b.json ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["current_task"] = TASK
hb["cpu_cores"] = 16
hb["free_ram_gb"] = FREE_GB
hb["gpu_free_vram_gb"] = GPU_GB
hb["cpu_util_pct"] = CPU_PCT
hb["round_no"] = 307
hb["verdict"] = "green"
hb["cores"] = 16
hb["idle_ram_gb"] = FREE_GB
hb["gpu_free_vram_mb"] = GPU_FREE_MB
hb["idle_ram_mb"] = FREE_MB
hb["gpu_idle_vram_mb"] = GPU_FREE_MB
hb["gpu_idle_vram_gb"] = GPU_GB
hb["cpu_pct"] = CPU_PCT
hb["round"] = 307
hb["free_ram_mb"] = FREE_MB
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read T-sep law (R262)"
assert v["round_no"] == 307
print("heartbeat ok: epoch=%d int, clock=%s, free_ram=%sGB gpu=%sMB" % (
    v["heartbeat_epoch_utc"], v["clock_read"], FREE_GB, GPU_FREE_MB))
