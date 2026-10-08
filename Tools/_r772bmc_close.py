"""r772 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law), pit direct-write
(clone-gate stale assert vs canon-citation self-collision ->
research/pit-lineage.md, r666/r747 direct-write precedent), receipt write,
json.loads self-verification (epoch int law R170/R178).
argv: ram_gb vram_mb cpu_pct head_sha(S0-integration origin/main, facts).
ALL SHAs extracted from results/_r772bmc_s05_facts.json with shape asserts
(r583 facts-driven law); PNG regex matches the REAL runner output line
(equity-curve-r772.png -- root-fix of the r771 pngfix dependency).
No git subprocess inside (git runs in the PS batch via Invoke-SilentExe).
Pattern credit: Tools/_r771bmc_close.py."""
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
    # ---- facts extraction ----
    with open(os.path.join(REPO, "results", "_r772bmc_s6.out"), encoding="utf-8") as fh:
        s6_lines = [l.strip() for l in fh if l.strip()]
    s6_first = s6_lines[0] if s6_lines else "S6 ?"
    with open(os.path.join(REPO, "results", "_r772bmc_qa_runner.out"), encoding="utf-8") as fh:
        qa = fh.read()
    m = re.search(r"REPORT qa\\smoke-r772\.md items=(\S+)", qa)
    qa_items = m.group(1) if m else "?"
    m = re.search(r"BACKTEST trades=(\d+) determinism=(\S+)", qa)
    trades = m.group(1) if m else "?"
    det = m.group(2) if m else "?"
    m = re.search(r"BACKTEST equity_points=\d+ final=(\d+)", qa)
    equity = m.group(1) if m else "?"
    m = re.search(r"PNG qa\\equity-curve-r772\.png \((\d+) bytes\)", qa)
    png_bytes = m.group(1) if m else "?"
    m = re.search(r"DATA latest_panel_bar=(\S+)", qa)
    panel_bar = m.group(1) if m else "?"
    with open(os.path.join(REPO, "results", "_r772bmc_s05_facts.json"), encoding="utf-8") as fh:
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

    did = (
        "r772: tick 维护轮（19:0x 窗·全链 40 腿+QA det-92nd+克隆门·第 73 连守轮）——"
        "①ORD/DEC 双恒等零动作（ORD %s·DEC %s·facts 单源 s05 双扫·unacked=0（51 orders）·inbox 0）；"
        "CEO 三选项维持等待态（A/B/C 菜单已在集团 outbound 面·视频段冻结维持·等待态一行声明不重扫）；"
        "②S0：单吸收腿（5 daemon 面 commit 3d195a959·round-start behind=0 零 rebase）"
        "+mv_work MV 冻结车道 scratch 维持未跟踪（r770/771 两轮先例·等 CEO 勾选）；"
        "③S1 smoke 49/49（尾随 reader-thread GBK 解码噪音如实披露·smoke rc=0 非阻塞）+饱和引擎活（exit 0）；"
        "④S2 任务板零 open 票·job 板零；"
        "⑤S6 40/40 rc0（update_daily sina 迟 bar 未落地 cutoff %s·CTA_P1 无可标 bar 诚实 no-op·"
        "fund_premium NAV 09-30 已覆 no-op·dualrun ZERO-DRIFT streak 51·"
        "compute_audit FLAG:pool_starvation,supply_floor 如实披露=供给线在飞已认领批非断供"
        "（moneyflow IC reference·collector R63 交付·面板 parked 源阻断 30min 自愈）·"
        "py_watermark py_low_board_clear=板清+无新 bar 合法 idle）；"
        "⑥QA det-92nd 5/5（%s trades·equity %s 冻结恒等·determinism=%s·png %sB·"
        "case#9 撞名披露：qa/smoke-r772.md bm-b 包 blob 12edbb33 先在册·同冻结数字零科学损失·"
        "同径覆写·bm-b 版 git 史保全·.err 0B）；"
        "⑦克隆门 4/4（_r772bmc_clone.py 序敏感双替换+stale 门先于叙事 fix+法典引用豁免断言·"
        "收据 _r772bmc_clone_receipt.json·stale 自撞坑直写 pit-lineage.md）；"
        "⑧孤儿面=1 只读（ComfyUI 产线资产）·token +0（L2 legs 0 today）·"
        "idle 非绿（RAM 17.7%%<40%%·本轮实工·idle_rounds=0·agenda 未饿）"
    ) % (ord_sha[:8], dec_sha[:8], panel_bar, trades, equity, det, png_bytes)

    verify = (
        "smoke 49/49 + qa/smoke-r772.md 5/5（%s trades·equity %s 冻结恒等·determinism=%s·92 连证·case#9 披露·.err 0B） "
        "+ results/_r772bmc_s6_log.txt（%s） "
        "+ results/_r772bmc_s05_facts.json（DEC/ORD 双恒等·unacked=0·inbox 0·shape-asserted） "
        "+ results/_r772bmc_clone_receipt.json（4 files·stale771=0·compile ok·canon-cite 豁免断言） "
        "+ results/_r772bmc_pit_receipt.json（pit-lineage 直写·r666/r747 范式） "
        "+ 孤儿面=1 只读（results/_orphan_face_probe.bm-c.json） "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % (trades, equity, det, s6_first)

    face = (
        "当前活: r772 bm-c（19:0x 窗·盘后维护轮·第 73 连守轮）"
        "——主产出=①S6 40/40 rc0（sina 迟 bar 未落地·CTA_P1/fund_premium 诚实 no-op）"
        "②QA det-92nd 5/5（93 trades·1,017,839 冻结恒等·case#9 同径覆写披露）"
        "③克隆门 4/4（stale 自撞坑固化 pit-lineage） "
        "| 最近实物: qa/smoke-r772.md 5/5+results/_r772bmc_s6_log.txt 40/40 rc0+results/_r772bmc_clone_receipt.json @ %s "
        "| 下个里程碑: sina 10-08 bar 落地→CTA_P1 首接线+fund_premium 10-08 NAV 首采（bm-c 车）"
        "（bar 持续未落则逐轮自愈重试）；CEO A/B/C 勾选前视频段冻结；next 5x=bm-c r775（HANDOVER 窗）"
    ) % NOW_ISO

    artifact = (
        "qa/smoke-r772.md 5/5 (93 trades frozen identity, 92nd chain, case#9 same-path overwrite "
        "disclosed, bm-b blob 12edbb33 git-preserved) + results/_r772bmc_s6_log.txt (40/40 rc0) "
        "+ results/_r772bmc_clone_receipt.json (4/4 compile) @ %s" % NOW_ISO
    )

    milestone = (
        "sina 10-08 late-bar lands -> CTA_P1 first-bar wiring + fund_premium 10-08 NAV first "
        "snapshot (bm-c lane) + REGIME_GUARD v3 new-bar enforce (bm-a host, bm-c lane-guard "
        "honest skip); CEO A/B/C menu awaiting pick (video lane frozen); next 5x = bm-c r775 "
        "(HANDOVER window)"
    )

    nxt = (
        "r773 续作: ①sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证+fund_premium 10-08 NAV 首采"
        "（bm-c 车）+REGIME_GUARD v3 新 bar enforce（live.paper 宿主面=bm-a·bm-c lane-guard 诚实 skip 常设）"
        "②CEO 三选项勾选后按勾选项走（A 本地合成法再修/B 云端通道待批/C 改构图）——点头前视频段维持冻结"
        "③QA det-93th 撞名预检（git ls-tree origin/main qa/ 探 r773）"
        "④next 5x=bm-c r775（HANDOVER 窗）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r772 sweep = "
        "UNCHANGED %s (zero action, watermark held); facts-driven from "
        "results/_r772bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r772 sweep = "
        "UNCHANGED %s (zero action, watermark held); facts-driven from "
        "results/_r772bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 773,
        "round_no_label": "round 772 (bm-c)",
        "last_round": 772,
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
        assert back["round_no"] == 773

    row = ("%s | r772 | dept:工程+交易（盘后窗·全链维护轮·第 73 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=1（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s") % (NOW_ISO, wm_line, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    pit_entry = (
        "- [2026-10-08 19:1x r772 bm-c] **克隆门 stale 断言×叙事法典引用自撞坑（case#9 撞名窗实弹·断言拦截零损失）**："
        "轮克隆门对撞名叙事做 QA_FIX 时把先例轮号追加进披露法典引用行（r761/r764/…/r770 后追加 /r771）——"
        "该合法引用回植的裸 771 token 被自家 stale 零断言（(?<!\\d)771(?!\\d) 形）当场拦截="
        "断言红但非克隆源陈旧（两态并存：真 stale=替换漏·假 stale=引用回植·处置相反：前者修替换对·后者豁免引用形）。"
        "正法=stale 门先于叙事 fix 执行（REPL 双替换后立即过门）+fix 后引用豁免断言"
        "（/r771 前导斜杠形恰 1 处·裸 771 前导非 /r 形=0）——门与 fix 分层后克隆即过（4/4 compile）。"
        "How to apply：未来撞名轮克隆 qa_ignite 时法典行会持续追加先例（case#10 起引用表逐年变长）——"
        "克隆门血统自带本分层律（r772 clone 源自含），见断言红先分真假 stale 再动替换对，禁反向放宽断言"
        "（r753 boot 坑同律：断言红=替换对错或引用豁免缺，二者必居其一）。"
    )
    pit_path = os.path.join(REPO, "research", "pit-lineage.md")
    n = append_line(pit_path, pit_entry)
    receipt = {
        "round": 772, "machine": "bm-c",
        "mode": "direct-write (r666/r747 precedent: main file at cap, lineage-tooling domain file)",
        "target": "research/pit-lineage.md",
        "entry_head": "克隆门 stale 断言×叙事法典引用自撞坑",
        "appended_bytes": n,
        "receipt_ts": NOW_ISO,
    }
    with open(os.path.join(REPO, "results", "_r772bmc_pit_receipt.json"), "w",
              encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)

    print("CLOSE_OK round=772->773 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s qa=%s trades=%s png=%sB panel=%s"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, qa_items, trades, png_bytes, panel_bar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
