# -*- coding: utf-8 -*-
# r280 bm-b round-close writer: HANDOVER 5x check-update (line-3 refresh + end-append
# two-track), round_reports.md line, state.json round_no=280, heartbeat bm-b.
# R271 timestamp law: all wall-clock values derive from ONE datetime.now() instance.
# R262 format law: clock_read = isoformat() with T separator.
import ctypes
import datetime as dt
import json
import subprocess

now = dt.datetime.now().astimezone()
ts_line = now.isoformat()               # T-separated, UTC offset
ts_compact = now.strftime("%Y-%m-%d %H:%M")
epoch = int(now.timestamp())

# ---------------------------------------------------------------- HANDOVER
hp = "research/HANDOVER.md"
t = open(hp, encoding="utf-8").read()
lines = t.splitlines()
LI = next(i for i, l in enumerate(lines) if l.startswith("> 本文件由循环"))
assert lines[LI].startswith("> 本文件由循环"), "line drift"
old_l3 = lines[LI]
# demote current 最近核对 block into 上一次核对, drop the previous 上一次核对 tail
idx = old_l3.find("最近核对=")
prev_block = old_l3[idx:]  # "最近核对=bm-a round 275（...）；上一次核对=bm-a round 270（...）；bm-b round 270 行亦在档=..."
# keep only the bm-a r275 segment as 上一次核对 (segment ends at the first "；上一次核对")
cut = prev_block.find("；上一次核对=")
if cut > 0:
    prev_keep = prev_block[:cut]  # "最近核对=bm-a round 275（...）"
else:
    prev_keep = prev_block
new_l3 = ("> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。最近核对=bm-b round 280"
          "（2026-09-26 23:5x·对账增量=文末 round 280 bm-b 行〔bm-b r277-280 窗+bm-a R276-278 并读："
          "**T-87 供给车道建设交付窗**（CEO O-2320 四票+O-2330/2335 双令窗·bm-b=采集器车道/让路面·"
          "bm-a=s2 prereg 冻结+runner 面）+统一链 187,845 平持=本窗零批 finalize（prereg 冻结/runner "
          "建造面零跑·MF_IC_P1 待源·迁移 precheck 等待面）〕）；上一次" + prev_keep)
lines[LI] = new_l3

NEW_LINE = (
    "- 开发队列增量窗（接续版）**round 280 bm-b（5x 核对本轮），2026-09-26 23:5x 补核；对账区间=增量 bm-b r277-280"
    "（基线=round 275 bm-a 行），统一链 187,845 平持实读（本窗零批 finalize：T-85 fusion-nav runner 修正案零跑、"
    "T-87 s2 REV_OSC_STOCK_P1 prereg 冻结面未判、MF_IC_P1 待 EM 源）**：①**bm-b r277-280=CEO O-2320/2325/2330/2335 "
    "四令窗+供给车道交付窗**——r277 四 CEO 票认领（T-85 fusion-nav 池备 selftest 15/15 caliber-anchored·T-86/87/88 面）"
    "+COMPUTE_AUDIT v2.3 any-day starvation law（周末空载豁免废除）+pool red card discharged；r278=T-86 认领竞速让路 bm-a"
    "（aea185e3 23:10:09<d98adfb2 23:11:50·§4）+O-2320/2325 双令回执+machine/bm-b-r278 保险分支首用（D-20260925-01③ "
    "首实弹）；r279=T-88 认领竞速让路 bm-a（0cd23254 23:18:36<7313592d 23:24:37·r279 pre-claim fetch 坑律）+五实测发现捐赠 "
    "addendum+PRODUCT_MATRIX v1.2 gap items 4-5+T-87 供给车道认领（progress_r279_bmb·与 bm-a s2 prereg 面零撞）"
    "+O-2330/2335 双令回执；**r280（本轮）=T-87 供给车道建设交付**——step-0 端点探针（ak.stock_zh_a_daily sina qfq 4/4 活"
    "含 bj 面 vs ak.stock_zh_a_hist EM 0/4 本机 ConnectionError=通道裁决定 sina-only·诚实披露）+采集器 scripts/"
    "update_astock_daily.py（update_sina_mf/futures 家族规约镜像：2.5s 限速/per-股 checkpoint 断点续拉/conn-fuse 3/"
    "隔离≥3/分离后台全宇宙/30min spawn 节流/锁/原子写/selftest 全过〔todo=文件派生面非 done-set=R235 族设计期根修〕；"
    "qfq 除权重写=整股重拉原子替换 readjusted 桶〔对家族 not-touched 律的已披露偏离·qfq 面必须跟源调整真值〕；"
    "宇宙=eligibility.csv 5,228 可拉〔B 股 2/9 前缀+北交 4/8/920 按桶诚实跳过·bj 探针活性在档=扩展留未来署名决策〕）"
    "+实弹小样 6 股 49,043 行全史（1991→09-24）零失败+vwap 单位锚 max 0.037 在档（r262 律）+全宇宙分离后台 pass spawn"
    "（5,228 股 ~3.6h 在飞·status=results/astock_daily_update_status.json）+S6 链接线（Tools/iteration_prompt.txt 新腿·"
    "车道=bm-b R31 护栏）+票面 progress_r280_bmb（R255/R257 五面探测 2+/1- 字段级增量）+fusion-nav-0of1 认领竞速让路"
    "（本机 tick 陈旧读面 claim 23:40:04→tick 自捕 claim_lost_yield→让 bm-a 23:20:03 原始认领·空重放合法弃置 r279 律·"
    "新坑律=autofill tick 认领前不 fetch 机制缺口在册）+两坑律入册（inbox 移件阻塞 rebase=r257 新参）；②**bm-a R276-278 "
    "并读**（其 5x 补核归 bm-a）——T-87 s2 first-priority=REV_OSC_STOCK_P1 prereg 冻结（CEO O-2330 超跌反弹袖个股版+"
    "O-2335 淬炼炉镜像轴·7 cells×2 faces+2000 nulls 双法+全史虚拟起点 census·p1c 冻结面板在位零拉取依赖·seed 登记同 "
    "commit）+zero-run amendment（sentinel dual-face·r251 probe-authoritative）+T-85 fusion-nav crash fix（3 CE frozen "
    "specs x2 block·selftest 15→18）+rev_osc_stock_p1.py runner（selftest 15/15 hermetic）+F-04 车道 MSG（双面互认零冲突="
    "bm-a 判批用冻结面板·bm-b 采集器供前向腿）；③窗口维护面：S6 链逐轮全绿（r280=22 腿全 rc=0 含新腿 no-op〔refresh 在飞"
    " spawn 节流〕·周末 no-op 族·cutoff 09-24 中秋休市）、smoke 25/25、orders 89/89 双扫零未回执、板 84 票全 done/claimed "
    "零 open、水位 healthy/py_low_board_clear、post_review 尾零 NO、迁移双 armed precheck 等编辑器（bm-b v2.2 PID 28696 等 "
    "Tuanjie 三进程·bm-a v2.1 等 Code.exe·窗 09-29 12:00·precheck 零突变车道照跑）、bm-c r71 后停机维持；④指针："
    "**09-28 周一开市窗=新 bar 全链接力**（update_daily→live.paper REGIME_GUARD v3 enforce→t35v→t24×2→aggr 20 账→"
    "grid 5 账首拍→export→scorecard→daily_report）+**astock_daily 全宇宙 pass 完成检查+周一首次日线续拉实弹**"
    "（消费面=T-87 REV_OSC 股票袖前向腿+O-2335 淬炼炉个股镜像·跨机数据本地性=fleet/TRANSFER.md 机制决策待 bm-a 消费面开启）"
    "+MF_IC_P1 待 EM 源恢复+10-01 月界三件套（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门生效"
    "（三重门·勿手改）+10-31 公决首检 all-HOLD 不变+T-34 半档梯 11-01 不变+R285 下次 5x 核对。")
lines.append(NEW_LINE)
with open(hp, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines) + "\n")
print("HANDOVER: line3 refreshed + r280 line appended (%d chars)" % len(NEW_LINE))

# ------------------------------------------------------------- round report
rp = "logs/iteration-loop/round_reports.md"
rr = ("{ts} | r280 (bm-b) | dept:数据/工程 | WM-VERDICT: GREEN healthy red=false "
      "(weekend legal idle·py_low_board_clear face unchanged) | did: T-87 supply-lane "
      "BUILD delivered per r279 claim — step-0 probe (sina stock_zh_a_daily qfq 4/4 "
      "alive incl bj face; EM stock_zh_a_hist 0/4 dead-from-bm-b -> channel=sina-only "
      "disclosed) + collector scripts/update_astock_daily.py (family conventions mirror, "
      "selftest all-PASS, qfq-readjust law deviation disclosed, file-derived todo = R235 "
      "family design-time fix) + live smoke 6 syms 49,043 rows full-history zero-fail + "
      "FULL-UNIVERSE detached pass SPAWNED (5,228 syms ~3.6h in flight, pid-lock in data, "
      "status=results/astock_daily_update_status.json) + S6 chain wiring (iteration_prompt "
      "new leg, lane=bm-b R31 guard) + ticket progress_r280_bmb (five-face probe 2+/1-) | "
      "S0 double collision resolved per skill: fusion-nav-0of1 claim race YIELDED to bm-a "
      "23:20:03 first-claim per s4 (empty-replay legal drop, r279 precedent; NEW pitfall: "
      "autofill tick claims on stale local read without fetch) + autofill_state mixed-dict+"
      "ledger union recipe (_r280bmb_resolve2.py) + inbox-move-blocks-rebase pitfall (r257 "
      "new param) | evidence: probe JSON + selftest PASS + status JSON + S6 22 legs rc=0 + "
      "smoke 25/25 + orders 89/89 double-scan zero-unacked | next: r281 = pass-completion "
      "check + Mon 09-28 first daily-continuation live fire + consumption face (REV_OSC "
      "sleeve forward leg; TRANSFER decision when bm-a consumption opens) + migration "
      "window watch (editor-gated, 09-29 12:00) + 10-01 month-first trio".format(ts=ts_line))
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(rr + "\n")
print("round_reports: r280 line appended")

# ------------------------------------------------------------------- state
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": 280,
    "did": ("r280: T-87 supply-lane build delivered (sina qfq channel probe 4/4 vs EM 0/4 "
            "disclosed; collector + selftest PASS + 6-sym smoke 49043 rows + full-universe "
            "detached pass spawned 5228 syms; S6 wiring; ticket progress_r280_bmb) + "
            "fusion-nav-0of1 claim race yielded to bm-a per s4 (autofill stale-read pitfall "
            "recorded) + 2 rebase collisions resolved per skill + HANDOVER 5x check-update"),
    "verdict": "green",
    "next": ("r281: astock_daily pass-completion check + Mon 09-28 first daily-continuation "
             "live fire + REV_OSC consumption face (TRANSFER decision when bm-a opens) + "
             "migration window watch (editor-gated precheck, 09-29 12:00) + 10-01 month-first "
             "trio + REGIME_GUARD v3 date gate"),
    "last_round_ts": ts_line,
    "last_result": "ok",
    "current_task": ("r280 done: T-87 supply lane built+live (collector/spawned pass); "
                     "orders 89/89; S6 22 legs rc=0"),
    "last_tick": now.strftime("%H:%M"),
    "updated_at": ts_line,
    "last_seen": ts_line,
    "ts": ts_compact,
    "last_run": "R280 " + ts_line,
    "last_round_at": now.strftime("%H:%M"),
    "updated": now.strftime("%H:%M"),
})
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json: round_no=280 written")

# --------------------------------------------------------------- heartbeat
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_gb = round(m.ullAvailPhys / 1e9, 1)
import os
cores = os.cpu_count()

hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb.update({
    "last_seen": ts_line,
    "clock_read": ts_line,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": cores,
    "free_ram_gb": free_gb,
    "current_task": ("T-87 supply lane: collector built, full-universe astock_daily pass "
                     "in flight (5228 syms, detached); S6 chain 22 legs green"),
    "verdict": "green",
    "round": 280,
})
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
with open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.loads(open(hb_path, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("heartbeat: epoch=%d int-ok clock T-ok free_ram=%sGB cores=%s"
      % (chk["heartbeat_epoch_utc"], free_gb, cores))
print("ALL CLOSE-WRITES OK ts=%s" % ts_line)
