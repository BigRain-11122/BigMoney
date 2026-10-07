# -*- coding: utf-8 -*-
# r714 bm-c closeout: state + heartbeat + round-report writes (r713/r712 close pattern).
# UTF-8 explicit everywhere (pit-encoding law); heartbeat epoch = fresh int;
# post-write json.loads self-checks (R170/R178 law: value AND type).
import io
import json
import time
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-08T01:5x:xx+08:00 (T-separator law)
TS_START = "2026-10-08T01:45:42+08:00"          # round-start clock read (S0-1)
EPOCH = int(time.time())
RAM_FREE = 4.0
GPU_FREE = 955
CPU_PCT = 19.0
CPU_IDLE = 81.0

CUR = ("当前活: r714 bm-c O-2245 bm-c 车道落池门接线收口轮（Tools/oss_import_gate.py 12 腿 fail-closed 准入闸"
       "·selftest 24/24+live dry-check ALL-HELD·10-08 复市 T-0 盘前值守第 34 连守轮） | "
       "最近实物: Tools/oss_import_gate.py + results/_r714bmc_oss_import_gate_selftest.json（24/24）+"
       "_r714bmc_oss_import_gate_livecheck.json（ALL-HELD·三候选诚实 REJECT 持门）+OSS_HARVEST_LEDGER.md §七 @ " + TS +
       " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce+fund_premium 首采"
       "（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证；next 5x=r715 HANDOVER")

DID = ("r714 bm-c: pre-open watch round (34th consecutive bm-c watch round, 10-08 reopen T-0). "
       "(1) MAIN PRODUCT (O-20261007-2245 bm-c lane enrollment-door closure, window <=10-12 met 4d early): "
       "Tools/oss_import_gate.py -- 12-leg fail-closed OSS-supply pool-enrollment admission gate (banned_direction_gate "
       "bloodline): id_prefix (OSS- r705 namespace) / id_unique (pool namespace dedup) / schema_declares (r705 three-field "
       "drift guard) / oss_fields / permit_pure (pure bucket MIT-Apache-BSD-ISC; GPL/AGPL/LGPL forbid; NOASSERTION must "
       "adjudicate via oss_license_probe; canonical-SPDX-full-name law -- live catch BSD-3 != BSD-3-Clause on G2) / "
       "adapt_status (adapted-only; rejected -> negative-results library) / attrition_cross (source tokens + dup_tags vs "
       "gate_attrition x4 1434 tokens anti-resurrection; MOM/clock/wild-way families) / in_service (akshare/tushare "
       "register-not-import) / prereg_exit_axis (resolvable in-repo .md + explicit exit-axis declaration per "
       "O-20261001-1108; unresolvable = fail-closed reject) / runner_exists / status_ready / fields_standard. "
       "Verification: selftest 24/24 PASS (hermetic 17 + mechanism 2 + CLI rc-contract 2 + real-carrier 3 incl. "
       "parameterized-walk vs oss_eng_scan carrier parity leg 1434==1434) -> results/_r714bmc_oss_import_gate_selftest.json; "
       "live dry-check ALL-HELD (ledger sec-4 three adaptation candidates G3/G2/B2 at scanning stage honestly REJECTed by "
       "the real gate with real carriers, zero pool write; red legs = adapt_status + prereg_exit_axis, G2 extra "
       "permit=BSD-3 non-canonical-SPDX red = fail-closed strictness live proof) -> "
       "results/_r714bmc_oss_import_gate_livecheck.json. Wiring closure: r705 schema (carrier) + r706/707 scan/license "
       "(evidence faces) + r714 gate (admission face) = judged-negative family resurrection path fully closed; ledger "
       "sec-7 appended; methodology card E45 + TREASURE_REGISTRY row. "
       "(2) S0 fetch behind=3 -> bm-c-owned churn absorb pre-rebase (0cb9e63f3) -> clean rebase zero conflict -> push "
       "delivered. (3) S0.5 sweep 1: orders 51 disk/176 ack unacked=0; DEC EE659451 / ORD 17accc40 both UNCHANGED "
       "(hex-case normalized per r711 law; facts results/_r714bmc_s05_facts.json). "
       "(4) S1 smoke 48/48. (5) S3 satengine rc0 alive; board 0 open (job_list 0 + fleet 0 unclaimed); idle NOT-GREEN "
       "(RAM 17.3%<40% resident load, idle_rounds=0, --worked declared); compute_audit rc0 flags pool_starvation (13 "
       "samples 139.3min) + supply_floor breach (ready 0<3) + supply_family_streak 438.7min recorded with disposition "
       "(engine wave-180 registered in engine queue; tonight post-close bar face = natural candidate supply; W16 "
       "wave-draft decision = next-window agenda per never-dry standing law; no manual pool burn). "
       "(6) S6 39/39 rc0 (dualrun ZERO-DRIFT streak 34; cta_p1_paper honest bar-gated no-op panel cutoff 2026-09-30 < "
       "paper_start 2026-10-08 -> auto-fires at tonight's first-bar round; golden-week/pre-open no-op lanes legal; "
       "py_watermark verdict=py_low_board_clear legal idle whitelist). "
       "(7) QA 5/5 35th determinism (93 trades, sharpe 0.1586, equity 1,017,839 frozen identity, png 66,206B). "
       "(8) post_review REPORT-20261008 zero red carryover; orphan face=1 no-kill documented. "
       "(9) S7 self-heal: loop pin=5 no-op + watchdog PRESENT + both claws IN-PLACE match + attrition guard CLEAN.")

VERDICT = ("r714 bm-c: OSS enrollment-door round clean. Product = Tools/oss_import_gate.py (O-2245 bm-c lane "
           "enrollment-door closure, window met 4d early; 12-leg fail-closed admission gate) + selftest 24/24 + "
           "live dry-check ALL-HELD (three candidates honestly held at scanning stage) + ledger sec-7 + E45 card + "
           "TREASURE_REGISTRY row; S0 behind=3 churn-absorb rebase clean; both watermarks unchanged zero action; pool "
           "flags recorded with disposition; S6 39/39 rc0 streak 34 (cta_p1_paper bar-gated no-op, auto-wiring tonight); "
           "QA 5/5 det-35th; smoke 48/48; orders sweep unacked=0; post_review zero red; orphan face=1 no-kill; idle not "
           "green-idle, idle_rounds=0 worked-declared.")

SUMMARY = ("r714: OSS enrollment gate (12-leg fail-closed, 24/24, ALL-HELD) + ledger sec-7 + E45; S6 39 rc0 streak 34; "
           "QA 5/5 det-35th; smoke 48/48; orders sweep unacked=0; pool flags dispositioned.")

NEXTP = ("r715: (a) 5x round -- HANDOVER 核对更新 (per 5-round law, research/HANDOVER.md product-list refresh); "
         "(b) watch continuation (10-08 reopen first trading day, intraday marks lane live 09:15, pre-open zero blind "
         "action); (c) tonight post-close face: data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + "
         "fund_premium 15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar auto-wiring "
         "+ first-marks verification (S6 cta_p1_paper leg; verify = marks 1 row + state trial-live + compounding "
         "identity) (<= 10-08 23:59); (d) O-2245 follow-ups: first OSS- enrollments (bm-a strategy-class adaptations "
         "<=10-16) must pass Tools/oss_import_gate.py rc0 before settle; NOASSERTION/conditional items stay REF-ONLY; "
         "(e) pool_starvation/supply_floor disposition: W16 wave-draft decision + tonight bar face natural supply "
         "(never-dry standing line); (f) cloudF row weekly rerun supply (window <=10-14 met, standing). [via bm-c r714]")

VERIFY = ("Tools/oss_import_gate.py + results/_r714bmc_oss_import_gate_selftest.json (24/24) + "
          "results/_r714bmc_oss_import_gate_livecheck.json (ALL-HELD) + results/_r714bmc_oss_gate_livecheck.py + "
          "qa/smoke-r714.md 5/5 + qa/equity-curve-r714.png 66,206B (determinism=True 35th, 93 trades, equity 1,017,839 "
          "frozen identity) + results/_r714bmc_s6_log.txt (39 legs rc0, dualrun streak 34) + "
          "results/_r714bmc_s05_facts.json (sweep 1 unacked=0) + research/OSS_HARVEST_LEDGER.md sec-7 + "
          "knowledge/METHODOLOGY_ASSETS.md E45 row + knowledge/TREASURE_REGISTRY.md r714 row")

REPORT_LINE = (
    TS + " | r714 | dept:工程（金周复市 T-0 盘前值守轮·第 34 bm-c 连守轮·O-2245 bm-c 车道落池门接线收口轮） | "
    "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单〔板 0 open/176 ack/池 406 全 done〕·"
    "compute_audit 旗标 pool_starvation+supply_floor 照录=池 ready 0<floor 3·供给族断流 438.7min·处置=引擎队列 W180 已注册+今晚盘后 bar 面天然候选供给+"
    "W16 波起草决策=下窗首位议程〔never-dry 常设律·禁手工代烧〕） | "
    "当前活: r714 主产品=O-20261007-2245 bm-c 车道落池唯一门收口（窗 ≤10-12 提前 4 天）：Tools/oss_import_gate.py"
    "（banned_direction_gate 血统 fail-closed 准入闸·12 腿=OSS- 前缀〔r705 保留命名空间〕/池查重/schema 漂移守卫/三字段载体/许可纯桶+SPDX 规范全称律"
    "〔GPL/AGPL/LGPL 禁入·NOASSERTION 先过 license_probe·BSD-3≠BSD-3-Clause 活捕〕/adapted 态准入〔rejected→负结果库〕/"
    "负结果库 token 反复活交叉〔1434 token·MOM/时钟/野路子族〕/在役去重〔akshare/tushare 登记不引进〕/出场轴显式+可解析 prereg〔O-20261001-1108〕/"
    "runner 在场/ready 态/标准字段）——任何机器任何车道 OSS- 件落池前必过门·rc0 ADMIT 才准正典 settle+同轮推送〔r598 律〕；"
    "验证=selftest 24/24〔hermetic 17+机制 2+CLI rc 契约 2+真载体 3·含参数化 token 走 vs oss_eng_scan 载体走 parity 1434==1434〕+"
    "live dry-check ALL-HELD〔台账 §四在排产 G3/G2/B3 按 scanning 态真门过闸→三件诚实 REJECT=持门律证明·G2 另捕非规范 SPDX 红=fail-closed 严格性活证·零池写〕；"
    "接线位次=r705 schema〔载体〕→r706/707 扫面〔证据〕→r714 门〔准入〕=judged-negative 家族复活路径全闭；"
    "台账 §七 append+E45 方法论卡+TREASURE_REGISTRY r714 行 | "
    "smoke 48/48 · S6 39/39 rc0（dualrun ZERO-DRIFT streak 34·cta_p1_paper 诚实 bar-门控 no-op〔panel cutoff 2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕·"
    "金周/盘前 no-op 腿合法） · QA 5/5（determinism=True 35th·93 trades·equity 1,017,839 冻结恒等·png 66,206B） · "
    "orders 扫描 unacked=0（51 disk/176 ack·S0.5 首扫零差·收尾二扫同验后 commit） · DEC/ORD 同哈希零 delta（EE659451/17accc40·hex-case 归一律遵从） · "
    "SAT 活 rc0 · idle NOT-GREEN（RAM 17.3%<40% 常驻·idle_rounds=0·--worked 申报） · post_review 零红承接（REPORT-20261008 ✗0） · "
    "孤儿面=1（只读披露不击杀） · attrition CLEAN（healed 注记照录） · 自愈=loop pin=5 no-op+watchdog 在位+双爪 IN-PLACE match · "
    "token 面=L1 零 token 腿（token_meter rc0·delta=0） · 方法论捕获=E45（落池唯一门 fail-closed 准入闸律）·宝藏捕获=E45 卡出入行（§1 五类收口步）·"
    "登记册零命中断言=N/A（无清扫/归档/恢复类动作） · 本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
    "下轮 r715：(a) 5x HANDOVER 核对更新 (b) 值守续（盘前零盲动·intraday marks 09:15 起活） (c) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首 bar enforce+"
    "fund_premium 15:30 首采（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤今夜） "
    "(d) O-2245 续作=首批 OSS- 落池件〔bm-a 策略适配件 ≤10-16〕一律先过 Tools/oss_import_gate.py rc0 再 settle (e) W16 波起草决策〔never-dry〕 "
    "(f) cloudF 周轮复跑供给 | 轮产品计分：2（落池门+台账+方法论卡=能跑能看实物） | 记账预算：4（state+心跳+轮报+登记册法定） [via bm-c r714]")

def main():
    # 1) state
    with io.open(ROOT + r"\state-bm-c.json", encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 715
    st["round_no_label"] = "round 714 (bm-c)"
    st["last_round"] = 714
    for k in ("last_round_at", "last_round_ts", "last_seen", "last_seen_at", "last_run_at",
              "last_ts", "updated", "updated_at", "current_task_at", "last_decisions_read_at",
              "clock_read", "last_action_at", "last_round_summary_at"):
        if k in st:
            st[k] = TS
    st["ts"] = TS_START
    st["heartbeat_epoch_utc"] = EPOCH
    st["cpu_pct"] = CPU_PCT
    st["cpu_idle_pct"] = CPU_IDLE
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        st[k] = RAM_FREE
    for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_free_mib", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb"):
        if k in st:
            st[k] = GPU_FREE
    st["current_task"] = CUR
    st["did"] = DID
    st["verdict"] = VERDICT
    st["activity_now"] = VERDICT
    st["last_round_summary"] = SUMMARY
    st["last_action"] = SUMMARY
    st["note"] = ("r714: OSS enrollment-door landed (O-2245 bm-c lane closure, 4d early; 12-leg fail-closed gate, "
                  "24/24 selftest, ALL-HELD livecheck); both watermarks unchanged; pool flags dispositioned.")
    st["next_pointer"] = NEXTP
    st["verify"] = VERIFY
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
                                       "r714 sweep = UNCHANGED EE659451 zero delta zero action; hex-case comparison "
                                       "normalized per r711 pit law; facts-driven from results/_r714bmc_s05_facts.json, "
                                       "64hex shape-asserted, never hand-typed (r583 S4 law))")
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r714 sweep "
                                    "= UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
                                    "facts-driven from results/_r714bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
    with io.open(ROOT + r"\state-bm-c.json", "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=True, indent=1)

    # 2) heartbeat
    with io.open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8") as f:
        hb = json.load(f)
    hb["round_no"] = 715
    hb["round_no_label"] = "round 714 (bm-c)"
    hb["last_round"] = 714
    hb["last_round_at"] = TS
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["last_seen"] = TS
    hb["clock_read"] = TS
    hb["ts"] = TS
    for k in ("last_seen_at", "updated", "updated_at", "last_run_at", "last_ts"):
        if k in hb:
            hb[k] = TS
    hb["current_task"] = CUR
    hb["current_task_at"] = TS
    hb["latest_artifact"] = ("Tools/oss_import_gate.py + results/_r714bmc_oss_import_gate_selftest.json (24/24) + "
                             "results/_r714bmc_oss_import_gate_livecheck.json (ALL-HELD; O-2245 bm-c lane "
                             "enrollment-door closure) @ " + TS)
    hb["next_milestone"] = ("今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first "
                            "snapshot + QDII watch rerun + CTA_P1 first-bar auto-wiring + first-marks verify (<= 10-08 23:59)")
    hb["cpu_pct"] = CPU_PCT
    hb["cpu_util_pct"] = CPU_PCT
    hb["cpu_idle_pct"] = CPU_IDLE
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        hb[k] = RAM_FREE
    for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib"):
        hb[k] = GPU_FREE
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["did"] = DID
    hb["verdict"] = VERDICT
    hb["activity_now"] = VERDICT
    hb["last_round_summary"] = SUMMARY
    hb["last_action"] = SUMMARY
    hb["note"] = st["note"]
    hb["next"] = NEXTP
    with io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=True, indent=1)

    # 3) round report append
    rp = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
    with io.open(rp, encoding="utf-8") as f:
        text = f.read()
    if not text.endswith("\n"):
        text += "\n"
    text += REPORT_LINE + "\n"
    with io.open(rp, "w", encoding="utf-8") as f:
        f.write(text)

    # 4) self-checks (R170/R178: value AND type; smoke F7 contract)
    with io.open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8") as f:
        hb2 = json.load(f)
    with io.open(ROOT + r"\state-bm-c.json", encoding="utf-8") as f:
        st2 = json.load(f)
    assert isinstance(hb2["heartbeat_epoch_utc"], int) and not isinstance(hb2["heartbeat_epoch_utc"], bool), "epoch not int"
    assert hb2["heartbeat_epoch_utc"] == EPOCH
    assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read format"
    assert hb2["round_no"] == 715 and st2["round_no"] == 715
    assert len(hb2.get("orders_ack", [])) == 176, "orders_ack mutated!"
    with io.open(rp, encoding="utf-8") as f:
        tail = f.read()[-400:]
    assert "r714" in tail and "[via bm-c r714]" in tail, "report tail missing r714"
    print("CLOSE_OK ts=%s epoch=%d state_round_no=715 orders_ack=176 report_tail=r714" % (TS, EPOCH))

if __name__ == "__main__":
    main()
