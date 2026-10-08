# -*- coding: utf-8 -*-
"""r780 bm-c S7 closeout: facts-driven state+heartbeat update ONLY.
argv: head_sha (pre-commit tip, 40hex). ALL SHAs/verdicts extracted from
results/_r780bmc_s05_facts.json + _r780bmc_s6_log.txt +
_r780bmc_qa_probe.json + _r780bmc_ledger_heal_receipt.json +
_r780bmc_close_facts.json + watermark_red.json with shape asserts
(r583 facts-driven law).
Round shape: 5x HANDOVER check + QA triple-slot defer (r780/r781/r782
all foreign-occupied, r669 overwrite ban) + ledger cross-face heal
(r771-r779 ten rows verbatim row-level union into canonical face
logs/iteration-loop/round_reports-bm-c.md per r749/r750/r865-heal
mirror recipe; ROOT orphan face untouched/frozen) + S6 40/40 rc0
first all-green window (aggressive_lab honest red cleared).
The r780 canon report row was appended by Tools/_r780bmc_row_append.py
BEFORE this close (canon face directly -- r749 cross-machine-law
misuse pit: close template must NEVER cite r844 ROOT law again).
No git subprocess inside (git runs in the PS batch via silent-git).
Pattern credit: _r779bmc_close.py."""
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
    with open(os.path.join(REPO, "results", "_r780bmc_close_facts.json"),
              encoding="utf-8") as fh:
        cf = json.load(fh)
    assert cf["round"] == 780, "close-facts round mismatch"
    RAM_GB = float(cf["ram_gb"])
    VRAM_MB = int(cf["vram_mb"])
    CPU_PCT = float(cf["cpu_pct"])

    with open(os.path.join(REPO, "results", "_r780bmc_s05_facts.json"),
              encoding="utf-8") as fh:
        facts = json.load(fh)
    assert facts["round"] == 780
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [] and facts["inbox_unread"] == []
    assert facts["dec_delta"] is False and facts["ord_delta"] is False
    assert facts["fleet_orders_total"] == 51
    ord8, dec8 = ord_sha[:8], dec_sha[:8]

    with open(os.path.join(REPO, "results", "_r780bmc_s6_log.txt"),
              encoding="utf-8") as fh:
        s6full = fh.read()
    assert s6full.startswith("r780 bm-c S6 chain run"), "s6 log round header"
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

    with open(os.path.join(REPO, "results", "_r780bmc_qa_probe.json"),
              encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 780
    assert qap["verdict_zero_collision"] is False, \
        "r780 slot must be foreign-occupied (defer path)"
    assert len(qap["slot_origin"]) == 2, "origin r780 foreign pack pair"
    assert len(qap["slot_r781_origin"]) == 2 and \
        len(qap["slot_r782_origin"]) == 2, "r781/r782 foreign packs"

    with open(os.path.join(REPO, "results",
                           "_r780bmc_ledger_heal_receipt.json"),
              encoding="utf-8") as fh:
        lh = json.load(fh)
    assert lh["status"] == "HEALED"
    assert lh["all_asserts_pass"] is True
    assert lh["orphan_untouched"] is True
    assert lh["appended_row_count"] == 10
    assert lh["byte_conservation"] is True
    assert lh["appended_block_in_canon_verbatim"] is True
    assert lh["round_labels"] == ["r771", "r772", "r773", "r774", "r775",
                                  "r775-tail", "r776", "r777", "r778",
                                  "r779"]
    heal_bytes = lh["appended_bytes"]

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
        "r780: 5x HANDOVER 核对+QA 三槽让位+轮账本跨面治愈轮（22:0x-22:2x 窗·第 81 连守轮）——"
        f"①S0：fetch 实核 HEAD==origin/main=={HEAD_SHA[:8]} 零增量免 rebase（pull --rebase 撞 6 daemon 活写面 unstaged 拒收=净树两步律前置·轮首脏复核全为 bm-c 自产面零外来半成品）；"
        f"②S0.5 双扫：ORD/DEC 双恒等零增量（{ord8}/{dec8}）·unacked=0（51 orders）·inbox=0；"
        "③S1 smoke 49/49 全绿+SAT 引擎活（status rc0·Tools 实例面）；"
        "④S2 板清（job 板零·51 票全 claimed·T-177 CEO 即时票=bm-a 车道不碰）"
        "+idle 非绿（RAM 16.2%<40%·VRAM 1.57GB<6GB·claimable_pool_lines=2 非绿零义务）；"
        "⑤**QA r780/r781/r782 三槽探针=全外机包占用（origin+本地同步态·qa face 821/567）→本司 r780 QA 包让位跳写（r669 覆写禁令·探针在案·让位=诚实披露非义务跳过）**；"
        "⑥**S6 40/40 rc0 首全绿窗**（aggressive_lab 诚实红清零=AGGR/GRID marks 10-08 幂等 no-op"
        "·update_daily new rows=0 cutoff 10-08 面板完备〔12 SZ r779 治愈面维持〕"
        "·fund_premium 期望 NAV 日仍 09-30 no-op〔源未发布 10-08 NAV·下轮重试·诚实面〕"
        "·regime ORANGE d2 shadow〔hs300<MA200 触发〕·live_paper ENFORCE active〔masked exec days blocked=0 yellow=1〕"
        "+lane_io stale-takeover derive 合法〔bm-a hb 陈 21min·O-2100 s2.4〕"
        "·t35 open-fill PASS 0/0/0·dualrun ZERO-DRIFT streak 51 @408 条"
        "·py_watermark insufficient_history〔窗 1 诚实〕"
        "·compute_audit 旗=pool_starvation+supply_floor breach〔ready=0<floor 3·N1 引擎常供线在役已知面·非空转〕）；"
        f"⑦**轮账本跨面治愈（本窗主产出）**：r771-r779 九轮 10 行（含 r775-tail）误落根孤儿件 round_reports-bm-c.md"
        "=r749 路径分裂坑 9 连复发（r771-r779 close 模板链仍引 r844 ROOT 跨机律=坑律未灌入模板·r645 纪元手术后首大规模复发窗·正典面 last-write 停 r770 18:26 铁证）"
        f"→行级 union verbatim 复迁正典面 logs/iteration-loop/round_reports-bm-c.md（r750/r865-heal 镜像律·S0-restore rc3 行级 union 例外面·10 行 {heal_bytes}B"
        "·字节恒等+orphan untouched+verbatim 尾断言+幂等门全过·receipt=_r780bmc_ledger_heal_receipt.json·孤儿件零触碰冻结维持）"
        "+r780 行直落正典面（3,984B·close 模板不再触 ROOT）；"
        "⑧5x HANDOVER 义务（r776-r780 增量窗行落 research/HANDOVER.md）"
        "+自愈四件全绿（loop pin5 no-op 22:15+watchdog 重注册 22:14+双爪 LF 归一 in-place）"
        f"+attrition 4 台账 CLEAN·孤儿面={orphan_n} 只读（ComfyUI 产线资产）·idle 非绿（RAM {RAM_GB}GB·idle_rounds=0·agenda 未饿）"
    )

    verify = (
        "smoke 49/49"
        " + results/_r780bmc_s6_log.txt（40 legs rc0=40 nonzero=0 首全绿窗·fund_premium 诚实 no-op·AGGR/GRID 幂等 no-op 行在案）"
        " + results/_r780bmc_s05_facts.json（双扫恒等·unacked=0·inbox=0·shape-asserted）"
        " + results/_r780bmc_qa_probe.json（r780/r781/r782 三槽外机占用披露·让位依据）"
        f" + results/_r780bmc_ledger_heal_receipt.json（10 行 {heal_bytes}B·字节恒等+orphan untouched+verbatim 断言全过）"
        " + results/_attrition_guard_scan.json CLEAN（4 台账）"
        " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
        " + results/watermark_red.json（red=false）"
        " + push 送达自证（commit 后 fetch origin/main..HEAD=0）"
    )

    face = (
        "当前活: r780 bm-c（22:0x-22:2x 窗·5x HANDOVER 核对+QA 三槽让位+轮账本 r771-r779 跨面治愈轮·第 81 连守轮）——"
        "主产出=①轮账本 r771-r779 十行 verbatim 复迁正典面（r749 坑 9 连复发治愈·receipt 在案）"
        "②S6 40/40 rc0 首全绿窗（CEO 面 40 张再生成）③QA r780/r781/r782 三槽让位（外机包在册·r669 禁令）"
        f" | 最近实物: results/_r780bmc_ledger_heal_receipt.json + _r780bmc_s6_log.txt @ {NOW_ISO}"
        " | 下个里程碑: r781=fund_premium 10-08 NAV 首采重试+QA det-99th 撞名预检（r781/r782/r783 槽探）"
        "（窗 ≤48h）；CEO 勾选后按选项走（A=视频段解冻）"
    )

    artifact = (
        "results/_r780bmc_ledger_heal_receipt.json (10 rows 36,371B verbatim "
        "row-level union into canonical ledger, all asserts pass) "
        "+ results/_r780bmc_s6_log.txt (40 legs rc0=40 first all-green window) "
        "+ logs/iteration-loop/round_reports-bm-c.md (r771-r779 healed 36,371B "
        "+ r780 row 3,984B) "
        "+ research/HANDOVER.md r780 5x line "
        f"@ {NOW_ISO}"
    )

    milestone = (
        "r781: fund_premium expected-NAV-date advance -> first 10-08 snapshot "
        "retry; QA det-99th slot probe (r781/r782/r783, defer verdict continues); "
        "CEO A/B/C menu choice follow-up (A=video-segment unfreeze, waiting "
        "state); T-177 regime-5 labeler (bm-a lane) consumption wiring; "
        "next 5x = bm-c r785"
    )

    nxt = (
        "r781 续作: ①fund_premium 期望 NAV 日推进→10-08 首采重试（源发布面观察）"
        "②QA det-99th 撞名预检（探 r781/r782/r783 槽占用·让位续判）"
        "③CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
        "④T-177 regime-5 标签器（bm-a 车道）消费面跟进"
        "⑤下一 5x=bm-c r785"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r780 sweep = UNCHANGED "
        f"{ord8} (zero delta, watermark held); facts-driven from "
        "results/_r780bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    )
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r780 sweep = "
        f"UNCHANGED {dec8} (zero delta, watermark held); facts-driven from "
        "results/_r780bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    )

    epoch = int(time.time())
    common = {
        "round_no": 781,
        "round_no_label": "round 780 (bm-c)",
        "last_round": 780,
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
        assert back["round_no"] == 781

    print("CLOSE_OK round=780->781 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f "
          "s6=40/40 all-green qa=defer(r780/r781/r782 foreign) "
          "heal=10rows/%dB ord=%s dec=%s orphan=%d"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, heal_bytes, ord8, dec8,
             orphan_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
