# -*- coding: utf-8 -*-
# r712 bm-c closeout: state + heartbeat + round-report writes (r674/r675 close pattern).
# UTF-8 explicit everywhere (pit-encoding law); heartbeat epoch = fresh int;
# post-write json.loads self-checks (R170/R178 law: value AND type).
import io
import json
import time
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-08T01:14:xx+08:00 (T-separator law)
TS_START = "2026-10-08T01:06:07+08:00"          # round-start clock read (S0-1)
EPOCH = int(time.time())
RAM_FREE = 4.0
GPU_FREE = 955
CPU_PCT = 19.0
CPU_IDLE = 81.0

CUR = ("当前活: r712 bm-c cloudF 聚合面补呈+D-20261008-01② 自翻收口轮（10-08 复市首交易日盘前值守·第 32 bm-c 连守轮）"
       " | 最近实物: results/cloudf_face_row.py+results/cloudf_face_row.json+HQ-FEEDBACK.md F-20261008-01 行"
       "（D-20261007-06 C-01 缺口补呈·278 单聚合·attribution CLEAN 缺值 0） @ " + TS +
       " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce+fund_premium 首采"
       "（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 有 bar 接线（O-2607-2 禁盲接·窗 ≤今夜）；next 5x=r715 HANDOVER")
CUR = CUR.replace("O-2607-2", "O-2215-2")

DID = ("r712 bm-c: pre-open watch round (32nd consecutive bm-c watch round, T-0 morning). "
       "(1) MAIN PRODUCTS: [a] D-20261007-06 C-01 gap cloudF aggregation row delivered 6 days ahead of the <=10-14 window -- "
       "results/cloudf_face_row.py (L1 zero-network zero-LLM zero-judgment rerunnable aggregator over the fleet-sole "
       "cloud-emission ledger cloudF-queue-c.jsonl, U218 antenna law) + results/cloudf_face_row.json (278 orders: "
       "done 230/pending 37/error 6/superseded 5; per-entity MiniGame 53/G17 47/G09 61/G10 45/Biggame 25 all-pending/"
       "G21 27/G12 7/G08 4/G04 4/FluxVerse 2/G03 2/G18 1; attribution 3-field CLEAN missing=0 = C-01(3) CLEAN-ZERO-STATE re-proof) "
       "+ HQ-FEEDBACK F-20261008-01 presentation row (3 honest boundaries in-row). "
       "[b] D-20261008-01(2) consumed: F-20261007-01 subsidiary-face stale status self-flipped open->closed "
       "(r709 delta mislabel sank the obligation 4 rounds; new pit direct-written to research/pit-protocol-d19.md "
       "per r666/r669 precedent -- main file 30,266B red-line headroom 454B held). "
       "(2) S0 fetch behind=0/ahead=0 zero rebase; S0.5 double sweep: orders 51 disk/176 ack unacked=0 BOTH sweeps, "
       "DEC EE659451 / ORD 17accc40 both UNCHANGED both sweeps (hex-case normalized per r711 law; facts results/_r712bmc_s05_facts.json). "
       "(3) S1 smoke 48/48. (4) S3 satengine rc0 alive; board 0 open (job_list 0 + fleet 0 open); idle NOT-GREEN "
       "(RAM 19.2%<40% resident load, idle_rounds=0, --worked declared); compute_audit rc0 flags pool_starvation+supply_floor "
       "recorded with disposition (engine wave-180 registered in engine queue; tonight post-close bar face = natural candidate "
       "supply; W16 wave-draft decision = r713 top agenda per never-dry standing law; no manual pool burn). "
       "(5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 32; golden-week no-op legs legal, latest panel bar 2026-09-30 pre-open expected). "
       "(6) QA 5/5 33rd determinism (93 trades, sharpe 0.1586, equity 1,017,839 frozen identity, png 66,167B). "
       "(7) orphan face=1 ComfyUI idle server (CEO-owned, no-kill documented). "
       "(8) S7 self-heal: loop pin=5 no-op + watchdog PRESENT + both claws IN-PLACE + attrition guard CLEAN (4 healed notes).")

VERDICT = ("r712 bm-c: cloudF aggregation row + F-file self-flip round clean. Product = cloudF face row "
           "(D-20261007-06 C-01 gap, 6d ahead of <=10-14 window; aggregator + JSON + HQ-FEEDBACK row, 278 orders, "
           "attribution CLEAN) + D-20261008-01(2) F-20261007-01 stale status self-flip; D-19 both watermarks unchanged "
           "zero action both sweeps; pool_starvation/supply_floor flags recorded with disposition; S6 38/38 rc0 streak 32; "
           "QA 5/5 det-33rd; smoke 48/48; orders double-sweep unacked=0; orphan face=1 no-kill; idle not green-idle, "
           "idle_rounds=0 worked-declared.")

SUMMARY = ("r712: cloudF face row (278 orders, attribution CLEAN) + D-20261008-01(2) F-20261007-01 self-flip; "
           "S6 38 rc0 streak 32; QA 5/5 det-33rd; smoke 48/48; orders double-sweep unacked=0; pool flags recorded.")

NEXTP = ("r713: (a) pool_starvation/supply_floor flag disposition = W16 wave-draft decision TOP agenda (never-dry standing "
         "line; engine wave-180 registered in engine queue = engine-side supply; tonight post-close bar face = natural "
         "candidate supply); (b) watch continuation (10-08 reopen first trading day, intraday marks lane live 09:15, "
         "pre-open zero blind action); (c) evening post-close face: data-chain full re-arm + REGIME_GUARD v3 first-new-bar "
         "enforce + fund_premium 15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 bar-gated wiring "
         "(O-2215-2, GM-signed, no-bar blind wiring forbidden, window <= tonight); (d) cloudF row collection window <=10-14 "
         "(F-20261008-01 presented, @BigCompute row peer); weekly cloud rows = cloudf_face_row.py rerun supply; "
         "(e) O-2245 follow-ups upon ticket; (f) next 5x = r715 HANDOVER. [via bm-c r712]")

VERIFY = ("results/cloudf_face_row.py + results/cloudf_face_row.json (278-order aggregation, attribution CLEAN) + "
          "HQ-FEEDBACK.md F-20261008-01 row + F-20261007-01 status flip + qa/smoke-r712.md 5/5 + qa/equity-curve-r712.png "
          "66,167B (determinism=True 33rd, 93 trades, equity 1,017,839 frozen identity) + results/_r712bmc_s6_log.txt "
          "(38 legs rc0, dualrun streak 32) + results/_r712bmc_s05_facts.json (double-sweep identical, unacked=0) + "
          "research/pit-protocol-d19.md r712 pit entry (D-19 delta row-enumeration discipline)")

REPORT_LINE = (
    TS + " | r712 | dept:工程/总经办（金周复市 T-0 盘前值守轮·第 32 bm-c 连守轮·cloudF 聚合面补呈+司面状态自翻收口轮） | "
    "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单〔板 0 open/176 ack/池 406 全 done〕·"
    "compute_audit 旗标 pool_starvation+supply_floor 照录=池 ready 0<floor 3·供给断流 394.8min·处置=引擎队列 W180 已注册+今晚盘后 bar 面天然候选供给+"
    "W16 波起草决策=r713 首位议程〔never-dry 常设律·禁手工代烧〕） | "
    "当前活: r712 双件收口——①D-20261007-06 C-01 缺口补呈（窗 ≤10-14 提前 6 天）：results/cloudf_face_row.py"
    "（L1 零网络零 LLM 零判定可复跑聚合器·机队唯一云端发射台账 U218 天线律）+results/cloudf_face_row.json"
    "（278 单=done 230/pending 37/error 6/superseded 5·分实体 MiniGame 53/G17 47/G09 61/G10 45〔36/6/3〕/Biggame 25〔全 pending〕/"
    "G21 27〔13/12/2〕/G12 7/G08 4/G04 4/FluxVerse 2/G03 2/G18 1·attribution 三字段 CLEAN 缺值 0=C-01③ CLEAN-ZERO-STATE 复证）+"
    "HQ-FEEDBACK F-20261008-01 数据行（诚实边界 3 条：无时间戳零趋势宣称/计费任务代理口径禁换算/单位配额基线=BigCompute 成本账本域）"
    "②D-20261008-01 ② 消费：F-20261007-01 司面状态列 stale→closed 自翻（D-20261007-04① 提前核销为唯一权威）——"
    "r709 delta 误标（771c3a8d→EE659451 实为 10-08 批 D-01..04·注记误标 D-20261007-07+「无新增本司工程义务」误判）致本司义务漏检 4 轨=新坑直写 pit-protocol-d19.md"
    "（D-19 delta 行级列举纪律·主件 30,266B 余量 454B 红线·r666/r669 直写先例） | "
    "smoke 48/48 · S6 38/38 rc0（dualrun ZERO-DRIFT streak 32·金周 no-op 腿合法·latest panel bar 2026-09-30 盘前预期） · "
    "QA 5/5（determinism=True 33rd·93 trades·equity 1,017,839 冻结恒等·png 66,167B） · orders 双扫零差（51 disk/176 ack·unacked=0·首尾双扫同） · "
    "DEC/ORD 双扫同哈希零 delta（EE659451/17accc40·hex-case 归一律遵从） · SAT 活 rc0 · idle NOT-GREEN（RAM 19.2%<40% 常驻·idle_rounds=0·--worked 申报） · "
    "post_review 零红承接 r711 · 孤儿面=1（ComfyUI idle server·CEO 私产·只读披露不击杀） · attrition CLEAN（4 healed 注记照录） · "
    "自愈=loop pin=5 no-op+watchdog 在位+双爪 IN-PLACE · token 面=L1 零 token 腿（token_meter rc0·delta=0） · "
    "方法论捕获=无新方法（cloudF 聚合=纯测量复用）·宝藏捕获=N/A（无五类收口批）·登记册零命中断言=N/A（无清扫/归档/恢复类动作） · "
    "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
    "下轮 r713：(a) pool_starvation/supply_floor 旗标处置=W16 波起草决策首位议程（never-dry 常设线·引擎 W180 已注册·今晚盘后 bar 面=天然候选供给） "
    "(b) 值守续（盘前零盲动·intraday marks 09:15 起活） (c) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采（bm-c 车）+"
    "QDII watch 重跑长假差分+CTA_P1 有 bar 接线（O-2215-2 禁盲接） (d) cloudF 行收取面并卷 @BigCompute 同行（≤10-14）·周轮云端行=cloudf_face_row.py 复跑供给 "
    "(e) O-2245 待工单 (f) next 5x=r715 HANDOVER | 轮产品计分：2（cloudF 聚合器+数据行+自翻收口=能跑能看实物） | 记账预算：3（state+心跳+轮报法定） [via bm-c r712]")
REPORT_LINE = REPORT_LINE.replace("4 轨", "4 轮")  # typo guard

def main():
    # 1) state
    with io.open(ROOT + r"\state-bm-c.json", encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 713
    st["round_no_label"] = "round 712 (bm-c)"
    st["last_round"] = 712
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
    for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_free_mib", "gpu_idle_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb"):
        if k in st:
            st[k] = GPU_FREE
    st["current_task"] = CUR
    st["did"] = DID
    st["verdict"] = VERDICT
    st["activity_now"] = VERDICT
    st["last_round_summary"] = SUMMARY
    st["last_action"] = SUMMARY
    st["note"] = ("r712: cloudF aggregation row delivered (D-20261007-06 window, 6d early) + F-20261007-01 self-flip "
                  "(D-20261008-01(2)); both watermarks unchanged; pool_starvation/supply_floor flags recorded with disposition.")
    st["next_pointer"] = NEXTP
    st["verify"] = VERIFY
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
                                       "r712 both sweeps = UNCHANGED EE659451 zero delta zero action; hex-case comparison "
                                       "normalized per r711 pit law; facts-driven from results/_r712bmc_s05_facts.json, "
                                       "64hex shape-asserted, never hand-typed (r583 S4 law))")
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r712 both sweeps "
                                    "= UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
                                    "facts-driven from results/_r712bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
    with io.open(ROOT + r"\state-bm-c.json", "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=True, indent=1)

    # 2) heartbeat
    with io.open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8") as f:
        hb = json.load(f)
    hb["round_no"] = 713
    hb["round_no_label"] = "round 712 (bm-c)"
    hb["last_round"] = 712
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
    hb["latest_artifact"] = ("results/cloudf_face_row.py + results/cloudf_face_row.json + HQ-FEEDBACK.md F-20261008-01 "
                             "(cloudF aggregation row, D-20261007-06 window) @ " + TS)
    hb["next_milestone"] = ("今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first "
                            "snapshot + QDII watch rerun holiday-delta + CTA_P1 bar-gated wiring (<= 10-08 23:59)")
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
    assert hb2["round_no"] == 713 and st2["round_no"] == 713
    assert len(hb2.get("orders_ack", [])) == 176, "orders_ack mutated!"
    with io.open(rp, encoding="utf-8") as f:
        tail = f.read()[-400:]
    assert "r712" in tail and "[via bm-c r712]" in tail, "report tail missing r712"
    print("CLOSE_OK ts=%s epoch=%d state_round_no=713 orders_ack=176 report_tail=r712" % (TS, EPOCH))

if __name__ == "__main__":
    main()
