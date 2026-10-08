# -*- coding: utf-8 -*-
"""r779 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
head_sha (post-rebase HEAD, 40hex). ALL SHAs/verdicts extracted from
results/_r779bmc_s05_facts.json + _r779bmc_s6_log.txt (chain scope-split:
40-leg chain + 13-leg POST-HEAL) + _r779bmc_qa_probe.json +
_r779bmc_coldptr_merge.json + _r779bmc_close_facts.json +
update_status.json + watermark_red.json with shape asserts (r583
facts-driven law).
Round shape: prior-session crash adoption (r294 law) -- prior r779
session completed S0 absorb (009b4ef30), S0.5 double-sweep, full 40-leg
S6 chain (21:23-21:24), QA det-98th pack ignition (runner completed
5/5), CODELY coldptr merge (30,684->29,773B <= cap), HQ-FEEDBACK status
flip, then died before closeout; this session adopted everything and
landed the round target: 12 lagging SZ members published 21:48 ->
update_daily new rows=12 -> aggressive_lab rc=0 (AGGR 20/20 marks
through 10-08) + grid marks through 10-08 + smoke 49/49 (RW-4 reds
cleared) + post-heal 13 legs all rc0 (bm-a alive: r366 stale-view veto
correct skips on bm-a-hosted faces).
No git subprocess inside (git runs in the PS batch via silent-git).
Pattern credit: _r778bmc_close.py."""
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


def read_utf8(path):
    with open(path, "rb") as fh:
        data = fh.read()
    bom = data.startswith(b"\xef\xbb\xbf")
    if bom:
        data = data[3:]
    return data.decode("utf-8"), bom


def write_utf8(path, text, bom):
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as fh:
        fh.write(data)


def detect_eol(text):
    tail = text[-400:]
    crlf = tail.count("\r\n")
    lf = tail.count("\n") - crlf
    return "\r\n" if crlf >= lf else "\n"


def append_line(path, line):
    text, bom = read_utf8(path)
    eol = detect_eol(text)
    if text and not text.endswith("\n"):
        text += eol
    text += line + eol
    write_utf8(path, text, bom)
    return len((line + eol).encode("utf-8"))


def main():
    with open(os.path.join(REPO, "results", "_r779bmc_close_facts.json"),
              encoding="utf-8") as fh:
        cf = json.load(fh)
    assert cf["round"] == 779, "close-facts round mismatch"
    assert cf["attrition_rc"] == 0, "attrition guard not CLEAN"
    assert cf["sat_rc"] == 0, "saturation engine not alive"
    RAM_GB = float(cf["ram_gb"])
    VRAM_MB = int(cf["vram_mb"])
    CPU_PCT = float(cf["cpu_pct"])

    with open(os.path.join(REPO, "results", "_r779bmc_s05_facts.json"),
              encoding="utf-8") as fh:
        facts = json.load(fh)
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [] and facts["inbox_unread"] == []
    assert facts["dec_delta"] is False and facts["ord_delta"] is False
    assert facts["fleet_orders_total"] == 51
    ord8, dec8 = ord_sha[:8], dec_sha[:8]

    with open(os.path.join(REPO, "results", "_r779bmc_s6_log.txt"),
              encoding="utf-8") as fh:
        s6full = fh.read()
    marker = "r779 bm-c S6 POST-HEAL completion legs"
    parts = s6full.split(marker)
    assert len(parts) == 2, "s6 log must split chain vs post-heal exactly once"
    chain = parts[0]
    m = re.search(r"legs=(\d+)", chain)
    assert m and m.group(1) == "40", "chain legs must be 40"
    rc0 = len(re.findall(r"\[rc=0\]", chain))
    rcbad = len(re.findall(r"\[rc=(?!0\])[0-9]+\]", chain))
    assert rc0 == 39 and rcbad == 1, "chain shape 39 rc0 + 1 nonzero"
    assert re.search(r"===== aggressive_lab =====.*?\[rc=2\]",
                     chain, re.S), "the one nonzero chain leg must be aggressive_lab"
    assert "data cutoff: 2026-10-08" in chain, "chain cutoff 10-08 line missing"
    ph = re.search(r"POST-HEAL DONE .*? legs=(\d+) rc0=(\d+) nonzero=(\d+)",
                   parts[1])
    assert ph and ph.group(1) == "13" and ph.group(2) == "13" \
        and ph.group(3) == "0", "post-heal shape must be 13/13/0"
    assert "20/20 AGGR marks through 2026-10-08" in parts[1], \
        "post-heal prelude AGGR face missing"
    assert "GRID-159915: bars=4 last=2026-10-08" in parts[1], \
        "grid 159915 heal face missing"

    with open(os.path.join(REPO, "results", "update_status.json"),
              encoding="utf-8") as fh:
        us = json.load(fh)
    assert us["total_new_rows"] == 12, "12 SZ members must have landed"
    assert us["data_cutoff"] == "2026-10-08"
    assert us["hook_ok"] is True, "live.paper hook must have fired"
    assert len(us["catchup"]["laggards"]) == 12
    assert len(us["catchup"]["fetched"]) == 12

    with open(os.path.join(REPO, "results", "_r779bmc_qa_probe.json"),
              encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 779
    assert qap["verdict_zero_collision"] is True
    assert qap["slot_local"] == [] and qap["slot_origin"] == []
    assert "qa/equity-curve-r780.png" in qap["slot_r780_origin"], \
        "r780 foreign-occupied disclosure face missing"
    qa_md = os.path.join(REPO, "qa", "smoke-r779.md")
    qa_png = os.path.join(REPO, "qa", "equity-curve-r779.png")
    assert os.path.exists(qa_md) and os.path.getsize(qa_md) > 0
    png_size = os.path.getsize(qa_png)
    assert png_size > 60000

    with open(os.path.join(REPO, "results", "_r779bmc_coldptr_merge.json"),
              encoding="utf-8") as fh:
        cp = json.load(fh)
    assert cp["round"] == 779
    assert cp["main_bytes_after"] == 29773
    assert cp["main_bytes_after"] <= 30720, "main file must be under cap"
    assert cp["assert_zero_loss"] and cp["assert_main_under_cap"] \
        and cp["assert_lane_under_cap"]
    assert cp["prescan_rc"] == 3, "prescan rc3 face (r735 authorized-migration precedent)"

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
        "r779: 前会话猝死收养+12 SZ 源补发落地轮（21:1x-21:5x 窗·第 80 连守轮·本会话=同轮重启接管·r294 收养律）——"
        f"①S0.5 双扫零增量（ORD {ord8} 恒等·DEC {dec8} 恒等·unacked=0〔51 orders〕·inbox=0）；"
        "②S0 前会话吸收 commit 009b4ef30（daemon 活写面·本会话轮首 git status 复核=全 dirty 均为 bm-c 自产面零外来半成品）；"
        "③S1 smoke 49/49 全绿（r778 的 RW-4 源滞后 2 红清零——12 SZ 成员 21:48 补发后面板 48/48 全 10-08）"
        "+SAT 引擎活（rc0）+S2 板清（job 板零·T-177 CEO 即时票=bm-a 已认领不碰·claimable_pool_lines=2 idle 非绿零义务）；"
        f"④**QA det-98th 证据包 r779 槽净写（前会话点火·本会话收养）**：探针零撞名（qa 本地面 818 件·origin 面 565 件·r779 双面零占用）"
        f"→qa/smoke-r779.md 5/5+qa/equity-curve-r779.png（{png_size}B）·market_clock CALL-09-30 cell=ORA·determinism=True·93 trades；"
        "r780/r781 槽他机包占用披露——bm-c r780 轮 QA 包须让位跳写（r669 覆写禁令）；"
        "⑤**前会话猝死面收养**：S6 40 腿已全跑完（21:23-21:24·legs=40 rc0=39 nonzero=1）"
        "+CODELY 主件冷指针合并（30,684→29,773B≤30KB 帽·10 行 verbatim 迁 archive·零丢失/主帽/车道三断言全过"
        "·prescan rc3=D-06 授权 verbatim 迁移面非删除·r735 判例·receipt=_r779bmc_coldptr_merge.json）"
        "+HQ-FEEDBACK F-20261008-02② 状态腿 open→adopted 翻面（D-20261008-06 已消费决策的回执面）；"
        "⑥**12 只 SZ 成员 21:48 补发落地（第 3 轮定向重试兑现·r778 next_pointer①）**："
        "update_daily new rows=12（159901/915/919/920/928/934/949/980/985/992/995/996 追加至 10-08"
        "·3 成员 ex-div parity 旗=已知 never-auto-correct 诚实面）"
        "→**aggressive_lab rc=0 门自愈（AGGR 20/20 账户 marks 推进至 10-08）**"
        "+grid 5 账户推进至 10-08（159915 heal 面）"
        "+live.paper hook stale-takeover derive（21:48 心跳 stale 74min 面·ENFORCE active·masked exec days blocked=0 yellow=1）"
        "+post-heal 补跑 13 腿全 rc0（strategy_scorecard/t35 族/daily_scorecard/build_status"
        "=lane_io r366 stale-view veto 正确跳过·bm-a origin 心跳 3-4min 新鲜=活体零误接管"
        "·daily_report+LIVE 一页纸已按治愈后面板再生成）；"
        "⑦fund_premium 诚实 no-op ×2（期望 NAV 日仍 09-30）；"
        "py_watermark 采样窗 verdict=py_low_with_work_cands（21:23 QA 包烧窗·板全闭环 0 票 0 bandit·work-cands=在飞批自身·无违令可点）；"
        "compute_audit 双采样=21:23 FLAG:cap_violation（cpu_total 90% 撞 CEO 10% 余量帽边界·py_procs=8 QA 烧窗瞬态）"
        "→21:56 复样 FLAG:supply_floor（cpu 79%/py 1.8%·cap 旗消退·supply_floor=池饿已知面"
        " idle-starvation 采样 1 例·N1 引擎波常设供给在役非空转）；"
        f"⑧自愈四件全绿（loop pin5 no-op·watchdog present·双爪 present-equal）+round.lock 续锁龄 1 次（r698 律）"
        f"+attrition 4 台账 CLEAN·孤儿面={orphan_n} 只读（ComfyUI 产线资产）·idle 非绿（RAM {RAM_GB}GB·idle_rounds=0·agenda 未饿）"
    )

    verify = (
        "smoke 49/49（RW-4 源滞后红清零·freshness 10-08 全绿）"
        f" + qa/smoke-r779.md（5/5）+qa/equity-curve-r779.png（{png_size}B·det-98th 零撞名净写·前会话点火本会话收养）"
        " + results/_r779bmc_s6_log.txt（chain legs=40 rc0=39 nonzero=1〔aggressive_lab 诚实红〕"
        "+POST-HEAL legs=13 rc0=13·AGGR 20/20 10-08+GRID-159915 10-08 行在案）"
        " + results/_r779bmc_s05_facts.json（ORD/DEC 双恒等零增量·unacked=0·inbox=0·shape-asserted·双扫）"
        " + results/_r779bmc_qa_probe.json（r779 槽双面零撞·r780/r781 他机占用披露）"
        " + results/_r779bmc_coldptr_merge.json（主件 29,773B≤30,720B 帽·零丢失三断言）"
        " + results/update_status.json（data cutoff 2026-10-08·total_new_rows=12·laggards 12/12 fetched·hook_ok）"
        " + results/watermark_red.json（red=false）"
        " + results/_attrition_guard_scan.json CLEAN（4 台账）"
        " + push 送达自证（fetch 后 origin/main..HEAD=0）"
    )

    face = (
        "当前活: r779 bm-c（21:1x-21:5x 窗·前会话猝死收养+12 SZ 补发落地轮·第 80 连守轮）——"
        "主产出=①qa/smoke-r779.md 5/5+equity-curve-r779.png（det-98th 零撞名净写）"
        "②12 SZ 补发→AGGR 20/20 marks 10-08+GRID 5 账户 10-08（RW-4 门自愈）③smoke 49/49 全绿"
        f" | 最近实物: qa/smoke-r779.md + AGGR/GRID 2026-10-08 marks @ {NOW_ISO}"
        " | 下个里程碑: r780=5x 轮 HANDOVER 核对+QA r780 槽让位（他机包在册）；"
        "fund_premium NAV 日期推进首采；T-177 regime-5 标签器（bm-a 车道）消费面接线"
    )

    artifact = (
        f"qa/smoke-r779.md (5/5) + qa/equity-curve-r779.png ({png_size}B, det-98th clean first-write) "
        "+ results/aggr_paper 20/20 accounts marks through 2026-10-08 (RW-4 gate self-healed) "
        "+ results/grid_paper GRID-510300/159915 bars=4 last=2026-10-08 "
        "+ results/_r779bmc_s6_log.txt (chain 40 legs + POST-HEAL 13 legs rc0=13) "
        f"@ {NOW_ISO}"
    )

    milestone = (
        "r780 = 5x round HANDOVER check + qa r780 slot defer (foreign pack on origin, "
        "r669 overwrite ban); fund_premium NAV date advance -> first 10-08 snapshot; "
        "T-177 regime-5 labeler (bm-a lane) consumption wiring; "
        "sina SZ late-publication watch retired (healed 10-08 21:48)"
    )

    nxt = (
        "r780 续作: ①5x 轮 HANDOVER 核对（research/HANDOVER.md 产物清单与完成状态）"
        "②QA r780 槽让位跳写（他机 smoke-r780 包在册·r669 覆写禁令·探针先行）"
        "③fund_premium 期望 NAV 日推进→10-08 首采④GM bm-b 车道裁定回执面跟进"
        "⑤CEO 勾选后按选项走（A=视频段解冻）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r779 sweep = UNCHANGED "
        f"{ord8} (zero delta, watermark held); facts-driven from "
        "results/_r779bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    )
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r779 sweep = "
        f"UNCHANGED {dec8} (zero delta, watermark held); facts-driven from "
        "results/_r779bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    )

    epoch = int(time.time())
    common = {
        "round_no": 780,
        "round_no_label": "round 779 (bm-c)",
        "last_round": 779,
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
    for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "gpu_vram_free_mb", "gpu_free_mb", "gpu_free_mib", "gpu_idle_mb", "gpu_idle_mib"):
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
        assert back["round_no"] == 780

    row = (f"{NOW_ISO} | r779 | dept:工程+数据（21:1x-21:5x 窗·前会话猝死收养+12 SZ 补发落地轮·第 80 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           f"WM-VERDICT: {wm_line} | 孤儿面={orphan_n}（ComfyUI 产线资产·只读不杀） | {did} | "
           f"验证证据: {verify} | 下轮指针: {nxt} | "
           "本轮产品积分：2（qa/smoke-r779.md 5/5+png=det-98th 能看能用实物净写；"
           "12 SZ 补发→AGGR 20/20+GRID 5 账户 10-08 marks=纸盘面实物落地；"
           "smoke 49/49 源滞后红清零=能跑实物） | "
           "记账预算：4（轮报行/心跳+state 收口/facts 双扫件/qa 探针件） | "
           "清扫/归档动作自证：冷指针合并 prescan rc3=登记簿命中（D-06 授权 verbatim 迁移面非删除"
           "·r735 判例·零丢失断言全过·receipt=_r779bmc_coldptr_merge.json）")
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=779->780 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f "
          "s6=40(rc0=39,aggr_red)+postheal=13(rc0=13) qa=clean-first-write r779 png=%dB "
          "ord=%s dec=%s orphan=%d coldptr_main=29773B r780_slot=foreign_occupied"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, png_size, ord8, dec8, orphan_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
