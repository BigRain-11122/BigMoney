"""r665 closeout: state bump (665->666) + heartbeat refresh + round-report line.
All writes programmatic with strict json.loads self-proofs (epoch int + T-clock law).
"""
import io
import json
import time

# --- state-bm-a.json: round_no bump ---
SP = "state-bm-a.json"
s = json.load(io.open(SP, encoding="utf-8"))
assert s["round_no"] == 665, f"unexpected round_no {s['round_no']}"
s["round_no"] = 666
with io.open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
s2 = json.load(io.open(SP, encoding="utf-8"))
assert s2["round_no"] == 666
print("state round_no 665->666 OK")

# --- heartbeat fleet/machines/bm-a.json ---
HP = "fleet/machines/bm-a.json"
h = json.load(io.open(HP, encoding="utf-8"))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["cpu_cores"] = 32
h["cpu_pct"] = 2.0
h["free_ram_gb"] = 59.6
h["gpu_free_vram_gb"] = 5.5
h["current_task"] = ("theme line R6 start-face grid probe delivered (fast10 7/16@pm10td, E29+sec9 canon); "
                     "fund trio NULLS bm-b in-flight watch (V/Q/D burns advancing); T-166 fund-statement "
                     "backfill advancing in background (148/258 staging)")
h["verdict"] = ("GREEN (smoke 48/48; S6 37/37 rc0 dualrun streak41; theme R6 start-face probe + E29 card + "
                "THEME_EVENT_LIBRARY sec9 delivered; O-20261004-0808 orbit: W14 park + G-SEG freeze maintained; "
                "fund trio NULLS bm-b canonical in-flight keepalive; T-166 backfill advancing; watermark red=false)")
with io.open(HP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
h2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int)
assert "T" in h2["clock_read"] and "+" in h2["clock_read"]
print("heartbeat OK epoch=", h2["heartbeat_epoch_utc"], "clock=", h2["clock_read"])

# --- round report line ---
RP = "round_reports-bm-a.md"
line = (
    "watermark: green (red=false; probe py_low_board_clear golden-week legal idle window; satengine alive rc0 queue 0; "
    "pool active 4 = W14 GM-parked + fund trio NULLS bm-b canonical in-flight keepalive 08:08 (V646/Q492/D352 of 2000 at leg-check, dup_k=0, bm-a fuse keep-block = designed face); "
    "compute_audit CLEAN flags=[]; T-166 fund-statement backfill advancing in background 148/258 staging lock-alive) "
    "| 2026-10-04T08:4x+08:00 | r665 | dept:研究 | 当前活: 题材线 R6 起点探测面网格普查落地——E28 滞后确认律的廉价下一刀："
    "16 CEO 锚 × 4 冻结候选起点面（nearlimit7/volstart/break60/fast10）锚格网格，主判 ±10td+对照 ±30cal，B0=v0.3 爆发规则引用不重算；"
    "首过发现：fast10（10td≥+10%）=最优起点面 7/16@±10td（中位 +2td）vs B0 2/16@±30cal；volstart/break60 早火但散（中位 −21/−24td）=早期预警非紧起点；"
    "nearlimit7 仅 4/16（ETF 题材启动少以近涨停开场）；锚双面性：4/5 窗外火为早火（−30..−56td）——机械起点可早于 CEO 共识锚数周，"
    "未来起点判据 prereg 须先裁定锚真值口径或用非对称容差禁对称 ±N；4 无起火（慢烧/代理晚面）如实披露 | "
    "S0: fetch behind=0 零动作（脏面=本地 daemon 生成面零交集）；S0.5 orders 双扫口径坑当场自纠（前缀/裸名两口径 r646 律）153/153 零未回执；"
    "D-19 decisions sha MATCH eb14b510 零新决策行（desktop 实径 fetch+show 原字节法·K: 缺中 S4U 窗）；S1 smoke 48/48 | "
    "验证证据: probe selftest 13/13（合成腿 <MIN_PRIOR 索引坑自检当场抓回修复后全绿）+确定性双跑实链 + 16×4 网格产物五件在盘 + "
    "THEME_EVENT_LIBRARY §九 + METHODOLOGY E29 卡 + TREASURE 行 + T-165 票面 progress_r665；S6 37/37 腿 rc0 110.2s "
    "(_r665bma_s6_log.txt; dualrun ZERO-DRIFT streak41; CALL ORANGE_COOL sleeves4 activated0; LIVE-20261004 ORANGE cap50; "
    "REPORT-20261004 faces5 token=1; t35 PASS 0 pending; 金周采集腿全合法 no-op; alloc_paper=bm-b 车道诚实 no-op; "
    "live.paper 系腿金周无新 bar 诚实跳过 r660 判例) | S7 4/4 (loop pin8 no-op + watchdog 重注 + 双爪 CR 归一 MATCH r662 探针复用 + "
    "attrition CLEAN 4 台账 healed 注记照录) + inbox 零未读 + state strict json.loads 自证 + 心跳 epoch int 自证 | "
    "记分: 2（可跑探针脚本+网格数据实物+正典三件=CEO 点名 T1 研究线 R6 实物）| 记账预算: 4/5（state+心跳+轮报告+票面）| "
    "本地未达 origin commit 数: 0（收尾 push 后 push_verify 自证）| "
    "ceo-visibility: [当前活] 题材战法研究线 R6 落地：16 个 CEO 题材锚上试了 4 类早期探测器，找到最强起点面 fast10（7/16 命中锚 ±10 交易日·中位 +2td），"
    "并发现 4 个「早火」比 CEO 共识锚早 1-2 个月——起点判据须先裁定锚真值口径 [最近实物] results/theme_ring/theme_ignition_face_probe.json+csv（16×4 网格·08:3x）+ "
    "scripts/theme_ignition_face_probe.py + THEME_EVENT_LIBRARY.md §九 + LIVE-2026-10-04 CEO 一页纸 [下个里程碑] 10-05 基金三族 V-NULLS 烧完→judged finalize 窗开（预演 ALL-GREEN x3 就绪·<=48h 首节点）; "
    "10-06..07 T-166 财报面板完备翻牌（148/258 推进中）; 10-08 开市窗 run-11/run-7 双腿\n"
)
line = line.rstrip("\n").rstrip() + "\n"
with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report r665 line appended")
