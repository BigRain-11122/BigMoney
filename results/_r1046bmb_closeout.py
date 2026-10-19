import json, io, time, datetime, subprocess

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S%z")
ts = ts[:-2] + ":" + ts[-2:]
epoch = int(time.time())

row = (
    "| 2026-10-20T04:02:00+08:00 | r1046 | dept:研究+产品 | "
    "WM verdict=false/lane healthy；S0 fetch behind=2（bm-c r1136 addendum 收据件）工作树预脏（drama 3 件+machine-health+update_status，他机/他道件）→ 不强 rebase 只定向提交；"
    "D-19 ord/dec 双水位持平（orders 目录 107/107 ack 零新令）；S1 smoke 49/49；orphan 面=0/7；sat engine alive(idle, queue 0, claimable 0)；"
    "watermark py_low_board_clear（合法 idle 白名单=板全闭环+pool 0+bandit 0）；compute_audit FLAG:supply_floor（pool ready 0 < floor 3 连续窗）"
    " | PRODUCT=①bm-a 承载两面 stale-takeover（O-2100 §2.4 STALE_MIN 合法）：t35_open_fill_verify day=2026-10-19 PASS（matched 1/dropped 0/breach 0/zero-pending 5）+ daily_scorecard HTML 再生（6 交易员/6 O-1600 行）"
    "②papers 六员推进至 10-19 bar（13 bars：COMPOSITE-CE-02 dd -1.39%、DROUGHT -0.41%、VOLATILITY -0.71%，x2 均 insufficient_data 诚实）"
    "③export-2026-10-19（6 交易员/19 持仓/equity 5,980,936/ops entry 1 exit 0）"
    "④REPORT-2026-10-20 + LIVE-2026-10-20（state=ORANGE/rung=ORANGE/cap 50%/heat=COOL/6 成员/4 版本行）"
    "⑤dashboard_status + strategy_scorecard（6 策略/28 交易员/7 组合卡，71.2s）+ market_clock CALL-2026-10-19（ORANGE_COOL，sleeves 4 activated 0）"
    "⑥regime_gate_dualarm DUALARM-2026-09-30（index 臂上行停在 09-30/emotion 09-22，awaiting-upstream 语义诚实，零判据）"
    " | 弃真/异动=bm-a 心跳 ~4.5h 陈旧（last_seen 10-19T23:29）已发 MSG-20261020-0400-bmb-bma-stale-faces；rev_osc 面板 incomplete=诚实 no-op（等面板）"
    " | S7 loop pin=2 no-op + watchdog 注册（S4U/SWA=false）+ pre-commit/pre-push 双爪 MATCH；attrition guard CLEAN（4 账本，历史缩行 healed）；"
    "本地未达 origin commit 数=2（本轮未 rebase，脏树含他机件）"
    " | r1047：1) 30min 节流到点（last spawn 03:20:17）后 update_astock_daily 点火补料 + 观察 validator 悬挂面 2) bm-a 回跳/接管面跟踪 3) supply_floor 补货=查 bm-c W281 波后席位转单可领面 4) RepoSlim 09:03 实锚核  |\n"
)

p = REPO + r"\logs\iteration-loop\round_reports.md"
with io.open(p, "a", encoding="utf-8", newline="") as f:
    f.write(row)

# state.json
sp = REPO + r"\state.json"
d = json.load(io.open(sp, encoding="utf-8"))
d["round_no"] = 1047
d["last_action"] = "r1046: bm-a-hosted faces stale-takeover (t35_open_fill_verify+ daily_scorecard) + papers/export/report/live products regenerated; MSG-20261020-0400 sent on bm-a 4.5h stale heartbeat"
d["last_action_at"] = ts
d["clock_read"] = ts
d["heartbeat_epoch_utc_face"] = epoch
json.dump(d, io.open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# heartbeat
hp = REPO + r"\fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["ts"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
h["current_task"] = "r1046 done: bm-a stale-takeover faces + product chain regenerated"
h["cpu_cores"] = 16
h["ram_free_pct"] = 44.0
h["gpu_free_vram_mb"] = 3709
h["cpu_load_pct"] = 12
h["verdict"] = ("YELLOW: r1046 product = bm-a 承载两面 stale-takeover 合法接管（t35_open_fill_verify 10-19 PASS / daily_scorecard 再生）+ papers 13 bars + export 10-19 + REPORT/LIVE-2026-10-20 + clock ORANGE_COOL。"
                "板空 pool 0 supply_floor 亮红；bm-a 心跳 ~4.5h 陈旧已发 MSG-20261020-0400。")
h["idle_rounds"] = 2
h["agenda_starved"] = True
json.dump(h, io.open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("report+state+heartbeat written", ts, epoch, type(epoch).__name__)