"""R319 bm-b wrap-up: round report line + state.json 318->319 + heartbeat."""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROUND = 319

REPORT_LINE = (
    f"{TS} | r319 bm-b | dept:研究+工程+总经办 | 水位=红瞬态→白（11:30 red=runnable-work-idle-low-cpu"
    "=O-1626 律面在 T-93 开票窗按 11:07 样本合法触发·唯一池件 T19-PHANTOM-P1 lane_owner=bm-c"
    " R31 律本机禁碰·bm-c 11:40:07 已认领在磨；11:47:25 新探针=py_low_board_clear 白名单·下 tick 自清）"
    "| did: (1) S0 pull FF 571cb162→8e68f689 + autostash UU autofill_state.json 按 r317 stage-union "
    "正典复用解（53 entries·last_tick 11:30:02·零损失）+ p1d_gates restore --staged 还原设计态 "
    "(2) S0.5 双扫 orders 96/96 零未回执（轮首轮尾双扫一致·无新令）·集团 ..\\..\\docs\\decisions.md "
    "不存在=零动作 (3) smoke 25/25 (4) **T-89 slice-3 DELIVERED**：进攻军供给提速评估 memo "
    "M-20260927-01 落 GM 审阅队列 research/GM_REVIEW_MEMOS.md（PENDING·提案=牛市专才供给线前置："
    "wave-1 判定过筛轮动三族 #81/#82/#83 预注册优先→35 库趋势流随后；证据=PROSPECT 0/22 进攻军候选"
    "（T-89 finalize）+T-90 ring2 路由全政体负+ring4 席位空位+SCHOOL queue#1-#5 全判负=零排他代价；"
    "重排执行权=GM 面·签署前零法件触碰） (5) **T-90 deliverable-4 LANDED**：monthly_briefing.py 新增"
    "§六「链条健康」月度四件套（①当值态+②换军事件+③断环扫描+④偏好面进度·单源消费 "
    "results/decision_chain_e2e.json verdict/ring_table/seat_vacancy + DECISION_CHAIN_LEDGER.md 版本行"
    "+偏好面 prereg glob·全输入缺件诚实分支）selftest 19/19（+5 新链腿：四件套渲染/判定数字/台账版本解析/"
    "偏好面缺口/缺件诚实）+实弹 BRIEF-202609 幂等再生（28 traders·N=286,541·§六 真实 v1.1 数字全渲染）"
    " (6) DECISION_CHAIN_LEDGER v1.1 verdict PENDING→LANDED 记录性落账（finalize r318 结果入行·"
    "判据零动·v1.1 版本面封版） (7) post_review 4 判据行登记（T-89-S1-PROSPECT-SEGMENTS-FINALIZE + "
    "T-90-V1-E2E-FINALIZE r318 收割面补登（产物稳定锚）+ T-89-S3-ATTACK-SUPPLY-MEMO + "
    "T-90-D4-CHAIN-HEALTH-WIRING 本轮面·registry 49 items·全部 json_field 路径实探后冻结） "
    "(8) T-89/T-90 双票 done 收口（四交付全齐·result_ref 落票·迭代序列走 ledger append-only+触发器"
    "（断环定位已触发）·下版预注册=GM 署名新票） (9) S6 29 lanes rc=0 周日无新 bar（09-25 中秋假="
    "cutoff 09-24 完整合法·regime ORANGE shadow 在态 2 日·clock CALL-2026-09-24 ORANGE_COOL sleeves=4 "
    "activated=0·promotion 0/22 诚实·t35_export 再生 09-24 面·daily_report 4 面·compute_audit CLEAN·"
    "lane 归属护栏全诚实 no-op） | evidence: selftest 19/19 stdout + results/briefings/BRIEF-202609.md §六 "
    "+ GM_REVIEW_MEMOS.md M-20260927-01 + post_review_criteria.json 49 items + 双票 status=done + "
    "S6 rc 板 29x0 + smoke 25/25 | next: GM 审 M-20260927-01（签收=研究部起草 wave-1 三族预注册·"
    "驳回=自然序零损失）；T-92 s3 下个 idle window；sina 深面板 complete 后 sina-construct prereg 起草"
    "（开工门 N≥150）；周一 2026-09-28 09:15 T-91 s3 首 cohort+新 bar 全链；10-01 月度三件套"
    "+REGIME_GUARD v3 日期门；迁移重试窗至 09-29 12:00（v2.2 armed 编辑器门控·勿双 arm）"
)

STATE = {
    "round_no": ROUND,
    "did": (
        "r319: T-89/T-90 双 CEO 令票收口 -- T-89 slice-3 进攻军供给提速 memo M-20260927-01 落 GM 队列"
        "（wave-1 三族优先·queue#1-5 全负零排他代价）；T-90 deliverable-4 月度四件套「链条健康」节接线 "
        "monthly_briefing.py §六（selftest 19/19+实弹 BRIEF-202609 再生）；ledger v1.1 verdict LANDED "
        "记录性落账；post_review 4 行登记；双票 done；S6 29 lanes rc=0 周日无新 bar"
    ),
    "verdict": "green",
    "next": (
        "GM 审 M-20260927-01（签收=wave-1 三族预注册起草·驳回=自然序零损失）; T-92 s3 idle window; "
        "sina deep panel complete 后 sina-construct prereg（N>=150 门）; 周一 09-28 09:15 T-91 s3 "
        "cohort+新 bar 全链; 10-01 monthly trio+REGIME_GUARD v3 日期门; 迁移窗至 09-29 12:00 "
        "(v2.2 armed, no double-arm)"
    ),
    "last_round_ts": TS,
    "last_result": "ok",
    "current_task": (
        "r319: T-89+T-90 closed (all deliverables landed); next = GM adjudication M-20260927-01 "
        "supply queue + T-92 s3 idle window + sina-construct prereg after deep panel complete"
    ),
    "updated_at": TS,
    "last_seen": TS,
    "ts": NOW.strftime("%Y-%m-%d %H:%M:%S"),
}


def update_heartbeat():
    p = ROOT / "fleet" / "machines" / "bm-b.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["last_seen"] = TS
    d["heartbeat_epoch_utc"] = EPOCH
    d["clock_read"] = TS
    d["current_task"] = STATE["current_task"]
    d["cpu_cores"] = 16
    d["free_ram_gb"] = 13.1
    d["idle_ram_gb"] = 13.1
    d["idle_ram_mb"] = 13414
    d["free_ram_mb"] = 13414
    d["total_ram_gb"] = 23.9
    d["cpu_util_pct"] = 2.0
    d["gpu_free_vram_gb"] = 6.8
    d["gpu_free_vram_mb"] = 6937
    d["gpu_idle_vram_mb"] = 6937
    d["gpu_idle_vram_gb"] = 6.8
    d["cpu_pct"] = 2.0
    d["round_no"] = ROUND
    d["round"] = ROUND
    d["verdict"] = (
        "green; r319: T-89 slice-3 supply-acceleration memo M-20260927-01 landed to GM queue "
        "(bull-specialist lanes first: wave-1 trio, zero exclusion cost) + T-90 deliverable-4 "
        "chain-health monthly four-piece wired into monthly_briefing.py section-6 (selftest 19/19, "
        "BRIEF-202609 live regen) + DECISION_CHAIN_LEDGER v1.1 verdict LANDED record-flip + post_review "
        "4 rows registered + T-89/T-90 tickets closed with result_ref; watermark transient red at 11:30 "
        "= O-1626 lawful fire on T-93 open-ticket window, fresh probe 11:47 py_low_board_clear "
        "(sole pool entry T19 lane_owner=bm-c per R31, claimed by bm-c 11:40:07); S6 29 lanes rc=0 "
        "Sunday no-new-bar; smoke 25/25"
    )
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    # smoke F7 self-assert: epoch must be JSON int, clock_read must be T-separated
    chk = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in chk["clock_read"], "clock_read not ISO-T"
    print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} clock={chk['clock_read']}")


def main():
    rp = ROOT / "logs" / "iteration-loop" / "round_reports.md"
    with open(rp, "a", encoding="utf-8", newline="\n") as f:
        f.write(REPORT_LINE + "\n")
    sp = ROOT / "logs" / "iteration-loop" / "state.json"
    sp.write_text(json.dumps(STATE, ensure_ascii=False, indent=1) + "\n",
                  encoding="utf-8")
    update_heartbeat()
    print(f"r{ROUND} wrap-up written (ts={TS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
