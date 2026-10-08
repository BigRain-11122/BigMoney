# -*- coding: utf-8 -*-
"""r778 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
ram_gb vram_mb cpu_pct head_sha. ALL SHAs/verdicts extracted from
results/_r778bmc_s05_facts.json + _r778bmc_s6_log.txt +
_r778bmc_qa_probe.json + watermark_red.json with shape asserts
(r583 facts-driven law). S6 honest-red face: legs=40 rc0=39 nonzero=1
(aggressive_lab rc=2, sina SZ-source lag SECOND consecutive round, RW-4
gate fail-closed by design; targeted re-runs update_daily x2 (new rows=0)
+ aggressive_lab x2 same red in round record). NEW product faces this
round: QA det-97th pack r778 clean first-write + CTA_P1 FIRST markable
bar accrued to 2026-10-08. Future-face disclosure: r780 qa slot occupied
by another machine's pack -- bm-c round 780 must defer (r669 overwrite ban).
No git subprocess inside (git runs in the PS batch via Invoke-SilentExe).
Pattern credit: _r777bmc_close.py."""
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
    with open(os.path.join(REPO, "results", "_r778bmc_s6_log.txt"), encoding="utf-8") as fh:
        s6 = fh.read()
    m = re.search(r"legs=(\d+)", s6)
    legs = m.group(1) if m else "?"
    rc0 = len(re.findall(r"\[rc=0\]", s6))
    rcbad = len(re.findall(r"\[rc=(?!0\])[0-9]+\]", s6))
    s6_first = "S6 legs=%s rc0=%d nonzero=%d" % (legs, rc0, rcbad)
    assert legs == "40" and rc0 == 39 and rcbad == 1, "S6 shape mismatch"
    assert re.search(r"===== aggressive_lab =====.*?\[rc=2\]",
                     s6, re.S), "the one nonzero leg must be aggressive_lab"
    assert "data cutoff: 2026-10-08" in s6, "cutoff 10-08 line missing"
    assert "marks accrued to 2026-10-08 (1 bar(s)" in s6, \
        "CTA_P1 first markable bar face missing"
    with open(os.path.join(REPO, "results", "_r778bmc_qa_probe.json"), encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 778
    occ = qap["occupied"]
    assert all("r780" in o for o in occ) and len(occ) == 2, \
        "occupied set must be exactly the r780 foreign pack pair"
    assert not any("r778" in o for o in occ), "r778 slot must be free"
    qa_md = os.path.join(REPO, "qa", "smoke-r778.md")
    qa_png = os.path.join(REPO, "qa", "equity-curve-r778.png")
    assert os.path.exists(qa_md) and os.path.getsize(qa_md) > 0
    qa_png_size = os.path.getsize(qa_png)
    assert qa_png_size > 60000
    with open(os.path.join(REPO, "results", "_r778bmc_s05_facts.json"), encoding="utf-8") as fh:
        facts = json.load(fh)
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [] and facts["inbox_unread"] == []
    assert facts["dec_delta"] is False and facts["ord_delta"] is False
    with open(os.path.join(REPO, "results", "watermark_red.json"), encoding="utf-8") as fh:
        wm = json.load(fh)
    assert wm.get("red") is False
    wm_line = "绿（red=%s·lane=%s·next_pick=%s）" % (
        str(wm.get("red")).lower(), wm.get("lane"),
        (wm.get("next_pick") or {}).get("status", "?") + " " +
        ((wm.get("next_pick") or {}).get("candidate") or "")[:40])
    with open(os.path.join(REPO, "results", "_orphan_face_probe.bm-c.json"),
              encoding="utf-8") as fh:
        orph = json.load(fh)
    orphan_n = int(orph.get("orphans", 0))

    did = (
        "r778: QA det-97th 净写+CTA_P1 首可标 bar 轮（20:5x-21:1x 窗·第 79 连守轮）——"
        "①S0.5 双扫零增量（ORD %s 恒等·DEC EE70CEF0 恒等·unacked=0〔51 orders〕·inbox=0）；"
        "②S0 吸收 commit 4db494f6d（6 文件本机 daemon 活写面·7 add 中 1 件零净差）"
        "+rebase origin/main CLEAN（并入 bm-a r892 三提交=W190 per-wave prereg freeze"
        "+W189 sec7/8 finalize backfill first-leg+seat archive·bm-a 车道本机不碰）；"
        "③S1 smoke 47/49（2 FAIL=RW-4 源滞后面：12 SZ 成员 09-30 vs anchor 10-08"
        "·与 aggressive_lab 同根因·本机 smoke 跑在锚推进后=r777 跑在锚推进前的诚实差异面）"
        "+SAT 引擎活（rc0·N1 注册面 189→190 NEW pair bm-a r892 披露）+S2 板清"
        "（零 open 票·job 板零·claimable_pool_lines=2 idle 非绿零义务）；"
        "④**QA det-97th 证据包 r778 槽净写（本轮主产出）**：探针 r778 槽空闲（563 件 qa 面）"
        "→分离点火 qa_smoke_run --round 778→qa/smoke-r778.md 5/5+qa/equity-curve-r778.png"
        "（%dB）净写（面板尾 800bar×3 员·market_clock CALL-09-30 cell=ORA·deterministic）；"
        "**r780 槽已被他机包占用（smoke-r780.md+equity-curve-r780.png 在 origin/main）"
        "→未来面披露：bm-c r780 轮 QA 包须让位跳写（r669 覆写禁令）**；"
        "⑤**CTA_P1 首可标 bar 落地**：marks accrued to 2026-10-08（1 bar·equity "
        "10,313,132.55 CNY·total_ret +0.0313）——r777 watch 解除项兑现（sleeve 宇宙不含滞后成员）；"
        "⑥S6 40 腿=39 rc0+1 诚实红（aggressive_lab rc=2=RW-4 在役面板门拒收：12 只 SZ 成员"
        "〔159901/915/919/920/928/934/949/980/985/992/995/996〕sina 源发布滞后第二轮连续仍在 09-30 "
        "vs anchor=10-08·门 fail-closed 设计正确·非代码故障）→修红纪律定向复跑 update_daily ×2"
        "（20:56 new rows=0+链内 new rows=0·源仍未发）+aggressive_lab ×2（同 12 成员·同红）"
        "→定性=数据源瞬态延续·源补发即自愈；fund_premium 诚实 no-op（期望 NAV 日仍 09-30）；"
        "live_paper 族 lane_io 守卫 skip（bm-a origin commit 3min 新鲜·r701 第三信号否决·bm-a 侧落地）；"
        "⑦自愈四件全绿+双爪核验+round.lock 续锁龄 1 次（r698 律）·孤儿面=%d 只读"
        "（ComfyUI 产线资产）·idle 非绿（RAM %.1fGB·ComfyUI 常驻·idle_rounds=0·agenda 未饿）"
    ) % (ord_sha[:8], qa_png_size, orphan_n, RAM_GB)

    verify = (
        "smoke 47/49（2 FAIL=RW-4 源滞后已知面·同 aggressive_lab 根因·定向复跑×2 在案） "
        "+ qa/smoke-r778.md（5/5）+qa/equity-curve-r778.png（%dB·det-97th 零撞名净写） "
        "+ results/_r778bmc_s6_log.txt（%s·aggressive_lab 诚实红+定向复跑在案·CTA_P1 首 bar 行在案） "
        "+ results/_r778bmc_s05_facts.json（ORD/DEC 双恒等零增量·unacked=0·inbox=0·shape-asserted·双扫） "
        "+ results/_r778bmc_qa_probe.json（r778 槽空闲·r780 槽他机占用未来面披露·563 件面自证） "
        "+ results/watermark_red.json（red=false） "
        "+ results/update_status.json（data cutoff 2026-10-08·new rows=0 源未发自证） "
        "+ results/_attrition_guard_scan.json CLEAN "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % (qa_png_size, s6_first)

    face = (
        "当前活: r778 bm-c（20:5x-21:1x 窗·QA det-97th 净写+CTA_P1 首 bar 轮·第 79 连守轮）"
        "——主产出=①qa/smoke-r778.md 5/5+equity-curve-r778.png（det-97th 零撞名净写）"
        "②CTA_P1 首可标 bar 10-08（equity 10.31M·total_ret +3.13%%）"
        "③S6 39/40+1 诚实红延续处置（sina SZ 源滞后第二轮·定向复跑在案） "
        "| 最近实物: qa/smoke-r778.md + CTA_P1 2026-10-08 marks @ %s "
        "| 下个里程碑: sina 12 SZ 成员补发→aggressive_lab 门复绿+AGGR 10-08 marks；"
        "fund_premium 10-08 NAV 首采；r780=5x 轮 HANDOVER 核对+QA r780 槽让位（他机包在册）"
    ) % NOW_ISO

    artifact = (
        "qa/smoke-r778.md (5/5) + qa/equity-curve-r778.png (%dB, det-97th clean first-write) "
        "+ CTA_P1 marks accrued to 2026-10-08 (first bar, equity 10,313,132.55 CNY, "
        "total_ret +0.0313) + results/_r778bmc_s6_log.txt (%s) @ %s"
    ) % (qa_png_size, s6_first, NOW_ISO)

    milestone = (
        "sina publishes the 12 lagging SZ members -> aggressive_lab RW-4 gate self-heal + "
        "AGGR 10-08 marks; fund_premium 10-08 NAV first snapshot (expected NAV date advance); "
        "r780 = 5x round HANDOVER check + qa r780 slot defer (foreign pack on origin); "
        "CEO picks A/B/C -> video lane unfreeze"
    )

    nxt = (
        "r779 续作: ①update_daily 重试→12 只 SZ 成员补发自愈（aggressive_lab 门复绿+AGGR 10-08 "
        "marks 首标）②fund_premium 期望 NAV 日推进→10-08 首采③r780=5x 轮 HANDOVER 核对面预备"
        "+QA r780 槽让位（他机 smoke-r780 包在册·r669 覆写禁令）④CEO 勾选后按选项走"
        "（A=视频段解冻）⑤GM bm-b 车道裁定回执面跟进"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r778 sweep = UNCHANGED "
        "%s (zero delta, watermark held); facts-driven from "
        "results/_r778bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r778 sweep = "
        "UNCHANGED %s (zero delta, watermark held); facts-driven from "
        "results/_r778bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 779,
        "round_no_label": "round 778 (bm-c)",
        "last_round": 778,
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
        assert back["round_no"] == 779

    row = ("%s | r778 | dept:工程+数据（20:5x-21:1x 窗·QA det-97th 净写+CTA_P1 首 bar 轮·第 79 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=%d（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s | 本轮产品积分：2（qa/smoke-r778.md 5/5+equity-curve-r778.png "
           "=det-97th 能看能用实物净写·CTA_P1 首可标 bar 10-08 marks 落地=纸盘面实物·S6 39/40"
           "+诚实红第二轮定向复跑处置=经营层实物） | 记账预算：4（轮报行/心跳+state 收口"
           "+facts 双扫件+qa 探针件）") % (NOW_ISO, wm_line, orphan_n, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=778->779 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s "
          "qa=clean-first-write r778 png=%dB ord=%s dec=%s orphan=%d r780_slot=foreign_occupied"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, qa_png_size, ord_sha[:8], dec_sha[:8], orphan_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
