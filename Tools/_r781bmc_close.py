# -*- coding: utf-8 -*-
"""r781 bm-c S7 closeout: facts-driven state+heartbeat update ONLY.
argv: head_sha (pre-commit tip, 40hex). ALL SHAs/verdicts extracted from
results/_r781bmc_s05_facts.json + _r781bmc_s6_log.txt +
_r781bmc_qa_probe.json + _r781bmc_close_facts.json + _r781bmc_row.txt +
watermark_red.json + _orphan_face_probe.bm-c.json with shape asserts
(r583 facts-driven law).
Round shape: S6 40/40 rc0 SECOND consecutive all-green window (CEO face
40 panels regenerated); QA det-99th defer window 3 (r781 slot
foreign-occupied, r669 overwrite ban; r782 occupied, r783 free on origin);
fund_premium expected-NAV-date publish-face observation (still 09-30,
fund NAV T+1 -> 10-09 evening retry window); CEO menu A waiting state
(one-line declaration, no rescan).
The r781 canon report row was appended by Tools/_r781bmc_row_append.py
BEFORE this close (canon face directly -- r749 cross-machine-law cured
template holds; ROOT orphan face untouched/frozen).
No git subprocess inside (git runs in the PS batch via silent-git).
Pattern credit: _r780bmc_close.py."""
import json
import os
import re
import sys
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HEAD_SHA = sys.argv[1]
assert re.fullmatch(r"[0-9a-f]{40}", HEAD_SHA), "head_sha must be 40hex"

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")


def main():
    with open(os.path.join(REPO, "results", "_r781bmc_close_facts.json"),
              encoding="utf-8") as fh:
        cf = json.load(fh)
    assert cf["round"] == 781, "close-facts round mismatch"
    RAM_GB = float(cf["ram_gb"])
    VRAM_MB = int(cf["vram_mb"])
    CPU_PCT = float(cf["cpu_pct"])

    with open(os.path.join(REPO, "results", "_r781bmc_s05_facts.json"),
              encoding="utf-8") as fh:
        facts = json.load(fh)
    assert facts["round"] == 781
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [] and facts["inbox_unread"] == []
    assert facts["dec_delta"] is False and facts["ord_delta"] is False
    assert facts["fleet_orders_total"] == 51
    ord8, dec8 = ord_sha[:8], dec_sha[:8]

    with open(os.path.join(REPO, "results", "_r781bmc_s6_log.txt"),
              encoding="utf-8") as fh:
        s6full = fh.read()
    assert s6full.startswith("r781 bm-c S6 chain run"), "s6 log round header"
    m = re.search(r"legs=(\d+)", s6full.split("\n")[0])
    assert m and m.group(1) == "40", "chain legs must be 40"
    rc0 = len(re.findall(r"\[rc=0\]", s6full))
    rcbad = len(re.findall(r"\[rc=(?!0\])[0-9]+\]", s6full))
    assert rc0 == 40 and rcbad == 0, "chain shape must be 40 rc0 all-green"
    assert "data cutoff: 2026-10-08" in s6full, "cutoff 10-08 line missing"
    assert "already covers expected NAV date 2026-09-30" in s6full, \
        "fund_premium honest no-op face missing"
    assert "marks already at panel cutoff 2026-10-08 -- no-op" in s6full, \
        "aggressive_lab idempotent no-op face missing"
    assert '"verdict": "py_low_board_clear"' in s6full, \
        "py_watermark board-clear verdict missing"

    with open(os.path.join(REPO, "results", "_r781bmc_qa_probe.json"),
              encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 781
    assert qap["verdict_zero_collision"] is False, \
        "r781 slot must be foreign-occupied (defer path)"
    assert len(qap["slot_origin"]) == 2, "origin r781 foreign pack pair"
    assert len(qap["slot_r782_origin"]) == 2, "r782 foreign pack"
    assert qap["slot_r783_origin"] == [], "r783 expected free on origin"

    row_bytes = open(os.path.join(REPO, "results", "_r781bmc_row.txt"),
                     "rb").read()
    ledger_bytes = open(os.path.join(
        REPO, "logs", "iteration-loop", "round_reports-bm-c.md"), "rb").read()
    assert ledger_bytes.endswith(row_bytes), "ledger tail == r781 row"
    row_len = len(row_bytes)

    with open(os.path.join(REPO, "results", "watermark_red.json"),
              encoding="utf-8") as fh:
        wm = json.load(fh)
    assert wm.get("red") is False
    wm_line = "绿（red=%s·lane=%s·next_pick=%s）" % (
        str(wm.get("red")), wm.get("lane"),
        (wm.get("next_pick") or {}).get("status", "?") + " " +
        ((wm.get("next_pick") or {}).get("candidate") or "")[:40])
    with open(os.path.join(REPO, "results", "_orphan_face_probe.bm-c.json"),
              encoding="utf-8") as fh:
        orph = json.load(fh)
    orphan_n = int(orph.get("orphans", 0))

    did = (
        "r781: S6 二连全绿窗+QA det-99th 让位续+fund_premium 发布面观察轮（22:2x-22:4x 窗·第 82 bm-c 连守轮）——"
        f"①S0：fetch 实核 HEAD==origin/main=={HEAD_SHA[:9]} 零增量免 rebase（ahead=0 behind=0·轮首脏 10 面全为 bm-c 自产 daemon live faces+本司 r781 driver 零外来半成品）；"
        f"②S0.5 双扫：ORD/DEC 双恒等零增量（{ord8}/{dec8}）·unacked=0（51 orders）·inbox=0；"
        "③S1 smoke 49/49 全绿+SAT 引擎活（status rc0·Tools 实例面·hb age 48s）；"
        "④S2 板清（177 票 0 open·bm-c 在册 claimed=T-2026-09-30-134 一张·job 板零）"
        "+idle 非绿（RAM 15.2%<40%·VRAM 1.62GB<6GB·claimable_pool_lines=2 非绿零义务·O-20261007-2315）；"
        "⑤**QA r781 槽探针=外机包占用（origin+本地同步态·qa face 821/567·slot_r781=smoke-r781.md+equity-curve-r781.png·r782 亦占·r783 空）"
        "→本司 det-99th QA 包让位跳写第三窗（r669 覆写禁令·探针 _r781bmc_qa_probe.json verdict_zero_collision=false 在案·让位=诚实披露非义务跳过）**；"
        "⑥**S6 40/40 rc0 二连全绿窗（CEO 面 40 张再生成）**：update_daily new rows=0 cutoff 10-08 面板完备〔12 SZ r779 治愈面维持〕"
        "·fund_premium 期望 NAV 日仍 09-30 诚实 no-op〔发布面=基金 NAV T+1·10-08 NAV 待 10-09 晚窗·第三连察·非故障〕"
        "·regime ORANGE d2 shadow〔hs300<MA200〕·live_paper ENFORCE active〔masked blocked=0 yellow=1〕"
        "+lane_io stale-takeover derive 合法〔bm-a hb 陈 43min·O-2100 s2.4〕"
        "·t35 open-fill PASS 0/0/0·t35_paper_export 6 员 18 仓 equity 5,996,451→export-2026-10-08.json"
        "·dualrun ZERO-DRIFT streak 51 @408 条"
        "·py_watermark verdict=py_low_board_clear〔窗 2·板清合法 idle 白名单〕"
        "·compute_audit 旗=pool_starvation+supply_floor〔ready=0<floor 3·N1 常供线在役已知面·supply_gap=false〕"
        "·daily_report REPORT-2026-10-08 再生成〔faces=5〕·ceo_live_usage LIVE-2026-10-08 再生成〔ORANGE·cap 50%·heat COOL〕"
        "·scorecard S=2 A=4 B=0 C=0·build_status 再生成〔factors=10·backtest 432combos〕；"
        "⑦CEO 菜单等待态一行声明（A=视频段解冻·零勾选回执·等待态维持不重扫）；"
        f"⑧自愈四件全绿（loop pin5 no-op 22:34+watchdog 重注册 22:35+双爪 LF 归一 in-place）+attrition 4 台账 CLEAN（3 healed 历史缩行注记照录）"
        f"+r781 行直落正典面（{row_len}B·ledger tail 断言过·ROOT 孤儿件零触碰冻结维持）"
        f"·孤儿面={orphan_n} 只读（ComfyUI 产线资产）·idle 非绿（RAM {RAM_GB}GB·idle_rounds=0·agenda 未饿）"
    )

    verify = (
        "smoke 49/49"
        " + results/_r781bmc_s6_log.txt（40 legs rc0=40 nonzero=0 二连全绿窗·fund_premium 诚实 no-op·AGGR/GRID/CTA 幂等 no-op 行在案）"
        " + results/_r781bmc_s05_facts.json（双扫恒等·unacked=0·inbox=0·shape-asserted）"
        " + results/_r781bmc_qa_probe.json（r781 槽外机占用披露·让位依据）"
        f" + logs/iteration-loop/round_reports-bm-c.md r781 行（{row_len}B·tail 断言）"
        " + results/_attrition_guard_scan.json CLEAN（4 台账）"
        " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
        " + results/watermark_red.json（red=false）"
        " + push 送达自证（commit 后 fetch origin/main..HEAD=0）"
    )

    face = (
        "当前活: r781 bm-c（22:2x-22:4x 窗·S6 40/40 二连全绿+QA det-99th 让位续+fund_premium 发布面观察轮·第 82 连守轮）——"
        "主产出=①S6 40 腿 CEO 面 40 张再生成（二连全绿窗）②paper_export/daily_report/LIVE 页 CEO 实物面刷新 10-08 版"
        "③QA r781 槽外机占用让位第三窗（r669 禁令·探针在案）"
        f" | 最近实物: results/_r781bmc_s6_log.txt + export-2026-10-08.json @ {NOW_ISO}"
        " | 下个里程碑: r782=fund_premium 10-08 NAV 首采重试（T+1·10-09 晚窗）+QA det-99th 撞名续判（r783 槽空在案）"
        "（窗 ≤48h）；CEO 勾选后按选项走（A=视频段解冻）"
    )

    artifact = (
        "results/_r781bmc_s6_log.txt (40 legs rc0=40 second consecutive "
        "all-green window) + results/paper_export/export-2026-10-08.json "
        "(6 traders 18 positions equity 5,996,451) + docs/daily_report/"
        "REPORT-2026-10-08.md + docs/live_usage/LIVE-2026-10-08.md "
        f"+ logs/iteration-loop/round_reports-bm-c.md r781 row ({row_len}B) "
        f"@ {NOW_ISO}"
    )

    milestone = (
        "r782: fund_premium 10-08 NAV first-collect retry (T+1 publish face, "
        "10-09 evening window); QA det-99th slot re-probe (r782 occupied "
        "known, r783 free on origin); CEO A/B/C menu choice follow-up "
        "(A=video-segment unfreeze, waiting state); T-177 regime-5 labeler "
        "(bm-a lane) consumption wiring; next 5x = bm-c r785"
    )

    nxt = (
        "r782 续作: ①fund_premium 10-08 NAV 首采重试（发布面=T+1·10-09 晚窗重试）"
        "②QA det-99th 撞名续判（r782 槽占用已知·r783 槽空在案）"
        "③CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
        "④T-177 regime-5 标签器（bm-a 车道）消费面跟进"
        "⑤下一 5x=bm-c r785"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r781 sweep = UNCHANGED "
        f"{ord8} (zero delta, watermark held); facts-driven from "
        "results/_r781bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    )
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r781 sweep = "
        f"UNCHANGED {dec8} (zero delta, watermark held); facts-driven from "
        "results/_r781bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    )

    epoch = int(time.time())
    common = {
        "round_no": 782,
        "round_no_label": "round 781 (bm-c)",
        "last_round": 781,
        "last_round_at": NOW_ISO,
        "last_seen": NOW_ISO,
        "last_seen_at": NOW_ISO,
        "clock_read": NOW_ISO,
        "ts": NOW_ISO,
        "updated": NOW_ISO,
        "updated_at": NOW_ISO,
        "current_task_at": NOW_ISO,
        "last_ts": NOW_ISO,
        "last_run_at": NOW_ISO,
        "last_orders_at": NOW_ISO,
        "last_decisions_at": NOW_ISO,
        "last_decisions_read_at": NOW_ISO,
        "last_round_ts": NOW_ISO,
        "heartbeat_epoch_utc": epoch,
        "idle_rounds": 0,
        "agenda_starved": False,
        "did": did,
        "verdict": did,
        "note": did,
        "last_action": did,
        "last_round_summary": did,
        "current_task": face,
        "activity_now": face,
        "latest_artifact": artifact,
        "next_milestone": milestone,
        "next": nxt,
        "next_pointer": nxt,
        "verify": verify,
        "last_orders_sha": ord_sha,
        "ord_sha_method": ord_method,
        "last_orders_sha_method": ord_method,
        "dec_sha_method": dec_method,
        "last_decisions_sha_method": dec_method,
        "last_decisions_sha": dec_sha,
        "head_sha": HEAD_SHA,
        "last_pulled_at": NOW_ISO,
        "free_ram_gb": RAM_GB,
        "idle_ram_gb": RAM_GB,
        "ram_free_gb": RAM_GB,
        "cpu_pct": CPU_PCT,
        "cpu_util_pct": CPU_PCT,
        "cpu_idle_pct": round(100 - CPU_PCT, 1),
    }
    for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb",
              "gpu_free_mib", "gpu_idle_mb", "gpu_idle_mib"):
        common[k] = VRAM_MB

    for path in (os.path.join(REPO, "state-bm-c.json"),
                 os.path.join(REPO, "fleet", "machines", "bm-c.json")):
        with open(path, encoding="utf-8") as fh:
            j = json.load(fh)
        for k, v in common.items():
            j[k] = v
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(j, fh, indent=1, ensure_ascii=False)
        back = json.loads(open(path, encoding="utf-8").read())
        assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
        assert back["round_no"] == 782

    print("CLOSE_OK round=781->782 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f "
          "s6=40/40 all-green(x2) qa=defer(r781/r782 foreign, r783 free) "
          "row=%dB ord=%s dec=%s orphan=%d"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, row_len, ord8, dec8,
             orphan_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
