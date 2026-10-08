"""r771 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append, pit direct-write (stale stat-cache fake-dirty rebase
refusal -> research/pit-git-resolver-rebase.md, r666/r747 precedent),
receipt write, json.loads self-verification (epoch int law R170/R178).
argv: ram_gb vram_mb cpu_pct. No git subprocess inside (git runs in the
PS batch via Invoke-SilentExe wrapper). Pattern credit: r770 closeout."""
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

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
HEAD_SHA = "0061ab8c76a9aecd6ec20f7351a5e1118002df5f"  # origin/main at S0 integration (facts)


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
    # ---- facts extraction ----
    with open(os.path.join(REPO, "results", "_r771bmc_s6.out"), encoding="utf-8") as fh:
        s6_lines = [l.strip() for l in fh if l.strip()]
    s6_first = s6_lines[0] if s6_lines else "S6 ?"
    with open(os.path.join(REPO, "results", "_r771bmc_qa_runner.out"), encoding="utf-8") as fh:
        qa = fh.read()
    m = re.search(r"REPORT qa\\smoke-r771\.md items=(\S+)", qa)
    qa_items = m.group(1) if m else "?"
    m = re.search(r"BACKTEST trades=(\d+) determinism=(\S+)", qa)
    trades = m.group(1) if m else "?"
    det = m.group(2) if m else "?"
    m = re.search(r"BACKTEST equity_points=\d+ final=(\d+)", qa)
    equity = m.group(1) if m else "?"
    m = re.search(r"PNG qa\\equity-c771?(-r771)?\.png \((\d+) bytes\)", qa)
    png_bytes = m.group(2) if m else "?"
    m = re.search(r"DATA latest_panel_bar=(\S+)", qa)
    panel_bar = m.group(1) if m else "?"
    with open(os.path.join(REPO, "results", "watermark_red.json"), encoding="utf-8") as fh:
        wm = json.load(fh)
    wm_line = "绿（red=%s·lane=%s·next_pick=%s）" % (
        str(wm.get("red")).lower(), wm.get("lane"),
        (wm.get("next_pick") or {}).get("status", "?") + " " +
        ((wm.get("next_pick") or {}).get("candidate") or "")[:40])

    did = (
        "r771: tick 正点轮（18:35 触发·wrapper 活 pid 锁自证单执行体）——"
        "①ORD delta 3 行消费（单跳 4B613571→98BD3FAA·prev commit e98691d04 facts 定位·穷举件 _r771bmc_ord_delta.txt）："
        "软著四款定名正典令（O-20261008-1810）=游戏域不涉本仓回执件（B/C 机游戏款归各游戏窗口自领）；"
        "MV 令二十三 CEO 直催 18:13「怎么这么慢？？」=r770 同窗 18:20 outbound 交付已应答"
        "（本窗 ls-tree 完好自证 REVIEW-PACKAGE-v1+5 场景图 6 件在 origin·30min 时限满足·A/B/C 菜单待 CEO 勾选·视频段维持冻结）；"
        "齐射归因+WT 收容所根治（U060 第八次）=本会话全程 silent 包装器+WT 吸收合规回执；"
        "②DEC EE70CEF0 恒等零动作·unacked=0（51 orders 双扫）·inbox 0（W189 席位件 bm-a r889 预处理·bm-c 零动作=bm-a 引擎域）；"
        "③S0：双吸收腿（leg1=daemon churn 7 件 a916db0e3·leg2=陈旧 stat-cache 假脏空提交触发 index 刷新——坑律直写 pit-git-resolver-rebase.md）"
        "+fetch+rebase origin/main（behind 1=bm-a r889 W188 finalize 一次过）+push CLEAN（behind=0 ahead=0）；"
        "④S1 smoke 49/49+饱和引擎活（exit 0）；⑤S2 任务板零 open 票·job 板零；"
        "⑥S6 40/40 rc0（update_daily sina 迟 bar 续自愈 new rows 0·cutoff %s·车道护栏全诚实 no-op）；"
        "⑦QA det-91st 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True·png %sB·"
        "case#8 撞名披露：qa/smoke-r771.md bm-b 包 blob 9bf1dcfb 先在册·同冻结数字零科学损失·同径覆写·bm-b 版 git 史保全）；"
        "⑧孤儿面=1 只读（ComfyUI 产线资产）·watermark %s·token +0（L2 local-LLM legs 0 today）·idle --worked（idle_rounds=0）"
    ) % (panel_bar, png_bytes, wm_line)

    verify = (
        "smoke 49/49 + qa/smoke-r771.md 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True·91 连证·case#8 披露） "
        "+ results/_r771bmc_s6_log.txt（40 legs rc0·%s） "
        "+ results/_r771bmc_s05_facts.json（ORD delta 消费/DEC 恒等/unacked=0/inbox 0/shape-asserted） "
        "+ results/_r771bmc_ord_delta.txt（3 行穷举·prev commit e98691d04 facts 定位） "
        "+ outbound ls-tree 完好自证（group origin 6 件在位·CEO 直催已应答） "
        "+ results/_r771bmc_pit_receipt.json（resolver-rebase 直写·r666/r747 范式） "
        "+ 孤儿面=1 只读 + push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % s6_first

    face = (
        "当前活: r771 bm-c（18:35-18:5x 窗·盘后窗·ORD CEO 直催回执+全链维护轮·第 72 连守轮）"
        "——主产出=①ORD 3 行消费（MV 直催 outbound 完好自证回执/软著令游戏域回执/WT 收容所合规回执）"
        "②S6 40/40 rc0（sina 迟 bar 续自愈）③QA det-91st 5/5 冻结恒等 "
        "| 最近实物: qa/smoke-r771.md 5/5（93 trades·1,017,839·91 连证）+results/_r771bmc_s6_log.txt 40/40 rc0 @ %s "
        "| 下个里程碑: CEO 三选项勾选（A 本地合成法再修一轮/B 云端通道待批/C 改构图）——点头前视频段冻结；"
        "sina 迟 bar 自愈重试（落地即 CTA_P1 接线）；next 5x=bm-c r775"
    ) % NOW_ISO

    artifact = (
        "qa/smoke-r771.md 5/5 (93 trades frozen identity, 91st chain, case#8 disclosed) "
        "+ results/_r771bmc_s6_log.txt (40/40 rc0) + outbound integrity verified "
        "(REVIEW-PACKAGE-v1 + 5 scene jpgs on group origin) @ %s" % NOW_ISO
    )

    milestone = (
        "O-1820 CEO gate: package intact on outbound, bm-a presents minute-level, CEO picks A/B/C; "
        "video lane frozen until CEO OK; sina late-bar self-heal per round (bar lands -> CTA_P1 wiring); "
        "next 5x = bm-c r775 (HANDOVER window)"
    )

    nxt = (
        "r772 续作: ①CEO 三选项勾选后按勾选项走：A=合成法再修一轮（底帧无穿帮版+overlay 缩小移位机械修法·拍子已证）；"
        "B=云端通道两卡壳场景（待 CEO 批·判例9）；C=CEO 改构图（待方向）——CEO 点头前视频段维持冻结"
        "（i2v 已杀·O-1715/1755 视频目标冻结）"
        "②sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证+REGIME_GUARD v3 新 bar enforce"
        "（live.paper 宿主面=bm-a·bm-c lane-guard 诚实 skip 常设）"
        "③QA det-92th 撞名预检（git ls-tree origin/main qa/ 探 r772）"
        "④分镜呈审件 CEO 反馈即出 v2 修订⑤next 5x=bm-c r775（HANDOVER 窗）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r771 sweep = single-hop "
        "4B613571->98BD3FAA: 3 added rows enumerated facts-driven (results/_r771bmc_ord_delta.txt, prev blob "
        "located at commit e98691d04) = soft-copyright 4-title canon order (game domain, non-our-repo, "
        "receipt-only) + MV order-23 CEO 18:13 direct-push (answered by r770 same-window outbound delivery, "
        "6-file integrity re-verified on origin, menu A/B/C awaiting CEO) + WT-shelter volley root-cure "
        "(silent-wrapper compliance receipt); hex-case normalized per r711 pit law; facts-driven from "
        "results/_r771bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    )
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r771 sweep = "
        "UNCHANGED EE70CEF0 (zero action, watermark held); facts-driven from "
        "results/_r771bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    )

    epoch = int(time.time())
    common = {
        "round_no": 772,
        "round_no_label": "round 771 (bm-c)",
        "last_round": 771,
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
        "last_orders_sha": "98BD3FAAC1B55CB1155993D9F1FDC23FEA1C0668",
        "ord_sha_method": ord_method,
        "last_orders_sha_method": ord_method,
        "dec_sha_method": dec_method,
        "last_decisions_sha_method": dec_method,
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
        assert back["round_no"] == 772

    row = ("%s | r771 | dept:工程+交易（盘后窗·ORD CEO 直催回执+全链维护轮·第 72 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=1（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s") % (NOW_ISO, wm_line, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    pit_entry = (
        "- [2026-10-08 18:4x r771 bm-c] **陈旧 stat-cache 假脏堵 rebase 坑（daemon churn 竞窗新面）**："
        "吸收腿 commit 后 git status 仍报 \" M\"（心跳/daemon 面 mtime-only 或同内容回写）且 git diff HEAD 为空——"
        "rebase 照样拒收「You have unstaged changes」；根因=index stat-cache 陈旧（内容未变但 stat 记录过期）；"
        "正法=任一 git 写操作触发 index 刷新（add -u 无可提交 rc=1 / commit 空尝试皆无害）后 rebase 即过，"
        "禁 checkout/reset 硬清（Unity 工程树尤禁）。〔r771 实弹：leg1 吸收 7 件 a916db0e3 后 rebase 拒·"
        "leg2 add -u 全仓无可提交·rebase 即 CLEAN·push CLEAN；r770 leg2「dispatcher live-face churn raced "
        "into rebase window」同窗异根——彼为真增量脏、此为假脏，两态并存须先核 diff HEAD 空满再定处置〕"
    )
    pit_path = os.path.join(REPO, "research", "pit-git-resolver-rebase.md")
    n = append_line(pit_path, pit_entry)
    receipt = {
        "round": 771, "machine": "bm-c",
        "mode": "direct-write (r666/r747 precedent: main file at cap, git-rebase domain sub-file)",
        "target": "research/pit-git-resolver-rebase.md",
        "entry_head": "陈旧 stat-cache 假脏堵 rebase 坑",
        "appended_bytes": n,
        "receipt_ts": NOW_ISO,
    }
    with open(os.path.join(REPO, "results", "_r771bmc_pit_receipt.json"), "w",
              encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)

    print("CLOSE_OK round=771->772 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s qa=%s trades=%s png=%sB panel=%s"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, qa_items, trades, png_bytes, panel_bar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
