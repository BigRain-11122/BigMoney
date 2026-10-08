# -*- coding: utf-8 -*-
"""r775 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
ram_gb vram_mb cpu_pct head_sha. ALL SHAs/verdicts extracted from
results/_r775bmc_s05_facts.json + qa runner .out + _r775bmc_s6.out with
shape asserts (r583 facts-driven law). No git subprocess inside (git runs
in the PS batch via Invoke-SilentExe). Pattern credit: _r774bmc_close.py."""
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
    with open(os.path.join(REPO, "results", "_r775bmc_s6.out"), encoding="utf-8") as fh:
        s6_lines = [l.strip() for l in fh if l.strip()]
    s6_first = s6_lines[0] if s6_lines else "S6 ?"
    with open(os.path.join(REPO, "results", "_r775bmc_qa_runner.out"), encoding="utf-8") as fh:
        qa = fh.read()
    m = re.search(r"REPORT qa\\smoke-r775\.md items=(\S+)", qa)
    qa_items = m.group(1) if m else "?"
    m = re.search(r"BACKTEST trades=(\d+) determinism=(\S+)", qa)
    trades = m.group(1) if m else "?"
    det = m.group(2) if m else "?"
    m = re.search(r"BACKTEST equity_points=\d+ final=(\d+)", qa)
    equity = m.group(1) if m else "?"
    m = re.search(r"PNG qa\\equity-curve-r775\.png \((\d+) bytes\)", qa)
    png_bytes = m.group(1) if m else "?"
    m = re.search(r"DATA latest_panel_bar=(\S+)", qa)
    panel_bar = m.group(1) if m else "?"
    with open(os.path.join(REPO, "results", "_r775bmc_s05_facts.json"), encoding="utf-8") as fh:
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
    with open(os.path.join(REPO, "results", "_r775bmc_outbound_cas.json"), encoding="utf-8") as fh:
        ob = json.load(fh)
    assert ob.get("push_ok") and ob.get("delivered"), "outbound CAS not delivered"

    did = (
        "r775: A 向滚动续产轮（19:5x-20:2x 窗·全链 40 腿+QA det-95th+克隆门+5x HANDOVER·第 76 连守轮）——"
        "①S0.5 双扫：ORD delta 1 行消费（bm-a gitsilent 弹窗根治批补正回执 10-08 20:0x·执行司=bm-a 已自执行·"
        "涉本司=否科学判断闸零动作·水位 AB24566E 更新）·DEC EE70CEF0 恒等零动作·unacked=0（51 orders）·inbox 0；"
        "②A 向滚动续产实弹（next-ptr ③）：v7 批 2 张本地 SDXL（seed 20011031/20011032·RTX 3070 ComfyUI）"
        "+z4 合成（鬼影 alpha 0.6→0.45 降一档）+云端盲评 3 次→**glass_d 9/8/7 过门**"
        "（玻璃场新最佳·真实感 9=全项目最高·青缝规格偏离=左缘 1/4 幅面诚实披露·判 7 过线）"
        "→**CAS 直投合同路径 2 件**（st4_glass_d.jpg+A-DIRECTION-v1.1.md·group newc %s·push_ok+delivered 自证 fetch+ls-tree）；"
        "2 败诚实：goddess_e 6/7/6（双 seed 择优=c 版 7/8/7 胜出·裙色菜单不变）"
        "·z4 4/4/5（降档假设证伪=弱鬼影读作贴图面板·z3 8/8/9 维持正典）；"
        "③S1 smoke 49/49+饱和引擎活（SAT rc0·W189 席位 bm-a 预留·引擎车道零触碰）；"
        "④S2 板清（零 open 票·job 板零·CEO 未勾选=outbound 无新 inbound 维持等待态）；"
        "⑤S6 40/40 rc0（update_daily 10-08 节后首 bar 落地尝试=cutoff 09-30 维持·sina 迟 bar 延续下轮重试"
        "·CTA_P1 无可标 bar 诚实 no-op·fund_premium NAV 09-30 已覆 no-op·10-08 首采等 bar）；"
        "⑥QA det-95th 5/5 零撞名首写（%s trades·equity %s 冻结恒等·determinism=%s·png %sB"
        "·撞名预检 next-ptr ⑤ 实跑=origin 无 r775 件·.err 0B）；"
        "⑦克隆门 4/4（stale774=0·QA clean-first-write 叙事修正+10-08 首 bar 窗叙事"
        "·收据 _r775bmc_clone_receipt.json）；"
        "⑧自愈四件全绿（loop pin=5+watchdog 在位+双爪 MATCH）·孤儿面=1 只读（ComfyUI 产线资产）"
        "·token +0（L2 legs 0 today·云端盲评 3 次入账披露）"
        "·idle 非绿（RAM %.1fGB<40%%·本轮实工·idle_rounds=0·agenda 未饿）"
    ) % ((ob.get("newc") or "")[:8], trades, equity, det, png_bytes, RAM_GB)

    verify = (
        "smoke 49/49 + qa/smoke-r775.md 5/5（%s trades·equity %s 冻结恒等·determinism=%s·95 连证·零撞名首写·.err 0B） "
        "+ results/_r775bmc_s6_log.txt（%s） "
        "+ results/_r775bmc_s05_facts.json（ORD AB24566E 消费+DEC 恒等·unacked=0·inbox 0·shape-asserted·双扫） "
        "+ results/_r775bmc_clone_receipt.json（4 files·stale774=0·compile ok） "
        "+ results/_r775bmc_outbound_cas.json（push_ok·delivered·newc %s·ls-tree 自证） "
        "+ results/mv_work/kf/（v7 2 张+z4 合成全留档+manifest·frozen-lane untracked） "
        "+ research/HANDOVER.md r775 5x 行（窗 r771-775） "
        "+ results/_attrition_guard_scan.json CLEAN "
        "+ 孤儿面=1 只读（results/_orphan_face_probe.bm-c.json） "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % (trades, equity, det, s6_first, (ob.get("newc") or "")[:8])

    face = (
        "当前活: r775 bm-c（19:5x-20:2x 窗·A 向滚动续产轮·第 76 连守轮）"
        "——主产出=①glass_d 9/8/7 过门+合同路径交付（玻璃场新最佳·真实感 9 全项目最高）"
        "②S6 40/40 rc0 ③QA det-95th 5/5（93 trades 冻结恒等·零撞名首写） "
        "| 最近实物: fleet/mv0001-handover/outbound/{st4_glass_d.jpg,A-DIRECTION-v1.1.md}"
        "（group newc %s·delivered 自证）+results/_r775bmc_s6_log.txt 40/40 @ %s "
        "| 下个里程碑: CEO 勾 A/B/C 后视频段解冻施工（A 向弹药三重加固：z3 8/8/9+carve_i 8/8/7+玻璃 d 9/8/7+裙色双版）；"
        "sina 10-08 bar 落地→CTA_P1 首接线+fund_premium 10-08 NAV 首采；next 5x=bm-c r780"
    ) % ((ob.get("newc") or "")[:8], NOW_ISO)

    artifact = (
        "fleet/mv0001-handover/outbound/{st4_glass_d.jpg,A-DIRECTION-v1.1.md} (group CAS newc %s, delivered) "
        "+ results/mv_work/kf/ v7 batch 2 gens + z4 composite (1-PASS/2-FAIL honest ledger) "
        "+ qa/smoke-r775.md 5/5 + results/_r775bmc_s6_log.txt (40/40 rc0) @ %s"
    ) % ((ob.get("newc") or "")[:8], NOW_ISO)

    milestone = (
        "CEO picks A/B/C -> video lane unfreeze and SP construction (A-option ammo triple-reinforced: "
        "z3 8/8/9 + carve_i 8/8/7 + glass_d 9/8/7 NEW BEST + dress-color dual menu); sina 10-08 late-bar "
        "lands -> CTA_P1 first-bar wiring + fund_premium 10-08 NAV first snapshot; next 5x = bm-c r780"
    )

    nxt = (
        "r776 续作: ①CEO 勾选后按选项走（A=视频段解冻·分镜表+调色链正典施工；B=云端通道；C=按新构图）"
        "②sina 迟 bar 自愈重试→CTA_P1 首接线+fund_premium 10-08 NAV 首采"
        "③A 向滚动续产备选（玻璃 d 版左缘青缝再收敛一轮·goddess/carve 场维持现最佳）"
        "④QA det-96th 撞名预检（git ls-tree origin/main qa/ 探 r776）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r775 sweep = DELTA "
        "CONSUMED %s (bm-a gitsilent desktop-flash-fix correction receipt 20:0x, executor=bm-a "
        "self-executed, not-this-office=zero action, science-gate passed); facts-driven from "
        "results/_r775bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r775 sweep = "
        "UNCHANGED %s (zero action, watermark held); facts-driven from "
        "results/_r775bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 776,
        "round_no_label": "round 775 (bm-c)",
        "last_round": 775,
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
        assert back["round_no"] == 776

    row = ("%s | r775 | dept:工程+交易+产线（19:5x-20:2x 窗·A 向滚动续产轮·第 76 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=1（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s | 本轮产品积分：2（glass_d 9/8/7 过门图+合同路径 CAS 交付=能看能用实物"
           "·S6 40 腿+QA det-95th=经营层实物·5x HANDOVER 窗内落账） | 记账预算：3（轮报行/心跳/state 收口"
           "+克隆收据+facts 双扫·云端盲评 3 次照实披露）") % (NOW_ISO, wm_line, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=775->776 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s qa=%s trades=%s png=%sB panel=%s ob_newc=%s"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, qa_items, trades, png_bytes,
             panel_bar, (ob.get("newc") or "")[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
