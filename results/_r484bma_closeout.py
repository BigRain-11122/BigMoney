# r484 bm-a close-out: state + heartbeat + round report append (surgical, utf-8)
import json, time, io
from datetime import datetime

now = datetime.now().astimezone()
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+08:00" if now.utcoffset().total_seconds() >= 0 else "-08:00")
ts_short = now.strftime("%Y-%m-%dT%H:%M") + "x+08:00"

# ---- 1) state-bm-a.json ----
sp = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\state-bm-a.json"
with io.open(sp, "r", encoding="utf-8") as f:
    state = json.load(f)
state["round_no"] = 484
state["did"] = ("r484: 并发会话避让观察轮: S6 链 36+ 腿全 rc0 (dualrun ZERO-DRIFT 51/3; CALL-2026-09-30 ORANGE_COOL 新鲜出炉; "
    "REPORT/LIVE-2026-09-30 再生 ORANGE cap50 COOL 含 15:00 结算 marks; live.paper OK + open_fill PASS 0 例 + prospect 22/22 + "
    "promotion 0/22 诚实; update_daily 0 新行诚实 no-op 包装器尾仍 09-29 源同律); 并发会话半成品零触碰 (PREREG_TEMPLATE §0.5 "
    "staged 编辑 + BANNED_DIRECTIONS.json 未跟踪 原样保全·提交后 staged 态复原); T-129 交付件#1 prereg 起草暂缓 (模板脏碰撞面+"
    "banned-gate 落地后起草+烧批窗 10-03·票内留痕); smoke 47/47; attrition CLEAN; 自愈三件绿")
state["verify"] = ("smoke 47/47; S6 全 rc0 (lhb no-op 披露窗覆盖 rc0 九轮检疫态终; ah spawn 30min 节流在途; fundamental 6.4h 新鲜; "
    "b_layer 5 门过; 车道守卫 4 诚实 no-op; marks 幂等 aggr/grid no-op·sysv1 写盘 marks=2); compute_audit cap_violation 旗=CPU88% "
    "非 py 外部负载如实 (py_cpu 2.7% 本方无违令); WM py_low_board_clear; orders 127/127 双扫零未回执; 心跳 epoch int 自证")
state["next"] = ("r485: 09-30 bar 包装器端点继续观察 (落地=S6 全链+条件块自动挂钩); 10-01 月首轮三件套 (science_audit/"
    "monthly_briefing/self_review·治理零双跑); REGIME_GUARD v3 日期门自动激活 hands-off; RW-5 外审 10-03→解冻→D-41#1 跨起点 "
    "prereg (待并发会话 banned-gate 落地)")
state["last_round_at"] = ts_iso
state["updated"] = ts_iso
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print("state ok round_no=%s" % state["round_no"])

# ---- 2) heartbeat fleet/machines/bm-a.json ----
hp = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\machines\bm-a.json"
with io.open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
hb["last_seen"] = ts_short
hb["current_task"] = "r484 watch round closed (S6 all-green, concurrent-session avoidance, T-129#1 deferred to banned-gate landing + 10-03); next: 10-01 month-first trio"
hb["cpu_pct"] = 69.0
hb["cpu_util_pct"] = 69.0
hb["free_ram_gb"] = 36.8
hb["idle_ram_gb"] = 36.8
hb["gpu_free_vram_gb"] = 2.26
hb["gpu_free_vram_mib"] = 2263
hb["gpu0_free_vram_gb"] = 2.26
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["round_no"] = 484
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)
# self-verify epoch int + clock T-sep
with io.open(hp, "r", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"] and "+" in back["clock_read"], "clock_read must be ISO8601 T-sep"
print("heartbeat ok epoch=%d int, clock=%s" % (back["heartbeat_epoch_utc"], back["clock_read"]))

# ---- 3) round report append ----
rp = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\round_reports-bm-a.md"
line = (now.strftime("%Y-%m-%dT%H:%M") + "x+08:00 | r484 | dept:工程 | "
 "WM=py_low_board_clear 绿（板 open=0·W14 停泊·RW-5 冻结待 10-03 外审=合法 idle 白名单·red=False healthy；"
 "compute_audit cap_violation 旗=CPU88% 非 py 外部负载如实披露·py_cpu 2.7% 本方无违令）| "
 "并发会话避让轮: S0 探测=PREREG_TEMPLATE §0.5 编辑（staged 态）+BANNED_DIRECTIONS.json 未跟踪=并发交互会话 banned-gate 接线在制半成品"
 "（r483 addendum 已留痕归其主）——本轮零触碰该两件·禁全仓 add·提交后 staged 态复原·"
 "T-129 交付件#1 prereg 起草暂缓（物理依赖留痕: 模板脏碰撞面+banned-gate 落地后起草+烧批窗 10-03）| "
 "做了什么: (1) S0.5 双扫 orders 127/127 零未回执+decisions 尾=D-41 无新行+inbox 本机零未读（自发 W14 通告留置待 bm-b/bm-c 处理）"
 "(2) S6 链 36+ 腿全 rc0: dualrun ZERO-DRIFT 139 entries streak 51/3·compute_audit flags pool_starvation+supply_floor+cap_violation（如实）·"
 "WM probe py_low_board_clear·update_daily 0 新行诚实 no-op（包装器端点尾仍 09-29·failures=0·源同律禁手工注数·假日轮 cutoff 守 09-29）·"
 "regime ORANGE d3（hs300<MA200 #10+breadth 0.83≥65%）·scorecard 6/28/7（VOLATILITY 87.0 best）·"
 "CALL-2026-09-30 ORANGE_COOL sleeves4 act0 新鲜出炉·lhb no-op 披露窗覆盖 rc0（九轮源改史检疫态终）·heat 当日已采·"
 "futures/repo/options cutoff 覆盖·mf rank-spawn·sina_mf no-op·ths 当日已采·ah spawn 30min 节流在途·fundamental 6.4h 新鲜·"
 "b_layer 5 门过·车道守卫 4 诚实 no-op·live.paper OK（enforce→shadow 日期门降级如实·10-01 hands-off）·open_fill PASS 0 例·"
 "prospect 22/22 drift0·promotion 0/22 诚实·marks 幂等（aggr/grid no-op·sysv1 写盘 marks=2 entries=10）·"
 "t35_export 09-29 再生（6 员 18 仓 equity ¥5,995,354）·dscore/dreport faces=5/LIVE-2026-09-30 再生"
 "（ORANGE cap50 COOL 6 员 intraday 15:00 结算含·4 版本行）/build_status/token delta=0 "
 "(3) 自愈三件绿: loop pin=8 no-op·watchdog Ready·claw MATCH (4) attrition CLEAN（4 ledgers·2 healed 注记照录）(5) S7 双扫零新增 | "
 "验证证据: smoke 47/47+S6 全 rc0+attrition CLEAN+epoch int 自证 | "
 "当前活: 节前观察轮（09-30 bar 包装器端点落地自动挂钩）+10-01 月首三件套准备; "
 "最近实物: results/market_clock/CALL-2026-09-30.md+docs/live_usage/LIVE-2026-09-30.md（18:0x 本轮·ORANGE cap50 COOL）; "
 "下里程碑: 10-01 月首轮三件套（science_audit/monthly_briefing/self_review·治理零双跑）+REGIME_GUARD v3 日期门自动激活（hands-off）+"
 "RW-5 外审 10-03→解冻→D-41#1 跨起点 prereg（待并发会话 banned-gate 落地），窗≤48h | "
 "next: r485 = 包装器端点观察自动挂钩+10-01 月首三件套+W14 停泊异议窗观察（至 10-07） [via bm-a]\n")
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended r484")
