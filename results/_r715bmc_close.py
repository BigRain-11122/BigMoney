# -*- coding: utf-8 -*-
# r715 bm-c closeout: state + heartbeat + round-report writes (r714 close pattern).
# UTF-8 explicit everywhere (pit-encoding law); heartbeat epoch = fresh int;
# post-write json.loads self-checks (R170/R178 law: value AND type).
# RAM/CPU/GPU measured fresh in-script (r653 close-size law kin: no stale copied numbers).
import io
import json
import time
import datetime
import subprocess

NO = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
TS_START = "2026-10-08T02:05:29+08:00"          # round-start clock read (S0-1)
EPOCH = int(time.time())

import psutil
vm = psutil.virtual_memory()
RAM_FREE = round(vm.available / (1024 ** 3), 1)
CPU_PCT = round(psutil.cpu_percent(interval=1.0), 1)
CPU_IDLE = round(100.0 - CPU_PCT, 1)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=NO, timeout=20)
    GPU_FREE = int(r.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:
    GPU_FREE = -1

CUR = ("当前活: r715 bm-c 5x HANDOVER 核对更新轮（增量窗 r711-715 五轮产品清单刷新·复市 T-0 盘前值守第 35 连守轮） | "
       "最近实物: research/HANDOVER.md r715 行 + qa/smoke-r715.md 5/5（determinism=True 36th）+ qa/equity-curve-r715.png + "
       "results/_r715bmc_s6_log.txt（39 legs rc0·dualrun streak 35） @ " + TS +
       " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce+fund_premium 首采"
       "（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证；next 5x=r720")

DID = ("r715 bm-c: 5x HANDOVER round + pre-open watch (35th consecutive bm-c watch round, 10-08 reopen T-0, 02:0x pre-open window). "
       "(1) MAIN PRODUCT (5-round law): research/HANDOVER.md r715 line -- increment window r711-715 five-round product-list "
       "refresh (r711 O-2115 governance-day acceptance pack ALL_MET 4/4 + hex-case watermark pit; r712 cloudF aggregator face "
       "+ F-20261008-01 row + F-20261007-01 status self-flip; r713 CTA-P1 paper harness + selftest 12/12 + E44 rehearsal 11/11; "
       "r714 OSS enrollment gate + selftest 24/24 + live dry-check ALL-HELD + ledger sec-7 + E45; r715 this line). "
       "(2) S0: behind=3 (bm-a r855 wave) -> 8-face own-churn absorb (2991aa338) -> clean rebase zero conflict -> push delivered "
       "behind=0. (3) S0.5 sweep 1: orders 51 disk/176 ack unacked=0; DEC ee659451 / ORD 17accc40 both UNCHANGED (hex-case "
       "normalized per r711 law; facts results/_r715bmc_s05_facts.json). (4) S1 smoke 48/48. (5) S3 satengine rc0 alive "
       "(burns 0; W180 finalize landed via bm-a lane -> unified-chain ledger_head 801,905 live read); board 0 open (job_list 0 "
       "+ fleet nondone all others' claimed/closed faces); idle NOT-GREEN (RAM %.1fG free <40%% resident), --worked declared, "
       "idle_rounds=0. compute_audit rc0 flags pool_starvation+supply_floor recorded with standing disposition (engine supply "
       "line W181+ projection + tonight post-close bar face natural supply + W16 draft berth bm-a T-172; no manual pool burn). "
       "(6) S6 39/39 rc0 (dualrun ZERO-DRIFT streak 35; cta_p1_paper honest bar-gated no-op panel cutoff 2026-09-30 < "
       "paper_start 2026-10-08 -> auto-fires at tonight's first-bar round; fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane "
       "first snapshot; py_watermark verdict=py_low_board_clear legal idle whitelist). (7) QA 5/5 36th determinism (93 trades, "
       "sharpe 0.1586, equity 1,017,839 frozen identity, png 66,137B; latest_panel_bar 2026-09-30 golden-week no-op expected "
       "until 10-08). (8) post_review zero red carryover (tail rows all YES); orphan face=1 no-kill documented. (9) S7 "
       "self-heal: loop pin=5 no-op + watchdog re-registered + both claws installed IN-PLACE; attrition guard CLEAN (4 healed "
       "notes as-is); inbox zero unread." % RAM_FREE)

VERDICT = ("r715 bm-c: 5x HANDOVER round clean. Product = research/HANDOVER.md r715 line (increment window r711-715 "
           "product-list refresh) + QA 5/5 36th determinism pack + S6 39/39 rc0 regen; S0 churn-absorb rebase clean behind=0; "
           "both watermarks unchanged zero action; orders sweep unacked=0; W180 finalize harvested by bm-a lane = unified chain "
           "801,905 live read; CA pool flags recorded with standing disposition; post_review zero red; orphan face=1 no-kill; "
           "idle not green-idle, idle_rounds=0 worked-declared.")

SUMMARY = ("r715: 5x HANDOVER line (r711-715) + QA det-36th + S6 39 rc0 streak 35; both watermarks unchanged; orders unacked=0; "
           "W180 harvested chain 801,905; smoke 48/48; post_review zero red.")

NEXTP = ("r716: (a) watch continuation (10-08 reopen first trading day, intraday marks lane live 09:15, pre-open zero blind "
         "action); (b) tonight post-close face: data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
         "15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar auto-wiring + first-marks "
         "verification (S6 cta_p1_paper leg; verify = marks 1 row + state trial-live + compounding identity) (<= 10-08 23:59); "
         "(c) O-2245 follow-ups: first OSS- enrollments (bm-a strategy-class adaptations <=10-16) must pass "
         "Tools/oss_import_gate.py rc0 before settle; NOASSERTION/conditional items stay REF-ONLY; (d) O-2215 deliverable (1) "
         "matrix spec + switching law v1 (<=10-16 12:00; consumes bm-a REGIME-5 discriminator <=10-14 + bm-b five-state router "
         "spec); (e) cloudF row weekly rerun supply (window <=10-14, standing); (f) month-boundary first exam 10-31. "
         "[via bm-c r715]")

VERIFY = ("research/HANDOVER.md r715 line + qa/smoke-r715.md 5/5 + qa/equity-curve-r715.png 66,137B (determinism=True 36th, "
          "93 trades, equity 1,017,839 frozen identity) + results/_r715bmc_s6_log.txt (39 legs rc0, dualrun streak 35) + "
          "results/_r715bmc_s05_facts.json (sweep unacked=0, both watermarks unchanged) + results/_r715bmc_smoke.txt (48/48) + "
          "results/_r715bmc_sat.txt (SAT rc0 alive) + results/_r715bmc_probe.py")

REPORT_LINE = (
    TS + " | r715 | dept:工程（金周复市 T-0 盘前值守轮·第 35 bm-c 连守轮·5x HANDOVER 核对更新轮） | "
    "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单〔板 0 open/176 ack/池 406 全 done〕·"
    "compute_audit 旗标 pool_starvation+supply_floor 照录=池 ready 0<floor 3·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面天然候选供给+"
    "W16 波起草泊位 bm-a T-172〔never-dry 常设律·禁手工代烧〕） | "
    "当前活: r715 主产品=5-round law HANDOVER 核对更新（research/HANDOVER.md r715 行）：增量窗 r711-715 五轮产品清单刷新——"
    "r711 治理日验收包〔O-2115 §三 ALL_MET 4/4+hex-case 水位假 delta 变体当场抓获→pit-protocol-d19.md 直写〕·"
    "r712 cloudF 聚合面补呈〔cloudf_face_row.py+cloudf_face_row.json 278 单全谱+HQ-FEEDBACK F-20261008-01 数据行+F-20261007-01 司面状态自翻〕·"
    "r713 CTA-P1 纸盘接线〔cta_p1_paper.py bar-门控 harness+selftest 12/12+E44 temp-panel 演练 11/11〕·"
    "r714 OSS 落池门收口〔oss_import_gate.py 12 腿 fail-closed+selftest 24/24+live dry-check ALL-HELD+台账 §七+E45 卡=judged-negative 家族复活路径全闭〕·"
    "r715 本行〔S0 干净窗+双水位 UNCHANGED+QA det-36th+S6 39/39+四自愈件幂等〕 | "
    "smoke 48/48 · S6 39/39 rc0（dualrun ZERO-DRIFT streak 35·cta_p1_paper bar-门控诚实 no-op〔panel cutoff 2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕·"
    "fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采·金周/盘前 no-op 腿合法） · QA 5/5（determinism=True 36th·93 trades·equity 1,017,839 冻结恒等·png 66,137B） · "
    "orders 双扫 unacked=0（51 disk/176 ack·S0.5 首扫零差·收尾二扫同验后 commit） · DEC/ORD 同哈希零 delta（EE659451/17accc40·hex-case 归一律遵从） · "
    "SAT 活 rc0（burns 0·W180 finalize 收割=统一链 801,905 实读前移〔live head n1_w180·bm-a 车道落账〕） · "
    "idle NOT-GREEN（RAM %.1fG<40%% 常驻·idle_rounds=0·--worked 申报） · post_review 零红承接（尾行全 YES） · "
    "孤儿面=1（只读披露不击杀） · attrition CLEAN（4 healed 注记照录） · 自愈=loop pin=5 no-op+watchdog 重注册+双爪 IN-PLACE match · "
    "token 面=L1 零 token 腿（token_meter rc0） · 方法论捕获=无新方法（5x 核对=纯簿记复用）·宝藏捕获=N/A（无五类收口批）·"
    "登记册零命中断言=N/A（无清扫/归档/恢复类动作） · 本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
    "下轮 r716：(a) 值守续（盘前零盲动·intraday marks 09:15 起活） (b) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首 bar enforce+"
    "fund_premium 15:30 首采（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤今夜） "
    "(c) O-2245 续作=首批 OSS- 落池件〔bm-a 策略适配件 ≤10-16〕一律先过 Tools/oss_import_gate.py rc0 再 settle "
    "(d) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00） (e) cloudF 行收取窗 ≤10-14 常设 (f) 月界首考 10-31 | "
    "轮产品计分：1（5x HANDOVER 法定核对+QA 证据包+S6 再生面=维护窗实物；零新产品线〔盘前值守如实〕） | "
    "记账预算：4（state+心跳+轮报+HANDOVER 法定） [via bm-c r715]" % RAM_FREE)

def main():
    # 1) state
    with io.open(ROOT + r"\state-bm-c.json", encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 716
    st["round_no_label"] = "round 715 (bm-c)"
    st["last_round"] = 715
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
    st["note"] = ("r715: 5x HANDOVER line landed (r711-715 window refresh); both watermarks unchanged; W180 harvested "
                  "(chain 801,905 live read); QA det-36th; S6 39/39 streak 35.")
    st["next_pointer"] = NEXTP
    st["verify"] = VERIFY
    st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
                                        "r715 sweep = UNCHANGED EE659451 zero delta zero action; hex-case comparison "
                                        "normalized per r711 pit law; facts-driven from results/_r715bmc_s05_facts.json, "
                                        "64hex shape-asserted, never hand-typed (r583 S4 law))")
    st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r715 sweep "
                                    "= UNCHANGED 17accc40, zero delta; hex-case comparison normalized per r711 pit law; "
                                    "facts-driven from results/_r715bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
    with io.open(ROOT + r"\state-bm-c.json", "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=True, indent=1)

    # 2) heartbeat
    with io.open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8") as f:
        hb = json.load(f)
    hb["round_no"] = 716
    hb["round_no_label"] = "round 715 (bm-c)"
    hb["last_round"] = 715
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
    hb["latest_artifact"] = ("research/HANDOVER.md r715 5x line + qa/smoke-r715.md (5/5, determinism=True 36th) + "
                             "qa/equity-curve-r715.png + results/_r715bmc_s6_log.txt (39 legs rc0, dualrun streak 35) @ " + TS)
    hb["next_milestone"] = ("今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first "
                            "snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify (<= 10-08 23:59)")
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

    # 3) round report append (canonical path pinned per r646 S5 law)
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
    assert hb2["round_no"] == 716 and st2["round_no"] == 716
    assert len(hb2.get("orders_ack", [])) == 176, "orders_ack mutated!"
    with io.open(rp, encoding="utf-8") as f:
        tail = f.read()[-400:]
    assert "r715" in tail and "[via bm-c r715]" in tail, "report tail missing r715"
    print("CLOSE_OK ts=%s epoch=%d state_round_no=716 orders_ack=176 report_tail=r715 ram=%.1f gpu=%d" % (TS, EPOCH, RAM_FREE, GPU_FREE))

if __name__ == "__main__":
    main()
