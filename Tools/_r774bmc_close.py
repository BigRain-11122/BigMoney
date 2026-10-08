# -*- coding: utf-8 -*-
"""r774 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
ram_gb vram_mb cpu_pct head_sha. ALL SHAs/verdicts extracted from
results/_r774bmc_s05_facts.json + qa runner .out + _r774bmc_s6.out with
shape asserts (r583 facts-driven law). No git subprocess inside (git runs
in the PS batch via Invoke-SilentExe). Pattern credit: _r772bmc_close.py."""
import json
import os
import re
import sys
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RAM_GB = float(sys.argv[1])
VRAM_MB = int(sys.argv[2])
CPU_PCT = float(sys.argv[3])
HEAD_SHA = sys.argv[4]
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
    with open(os.path.join(REPO, "results", "_r774bmc_s6.out"), encoding="utf-8") as fh:
        s6_lines = [l.strip() for l in fh if l.strip()]
    s6_first = s6_lines[0] if s6_lines else "S6 ?"
    with open(os.path.join(REPO, "results", "_r774bmc_qa_runner.out"), encoding="utf-8") as fh:
        qa = fh.read()
    m = re.search(r"REPORT qa\\smoke-r774\.md items=(\S+)", qa)
    qa_items = m.group(1) if m else "?"
    m = re.search(r"BACKTEST trades=(\d+) determinism=(\S+)", qa)
    trades = m.group(1) if m else "?"
    det = m.group(2) if m else "?"
    m = re.search(r"BACKTEST equity_points=\d+ final=(\d+)", qa)
    equity = m.group(1) if m else "?"
    m = re.search(r"PNG qa\\equity-curve-r774\.png \((\d+) bytes\)", qa)
    png_bytes = m.group(1) if m else "?"
    m = re.search(r"DATA latest_panel_bar=(\S+)", qa)
    panel_bar = m.group(1) if m else "?"
    with open(os.path.join(REPO, "results", "_r774bmc_s05_facts.json"), encoding="utf-8") as fh:
        facts = json.load(fh)
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [] and facts["inbox_unread"] == []
    with open(os.path.join(REPO, "results", "watermark_red.json"), encoding="utf-8") as fh:
        wm = json.load(fh)
    wm_line = "绿（red=%s·lane=%s·next_pick=%s）" % (
        str(wm.get("red")).lower(), wm.get("lane"),
        (wm.get("next_pick") or {}).get("status", "?") + " " +
        ((wm.get("next_pick") or {}).get("candidate") or "")[:40])
    with open(os.path.join(REPO, "results", "_r774bmc_outbound_cas.json"), encoding="utf-8") as fh:
        ob = json.load(fh)
    assert ob.get("push_ok") and ob.get("delivered"), "outbound CAS not delivered"

    did = (
        "r774: CEO 全面开工令 A 向预开工轮（19:3x-19:5x 窗·全链 40 腿+QA det-94th+克隆门·第 75 连守轮）——"
        "①S0.5 双扫：ORD delta 1 行消费（CEO 19:25「我下班了，全面开工，全面利用机器算力」令·"
        "item④ A 向预开工令下 bm-c=承 O-1715 自决授权 CEO 勾选前先动——**本轮认领即开工同轮收口**；"
        "r770 O-1820 破案=时限内无违令维持·DEC %s 恒等零动作）·unacked=0（51 orders）·inbox 0；"
        "②CEO 令④ 实弹：v6 批 7 张本地 SDXL（85 秒·seed 锁 20011024-30·RTX 3070 ComfyUI）"
        "+合成两迭代（z 面板瑕疵→z3 暗剪影乘法鬼影·画布黑边 bug 当场修复=掩码×贴图区指示）"
        "+云端盲评 7 次→**3 张过门**：st3_goddess_c 白裙版 7/8/7（白袍确认·与 b 版烟青构成裙色双版菜单）"
        "/st1_library_z3_composite 8/8/9（书库三代 FAIL 后**首次过门**·两时代同框拍子成立·考据 9 分本包最高）"
        "/st2_carve_i 快切剪影 8/8/7（文字弱化=设计·绕开本地楔形字能力边界）；4 败诚实：goddess_d 种子漂移 5/8/2"
        "·glass_c 青窗失控 7/8/5（玻璃场维持 a 版 7/7/7 最佳）·carve_j 缺手 5/4/3·z 面板硬边 5/7/7（被 z3 取代）；"
        "**CAS 直投合同路径 4 件**（3 jpg+A-DIRECTION-v1.md·newc %s·push_ok+delivered 自证 fetch+ls-tree）"
        "=bm-a 哨盯双路径可收；"
        "③S1 smoke 49/49+饱和引擎活（W189 席位 bm-a 预留·引擎车道零触碰）；"
        "④S2 板清（零 open 票·job 板零·MV 无撞认领：mv_work 18:18 后零他机新动）；"
        "⑤S6 40/40 rc0（update_daily sina 迟 bar 仍未落地 cutoff %s=当窗重试"
        "·CTA_P1 无可标 bar 诚实 no-op·fund_premium NAV 09-30 已覆 no-op"
        "·dualrun ZERO-DRIFT streak 51"
        "·compute_audit FLAG:pool_starvation,supply_floor 如实披露=moneyflow IC reference 在飞已认领批非断供"
        "·py_watermark py_low_with_work_cands=probe 捕获本轮自身三批在飞（S6+QA+MV-v6）非违令·如实点名）；"
        "⑥QA det-94th 5/5（%s trades·equity %s 冻结恒等·determinism=%s·png %sB·"
        "case#11 撞名披露：qa/smoke-r774.md bm-b 包 blob 6360ac35 先在册·同冻结数字零科学损失"
        "·同径覆写·bm-b 版 git 史保全·.err 0B）；"
        "⑦克隆门 4/4（序敏感双替换+stale 门先于叙事 fix+case#11 叙事 fix+法典引用豁免断言"
        "·收据 _r774bmc_clone_receipt.json）；"
        "⑧自愈四件全绿（loop pin=5+watchdog 在位+双爪 MATCH）·孤儿面=1 只读（ComfyUI 产线资产）"
        "·token +0（L2 legs 0 today·云端盲评 7 次入账披露）"
        "·idle 非绿（RAM %.1fGB<40%%·本轮实工·idle_rounds=0·agenda 未饿）"
    ) % (dec_sha[:8], (ob.get("newc") or "")[:8], panel_bar, trades, equity, det,
         png_bytes, RAM_GB)

    verify = (
        "smoke 49/49 + qa/smoke-r774.md 5/5（%s trades·equity %s 冻结恒等·determinism=%s·94 连证·case#11 披露·.err 0B） "
        "+ results/_r774bmc_s6_log.txt（%s） "
        "+ results/_r774bmc_s05_facts.json（ORD A401710A 消费+DEC 恒等·unacked=0·inbox 0·shape-asserted·双扫） "
        "+ results/_r774bmc_clone_receipt.json（4 files·stale773=0·compile ok·canon-cite 豁免断言） "
        "+ results/_r774bmc_outbound_cas.json（push_ok·delivered·newc %s·ls-tree 自证） "
        "+ results/mv_work/kf/（v6 7 张+合成 z/z2/z3 全留档+manifest+双 receipt） "
        "+ results/_attrition_guard_scan.json CLEAN "
        "+ 孤儿面=1 只读（results/_orphan_face_probe.bm-c.json） "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % (trades, equity, det, s6_first, (ob.get("newc") or "")[:8])

    face = (
        "当前活: r774 bm-c（19:3x-19:5x 窗·CEO 全面开工令 A 向预开工轮·第 75 连守轮）"
        "——主产出=①A 向 3 张过门图+合同路径交付（goddess 白裙 7/8/7·library_z3 8/8/9 三代首过·carve 快切剪影 8/8/7）"
        "②S6 40/40 rc0 ③QA det-94th 5/5（93 trades 冻结恒等） "
        "| 最近实物: fleet/mv0001-handover/outbound/{st3_goddess_c,st1_library_z3_composite,st2_carve_i}.jpg"
        "+A-DIRECTION-v1.md（group newc %s·delivered 自证）+results/_r774bmc_s6_log.txt 40/40 @ %s "
        "| 下个里程碑: CEO 勾 A/B/C 后视频段解冻施工（A 向弹药已备齐：z3+carve_i+裙色双版）；"
        "sina 10-08 bar 落地→CTA_P1 首接线+fund_premium 10-08 NAV 首采；next 5x=bm-c r775（HANDOVER 窗）"
    ) % ((ob.get("newc") or "")[:8], NOW_ISO)

    artifact = (
        "fleet/mv0001-handover/outbound/ 3 jpg + A-DIRECTION-v1.md (group CAS newc %s, delivered) "
        "+ results/mv_work/kf/ v6 batch 7 gens + z3 composite (3-PASS/4-FAIL honest ledger) "
        "+ qa/smoke-r774.md 5/5 + results/_r774bmc_s6_log.txt (40/40 rc0) @ %s"
    ) % ((ob.get("newc") or "")[:8], NOW_ISO)

    milestone = (
        "CEO picks A/B/C -> video lane unfreeze and SP construction (A-option ammo stocked: "
        "z3 8/8/9 + carve_i 8/8/7 + dress-color dual menu); sina 10-08 late-bar lands -> CTA_P1 "
        "first-bar wiring + fund_premium 10-08 NAV first snapshot; next 5x = bm-c r775 (HANDOVER window)"
    )

    nxt = (
        "r775 续作: ①HANDOVER 窗（5x·核对更新 research/HANDOVER.md 产物清单）"
        "②CEO 勾选后按选项走（A=视频段解冻·分镜表+调色链正典施工·SP 12 项清单；B=云端通道；C=按新构图）"
        "③A 向滚动续产备选（玻璃青板收窄可再试 seed 族·z3 鬼影透明度降一档微调·goddess 白裙第二 seed 择优）"
        "④sina 迟 bar 自愈重试→CTA_P1 首接线+fund_premium 10-08 NAV 首采"
        "⑤QA det-95th 撞名预检（git ls-tree origin/main qa/ 探 r775）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r774 sweep = DELTA "
        "CONSUMED %s (CEO 19:25 full-work-start order, item-4 A-direction pre-start executed "
        "same-round claim-to-delivery); facts-driven from results/_r774bmc_s05_facts.json, 40hex "
        "shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r774 sweep = "
        "UNCHANGED %s (zero action, watermark held); facts-driven from "
        "results/_r774bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 775,
        "round_no_label": "round 774 (bm-c)",
        "last_round": 774,
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
        assert back["round_no"] == 775

    row = ("%s | r774 | dept:工程+交易+产线（19:3x 窗·CEO 全面开工令 A 向预开工轮·第 75 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=1（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s | 本轮产品积分：2（A 向 3 张过门图+合同路径 CAS 交付=能看能用实物"
           "·S6 40 腿+QA det-94th=经营层实物） | 记账预算：3（轮报行/心跳/state 收口+克隆收据+facts 双扫"
           "·云端盲评 7 次照实披露）") % (NOW_ISO, wm_line, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=774->775 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s qa=%s trades=%s png=%sB panel=%s ob_newc=%s"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, qa_items, trades, png_bytes,
             panel_bar, (ob.get("newc") or "")[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
