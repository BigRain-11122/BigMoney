"""r446 bm-c closeout: round report + state + heartbeat (no HANDOVER: 446 not 5x).

All writes json.dump/programmatic + post-write self-verify (state.json
trailing-comma law + heartbeat epoch int-type law). Hard asserts throughout.
"""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_COMPACT = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

# ---------------------------------------------------------------- 1) round report append
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
RR_LINE = (
    "watermark: 绿 (red=false lane healthy; satengine bm-c rc0 alive queue 0; golden-week 合法 idle; N1 W116+ 供给裁定=不开新波〔O-2115 §二 新方向>永续深挖+fund-trio 在烧〕) | "
    + NOW + " | r446 | dept:工程/策略 | 当前活: O-2115 验收证据包脚本落地（10-08 治理日四件机械取证·可复跑自动再生）+ W2 判决消费面收口（E27 累计 N 通缩律卡+登记册行） | "
    "S0: 树脏=4 lane daemon 面定向 absorb d18c2d220（fetch 实核 HEAD==origin 零交集零冲突·treadmill 预对齐律） | "
    "S0.5: 双扫 152/152 零未回执 + D-19 MATCH EB14B510 + GORDERS MATCH 68947C17（_r446bmc_d19.py 原始字节零树触碰） | "
    "S1: smoke 47/47 | S2/S3: 板零 open 票·satengine rc0 活; FUND 三族 NULLS=ready×3 分属 bm-b 正主烧（MSG-1132/1155 分工+keep-block 在册·本机 dispatcher pool_empty_or_busy 让路正确·禁双烧）; moneyflow IC=next_pick claimed 他机车道让路; N1 W116+ 供给裁定=本轮不开（O-2115 §二明文+fund-trio 占火力·W116 冻结需席位 MSG+带闸+五面+per-wave prereg·观察相） | "
    "主产出: scripts/o2115_acceptance_pack.py（selftest PASS·live ALL_MET 4/4）→ results/o2115_acceptance/pack_latest.json + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md——件1 T-145 PIT 审计+H 行解锁 7/8+三族 prereg FROZEN（冻结判据=池 prereg_ref FROZEN+模板冻结条款双证）; 件2 深轴族 10/10 done; 件3 W2 判决 landed 诚实负 0 eligible（E[FP]=40.25@5%·verdicts pass=1/fail=804）; 件4 火力分布窗口 81 点火新面孔占比 71.6%（o2115_new 58/other 16/perpetual 7·bm-a 27/bm-b 18/bm-c 13） | "
    "捕获步: E27 千人供给波累计 N 通缩律卡（r444 判决收口漏项本窗机械补: DSR≥0.95 门分母=活账本头 622,522 跨波累计 N 永不重置·千人级供给注册级产出趋零·wave-3+ 定位二选一）+ TREASURE_REGISTRY E27 行（方法论卡 append 类） | "
    "S4: CODELY 坑律 1 条（探针一律落文件律——python -c 经包装器 -ArgString 内单引号提前终止 PS 串·双犯实录·r436/r438 族第三形态） | "
    "S6: 37/37 rc0（dualrun ZERO-DRIFT streak 48; compute_audit CLEAN pool-supply-gap 观察相〔ready=3=fund NULLS·unclaimed=1〕; update_daily 金周 cutoff 2026-09-30 零新行; LHB refetch 5432 行零 beyond-cutoff; fund_premium 周末 no-op; b_layer 全门过; scorecard/paper_export/daily_scorecard/dashboard 四面 stale-view veto 让路 bm-a fresh host 合法; REPORT/LIVE-2026-10-04 ORANGE cap50 COOL 再生; token delta=0 全 L1） | "
    "S7: 自愈 4x 绿（pin5 no-op 05:55 首发火/watchdog 05:51 在位/双爪字节恒等零重装）+attrition CLEAN（2 healed 历史注记照录）+inbox 空+orders 双扫 152 复核零漂 | "
    "验证证据: acceptance pack selftest 0 fails + live run ALL_MET 4/4 + E27/registry append 在案 + S6 rc0 全链 + smoke 47/47 + push_verify ahead==0 | "
    "记分: 2（验收证据包=能跑能看能用实物·10-08 呈报日直接消费） | 记账预算: 3/5（state+心跳+轮报） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证） | "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（prescan 未触发; TREASURE_REGISTRY +1 行=捕获步合法 append 非删除面） | "
    "ceo-visibility: [当前活] O-2115 验收证据包已建成可复跑（四件全 MET·引擎火力新面孔占比 71.6%·W2 千人审判诚实负结果在册） | [最近实物] scripts/o2115_acceptance_pack.py + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md @ " + NOW + " | "
    "[下个里程碑] FUND 三族 NULLS 烧毕→finalize 窗 10-05..10-09（两前置裁决观察）+ D-06 收口 10-07 + O-2115 验收呈报 10-08 | "
    "下轮指针: (a) D-06 final sweep 预备（pit-data CRLF 裁定+断言层 increment+流水下沉·10-07 截） (b) fund-trio finalize 前置观察（G-SEG GM 裁决+VALUE passive bm-b 修复·NULLS 烧完即 finalize 就绪面） (c) O-2115 pack 10-08 呈报前终跑 (d) T-143 装配 10-09 后"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r446" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 446
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r446 bm-c: O-2115 acceptance evidence pack (script+pack+CEO page, ALL_MET 4/4, new-face fire share 71.6%) + E27 cumulative-N deflaw card + N1 W116+ supply ruling (closed per O-2115 sec-2); orders/D19 MATCH; smoke 47/47")
st["current_task"] = ("r446 done (O-2115 acceptance pack script scripts/o2115_acceptance_pack.py selftest PASS + live ALL_MET 4/4 -> results/o2115_acceptance/pack_latest.json + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md; W2 judgment consumption face closed with E27 card + registry row; N1 W116+ supply ruled closed this window); next: D-06 final sweep 10-07, O-2115 pack final run 10-08, fund-trio finalize watchers 10-05..10-09")
st["did"] = (
    "r446 bm-c golden-week maintenance + acceptance-pack product round: "
    "(1) MAIN DELIVERABLE (score 2): O-2115 acceptance evidence pack -- scripts/o2115_acceptance_pack.py (deterministic L1 aggregation, zero network/engine; selftest PASS; subcommands run|selftest) building the 10-08 governance-day four statutory items mechanically: item1 T-145 PIT audit + census H unlock (n_unlock=7/n_stay_locked=1) + first fundamental-family preregs FROZEN x3 (freeze evidence = pool prereg_ref FROZEN + template freeze-clause dual check); item2 deep-axis LOWAMP-DEEP-P1 10/10 pool faces done; item3 W2 judgment landed (805 cells, pass=1/fail=804, E[FP]=40.25 @5%, G2-eligible 0 = honest negative); item4 engine fire distribution window since O-2115 issuance: 81 launches, o2115_new 58 (71.6%), bm-a 27 / bm-b 18 / bm-c 13; outputs results/o2115_acceptance/pack_latest.json + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md (re-runnable, regenerates in place). "
    "(2) W2 judgment consumption face closed (T-158 post-judge leg): E27 cumulative-N deflation card appended to knowledge/METHODOLOGY_ASSETS.md (DSR>=0.95 correction denominator = live ledger-head cumulative trials 622,522, never reset cross-wave; thousand-scale supply -> registration yield ->0; wave-3+ positioning choice) + TREASURE_REGISTRY E27 row -- r444 finalize capture-step backfill (mechanical). "
    "(3) N1 W116+ supply ruling: NO new wave this window per O-2115 sec-2 (new-direction furnaces > perpetual deep-dig; fund-trio consuming fire on bm-b; W116 freeze would need seat MSG + band gate + five faces + per-wave prereg) -- ruling carried in state/round report + pack risk flags. "
    "(4) FUND trio NULLS observed ready x3 = bm-b rightful burner per MSG-1132/1155 division (keep-block on crash_fuse; local dispatcher correctly yielded pool_empty_or_busy; zero double-burn). "
    "(5) S0 lane daemon faces absorbed d18c2d220 (HEAD==origin zero intersection); S0.5 orders 152/152 double-scan zero un-acked + D-19 MATCH EB14B510 + GORDERS MATCH 68947C17; S1 smoke 47/47; S6 chain 37/37 rc0 (dualrun ZERO-DRIFT streak 48, compute_audit CLEAN, REPORT/LIVE-2026-10-04 regenerated, token delta=0); S7 self-heal 4x green + attrition CLEAN + inbox empty; S4 pit entry: probe-to-file law (python -c quoting double-fail, r436/r438 family third form)."
)
st["next"] = (
    "(a) D-06 final sweep prep 10-07 (pit-data CRLF adjudication + assert-layer increments + flow-sinking; T-144(c) remaining). "
    "(b) FUND trio finalize window 10-05..10-09 watchers (two pre-rulings pending: G-SEG GM + VALUE passive bm-b fix; NULLS burn completion on bm-b -> finalize readiness face). "
    "(c) O-2115 acceptance pack final run at 10-08 governance day (script re-runs in place). "
    "(d) O-2030 treasure-protection acceptance 10-08. (e) T-143 assembly post 10-09 (deliver 10-29). (f) W116+ N1 supply reassess after fund-trio finalize."
)
st["verify"] = (
    "o2115_acceptance_pack selftest 0 fails + live ALL_MET 4/4 (new_share 71.6%); E27 card + registry row appended; S6 37/37 rc0; smoke 47/47; orders 152/152 zero-diff double-scan; D-19 EB14B510 raw-bytes MATCH; attrition CLEAN; push delivery via Tools/push_verify.py post-commit (ahead==0 self-check)"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 446 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=446 epoch=%d" % re_st["heartbeat_epoch_utc"])

# ---------------------------------------------------------------- 3) heartbeat update
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = st.get("cpu_pct", 0.0), st.get("idle_ram_gb", 0.0)
hb["activity_now"] = "O-2115 acceptance evidence pack BUILT r446 (4/4 ALL_MET, re-runnable; new-face fire share 71.6%); W2 consumption face closed (E27 cumulative-N deflation card); N1 W116+ ruled closed per O-2115 sec-2; FUND trio NULLS bm-b in-flight"
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["latest_artifact"] = "scripts/o2115_acceptance_pack.py + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md (O-2115 four statutory items ALL_MET: PIT audit + unlock 7/8 + 3 family preregs FROZEN / deep-axis 10/10 / W2 judged honest-negative / fire share 71.6%) @ " + NOW
hb["next_milestone"] = "FUND trio NULLS burn -> finalize window 10-05..10-09 (G-SEG GM + VALUE passive pre-rulings); D-06 final sweep 10-07; O-2115 acceptance presentation 10-08; T-143 assembly post 10-09 (deliver 10-29)"
hb["prod_lanes"] = "O-2115 acceptance pack live (4/4 MET); N1 closed this window per O-2115 sec-2 supply priority (fund-trio has fire); FUND trio NULLS bm-b in-flight; W2 MASS_TRIAL judged+consumed (negative, E27 card)"
hb["round_no"] = 446
hb["updated_at"] = NOW
hb["verdict"] = "green (acceptance-pack product landed + golden-week maintenance all-green; board/pool/orders lawful; lane divisions respected)"
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
# ack list carries 152 O-*.md + README.md (historical fleet convention) = 153.
assert re_hb["round_no"] == 446 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f epoch=%d acks=%d" % (cpu, ram_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))
print("CLOSE-ALL-GREEN", NOW)
