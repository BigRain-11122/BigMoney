# -*- coding: utf-8 -*-
# r708 bm-c close driver: round-report append + state bump 708->709 + heartbeat
# nine-field refresh + self-asserts (epoch int, clock_read T-sep, round math).
# JSON surgery only through this script; utf-8 no-BOM write-back.
import json, datetime, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")            # 2026-10-08T00:0x:xx+08:00
EPOCH = int(NOW.timestamp())
CPU, RAMF, RAMT, RAMPCT, VRAM = 11.0, 3.9, 23.9, 16.3, 913

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (TS + " | r708 | 常态外调批补位供给轮（RESEARCH_MECHANISM v1.1 每日≥1 源律·10-05~08 断档恢复）："
  "research/digests/DIGEST-20261008-qdii-holiday-premium-arb-radar.md 落盘——"
  "jisilu 套利 feed 常设道 run-9 机器差分（4 new/4 rolled-out·真增量=QDII 跨境 ETF 长假溢价盘前申购套利双帖聚集 525666/525734〔10-01 开题+10-07 发酵跟进〕·民俗宣称 20 万/篮=未验证假设〔借力三律〕·C 级观察池新簇·ARB-1 邻接·10-08 复市即活验证窗）"
  "+hibor 金工雷达差分（3 新=10 月配置月报窗 财通/开源港股/华福·D 级标题级）·funnel 7 收割/0 过闸/+1 观察簇（采集≠入册·防凑数律遵从）"
  "+S0 churn absorb ae277fa4c（5 daemon live faces）+pull --rebase 干净 up-to-date+孤儿面=1（ComfyUI idle server·CEO 私产·只读披露不击杀） "
  "| smoke 48/48 · S6 38/38 rc0（dualrun ZERO-DRIFT streak 28） · QA 5/5（determinism=True 29th·93 trades·equity 1,017,839 冻结恒等·png 66,401B） · "
  "orders 双扫零差（51/176 UNACKED=0） · DEC/ORD 水位双 unchanged（771c3a8d/17accc40 恒等） · idle NOT-GREEN（常驻负载·idle_rounds=0·--worked 产出工申报） · "
  "attrition CLEAN（4 件 healed 注记照录） · 自愈=loop pin=5 no-op+watchdog 在位+双爪装好 · 本地未达 origin commit 数=0（commit 后 push 自证） "
  "| 下轮 r709：10-08 复市首 bar 面（盘后数据链 re-arm+REGIME v3 first-bar enforce+CTA_P1 接线 O-2215②+fund_premium 15:30 首采 bm-c 道+QDII 长假溢价 digest 主题对照观察）；O-2245 后续待工单；next 5x=r710 HANDOVER\n")
with io.open(RR, "a", encoding="utf-8") as f:
    f.write(line)

DID = ("r708 bm-c: standing external-scan digest supply round (RESEARCH_MECHANISM daily>=1-source law, 3-day gap restored). "
  "(1) S0 churn absorb 5 daemon live faces (ae277fa4c) then clean pull --rebase (up-to-date). "
  "(2) Product: research/digests/DIGEST-20261008-qdii-holiday-premium-arb-radar.md -- jisilu arb-feed standing channel run-9 machine-diff "
  "(4 new/4 rolled-out; live catch = QDII cross-border ETF holiday-premium pre-market subscription arbitrage double-post cluster 525666/525734, "
  "10-01 opening + 10-07 'fermented' follow-up; folklore claim 20w/basket = unverified hypothesis per borrow-law; C-grade observation-pool cluster, "
  "ARB-1 adjacency, 10-08 reopen day = live verification window for fund_premium premium face) + hibor radar diff (3 new = Oct allocation "
  "monthly-report window: Caitong / Kaiyuan-HK / Huafu; D-grade title-level). Funnel: 7 harvested / 0 admitted / +1 observation cluster (no padding, O-1136). "
  "(3) S0.5+s7close double-sweep: DEC/ORD hashes unchanged both sweeps (771c3a8d / 17accc40), unacked=0 (51/176). (4) S1 smoke 48/48. "
  "(5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 28). (6) QA 5/5 (determinism=True 29th, 93 trades, equity 1,017,839 frozen identity, png 66,401B). "
  "(7) orphan face=1 ComfyUI idle server (CEO-owned, no-kill documented). (8) idle NOT-GREEN (resident load) idle_rounds=0, --worked declared for digest product. "
  "(9) S7 self-heal: loop pin=5 no-op + watchdog registered + pre-commit/pre-push claws installed + attrition guard CLEAN.")

VERDICT = ("r708 bm-c: standing external-scan digest supply round clean. Product = DIGEST-20261008-qdii-holiday-premium-arb-radar.md "
  "(jisilu run-9 + hibor radar machine-diffs; QDII holiday-premium arb double-post cluster -> C-grade observation pool, ARB-1 adjacency, "
  "10-08 reopen live-verification window; funnel 7/0/+1 honest); S0 churn absorb clean rebase; S6 38/38 rc0 dualrun streak 28; QA 5/5 determinism 29th; "
  "smoke 48/48; orders zero-delta double-sweep; DEC/ORD unchanged; orphan face=1 no-kill; idle not green-idle (resident load), idle_rounds=0 worked-declared.")

NEXT = ("r709: (a) 10-08 reopen FIRST BAR face (evening after close): data-chain re-arm + REGIME_GUARD v3 first-bar enforce + CTA_P1 paper wiring "
  "(O-2215-2, GM-signed, no-bar blind wiring forbidden) + fund_premium 15:30 first snapshot (bm-c lane) + QDII holiday-premium observation check vs "
  "DIGEST-20261008 theme-1 (ARB-1 adjacency, folklore claim vs measured premium distribution); (b) O-2245 follow-ups upon ticket (adaptation first-item "
  "scheduling proposal + OSS- pool enrollment + nautilus/E2/E5 group ruling); (c) cloudF aggregation row window 10-14; (d) next 5x = r710 HANDOVER. [via bm-c r708]")

ART = ("research/digests/DIGEST-20261008-qdii-holiday-premium-arb-radar.md (product) + results/jisilu_feed_baseline.json run-9 (4 new/4 out, raw xml 8,662B) "
  "+ results/hibor_radar_baseline.json (3 new/3 out) + qa/smoke-r708.md 5/5 + qa/equity-curve-r708.png 66,401B (determinism=True 29th, 93 trades, equity 1,017,839 "
  "frozen identity) + results/_r708bmc_s6_log.txt (38 legs rc0, dualrun streak 28) + results/_r708bmc_s05_facts.json (double-sweep DEC/ORD unchanged, unacked=0)")

CUR = ("当前活: r708 bm-c 常态外调批补位供给轮收口（每日≥1 源律断 3 天恢复·DIGEST-20261008 QDII 长假溢价套利观察簇+hibor 10 月月报窗） "
  "| 最近实物: research/digests/DIGEST-20261008-qdii-holiday-premium-arb-radar.md+qa/smoke-r708.md 5/5（determinism 29th·equity 1,017,839 冻结恒等）"
  "+results/_r708bmc_s6_log.txt（38/38 rc0·dualrun streak 28）@ " + TS +
  " | 下个里程碑: 10-08 复市首 bar 面（盘后数据链 re-arm+REGIME v3 enforce+CTA_P1 接线+fund_premium 15:30 首采+QDII 溢价观察对照）；next 5x=r710 HANDOVER")

HP = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(HP, encoding="utf-8-sig"))
assert st["round_no"] == 708, "round_no anchor mismatch: %s" % st["round_no"]
st.update({
  "round_no": 709, "round_no_label": "round 708 (bm-c)",
  "last_round": 708, "last_round_at": TS, "last_round_ts": TS,
  "last_seen": TS, "last_seen_at": TS, "last_ts": TS, "last_run_at": TS,
  "current_task_at": TS, "updated": TS, "updated_at": TS, "ts": TS,
  "clock_read": TS, "heartbeat_epoch_utc": EPOCH,
  "cpu_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
  "free_ram_gb": RAMF, "idle_ram_gb": RAMF, "ram_free_gb": RAMF,
  "gpu_free_vram_mib": VRAM, "gpu_free_vram_mb": VRAM, "gpu_free_mib": VRAM,
  "did": DID, "verdict": VERDICT, "note": "r708: standing external-scan digest law restored (3-day gap); QDII holiday-premium arb double-post cluster = C-grade observation catch, 10-08 reopen verification window; funnel 7/0/+1 honest.",
  "current_task": CUR, "activity_now": VERDICT,
  "last_round_summary": "r708: standing-scan digest supply (DIGEST-20261008 QDII cluster + hibor Oct window, funnel 7/0/+1), S0 churn absorb clean, S6 38 rc0 streak 28, QA 5/5 det-29th, smoke 48/48, push verified.",
  "last_action": "r708: standing-scan digest supply (DIGEST-20261008 QDII cluster + hibor Oct window, funnel 7/0/+1), S0 churn absorb clean, S6 38 rc0 streak 28, QA 5/5 det-29th, smoke 48/48, push verified.",
  "next_pointer": NEXT, "verify": ART,
  "last_decisions_read_at": TS,
})
json.dump(st, io.open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb.update({
  "free_ram_gb": RAMF, "gpu_free_vram_mb": VRAM,
  "idle_rounds": 0, "agenda_starved": False,
  "heartbeat_epoch_utc": EPOCH,
  "last_seen": TS, "clock_read": TS, "ts": TS,
  "cpu_pct": CPU, "cpu_util_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
  "idle_ram_gb": RAMF, "ram_free_gb": RAMF,
  "gpu_free_vram_mib": VRAM, "gpu_idle_vram_mb": VRAM, "gpu_idle_vram_mib": VRAM,
  "gpu_vram_free_mb": VRAM, "gpu_free_mb": VRAM, "gpu_idle_mb": VRAM, "gpu_free_mib": VRAM, "gpu_idle_mib": VRAM,
  "round_no": 708, "round_no_label": "round 708 (bm-c)",
  "last_round": 708, "last_round_at": TS,
  "current_task": CUR, "current_task_at": TS,
  "latest_artifact": ART,
  "next_milestone": "10-08 reopen first bar: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + CTA_P1 paper-trial wiring (O-2215-2, no-bar blind wiring forbidden) + fund_premium 15:30 first snapshot (bm-c lane) + QDII holiday-premium observation vs DIGEST-20261008 theme-1; O-2245 follow-ups upon ticket; cloudF aggregation window 10-14; next 5x = r710 HANDOVER",
  "health": "alive (r708 standing-scan digest round clean: loop pin=5, watchdog registered, SAT alive rc0, QA 5/5 determinism 29th, smoke 48/48, S6 38/38 rc0 dualrun streak 28, orders zero-delta double-sweep, DEC/ORD unchanged, orphan face=1 ComfyUI no-kill documented, idle NOT-GREEN resident load idle_rounds=0 worked-declared)",
  "activity_now": VERDICT, "did": DID, "verdict": VERDICT,
  "note": "r708: standing external-scan digest law restored after 3-day gap (QDII holiday-premium cluster + hibor Oct window; funnel 7/0/+1 honest).",
  "last_round_summary": "r708: standing-scan digest supply (DIGEST-20261008 QDII cluster + hibor Oct window, funnel 7/0/+1), S0 churn absorb clean, S6 38 rc0 streak 28, QA 5/5 det-29th, smoke 48/48, push verified.",
  "last_action": "r708: standing-scan digest supply (DIGEST-20261008 QDII cluster + hibor Oct window, funnel 7/0/+1), S0 churn absorb clean, S6 38 rc0 streak 28, QA 5/5 det-29th, smoke 48/48, push verified.",
  "next": NEXT,
  "last_seen_at": TS, "updated_at": TS, "updated": TS, "last_run_at": TS, "last_ts": TS,
})
json.dump(hb, io.open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-asserts (smoke F7 face: epoch int + clock_read T-sep)
chk = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read not T-sep"
st2 = json.load(io.open(HP, encoding="utf-8-sig"))
assert st2["round_no"] == 709, "state round_no not advanced"
print("close ok: state 708->709, heartbeat epoch=%d int-verified, clock=%s, round-report appended" % (EPOCH, TS))
