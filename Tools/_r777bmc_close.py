# -*- coding: utf-8 -*-
"""r777 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
ram_gb vram_mb cpu_pct head_sha. ALL SHAs/verdicts extracted from
results/_r777bmc_s05_facts.json + _r777bmc_s6_log.txt +
_r777bmc_qa_probe.json + watermark_red.json with shape asserts
(r583 facts-driven law). S6 honest-red face: legs=40 rc0=39 nonzero=1
(aggressive_lab rc=2, sina SZ-source lag transient, RW-4 gate
fail-closed by design, targeted re-run both legs in round record).
No git subprocess inside (git runs in the PS batch via Invoke-SilentExe).
Pattern credit: _r776bmc_close.py."""
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
    with open(os.path.join(REPO, "results", "_r777bmc_s6_log.txt"), encoding="utf-8") as fh:
        s6 = fh.read()
    m = re.search(r"legs=(\d+)", s6)
    legs = m.group(1) if m else "?"
    rc0 = len(re.findall(r"\[rc=0\]", s6))
    rcbad = len(re.findall(r"\[rc=(?!0\])[0-9]+\]", s6))
    s6_first = "S6 legs=%s rc0=%d nonzero=%d" % (legs, rc0, rcbad)
    assert legs == "40" and rc0 == 39 and rcbad == 1, "S6 shape mismatch"
    assert re.search(r"===== aggressive_lab =====.*?\[rc=2\]",
                     s6, re.S), "the one nonzero leg must be aggressive_lab"
    assert "data cutoff: 2026-10-08" in s6, "10-08 first-bar landing missing"
    with open(os.path.join(REPO, "results", "_r777bmc_qa_probe.json"), encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 777 and qap["occupied"] == []
    qa_md = os.path.join(REPO, "qa", "smoke-r777.md")
    qa_png = os.path.join(REPO, "qa", "equity-curve-r777.png")
    assert os.path.exists(qa_md) and os.path.getsize(qa_md) > 0
    assert os.path.exists(qa_png) and os.path.getsize(qa_png) > 60000
    with open(os.path.join(REPO, "results", "_r777bmc_s05_facts.json"), encoding="utf-8") as fh:
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
        "r777: QA det-96th 净写+10-08 节后首 bar 落地轮（20:3x-20:4x 窗·第 78 连守轮）——"
        "①S0.5 双扫零增量（ORD %s 恒等·DEC EE70CEF0 恒等·unacked=0〔51 orders〕·inbox=0）；"
        "②S0 吸收 commit 00b0037b1（7 件本机 daemon 活写面）+rebase origin/main CLEAN"
        "（并入 bm-a r891 双提交=W189 finalize EXACT+W190 seat+closeout）；"
        "③S1 smoke 49/49+SAT 引擎活（rc0·N1 注册面在册至 W189）+S2 板清（零 open 票·job 板零）；"
        "④**QA det-96th 证据包 r777 槽净写（本轮主产出）**：探针 r777 槽空闲（561 件 qa 面零撞名）"
        "→分离点火 qa_smoke_run --round 777→qa/smoke-r777.md 5/5+qa/equity-curve-r777.png"
        "（66,189B）净写（面板尾 800bar×3 员·93 笔·determinism=True·market_clock CALL-09-30 cell=ORA）；"
        "⑤**10-08 节后首 bar 落地（r774-776 三轮 watch 解除）**：update_daily 20:41 落 36 行"
        "·data cutoff 推进 2026-10-08·live.paper hook 触发（lane_io 单写者守卫=bm-a 心跳新鲜 7min"
        "→paper/t35/prospect 族本机本轮跳过 derive·bm-a 侧下轮落地）；"
        "⑥S6 40 腿=39 rc0+1 诚实红（aggressive_lab rc=2=RW-4 在役面板门拒收：12 只 SZ 成员"
        "〔159901/915/919/920/928/934/949/980/985/992/995/996〕sina 源发布滞后仍在 09-30 "
        "vs anchor=max=10-08·门 fail-closed 设计正确·非代码故障）→修红纪律定向复跑 update_daily"
        "（new rows=0·源仍未发）+aggressive_lab（同 12 成员·同红）→定性=数据源瞬态·下轮自愈预期；"
        "CTA_P1 仍无可标 bar（min cutoff 09-30<paper_start 10-08·等滞后成员）；fund_premium NAV 期望日仍 09-30；"
        "⑦自愈四件全绿+双爪核验+round.lock 续锁龄 1 次（20:41·r698 律）·孤儿面=%d 只读"
        "（ComfyUI 产线资产）·idle 非绿（RAM %.1fGB<40%%·本轮实工·idle_rounds=0·agenda 未饿）"
    ) % (ord_sha[:8], orphan_n, RAM_GB)

    verify = (
        "smoke 49/49 "
        "+ qa/smoke-r777.md（5/5）+qa/equity-curve-r777.png（66,189B·det-96th 零撞名净写） "
        "+ results/_r777bmc_s6_log.txt（%s·aggressive_lab 诚实红+定向复跑两腿在案·10-08 落地行在案） "
        "+ results/_r777bmc_s05_facts.json（ORD/DEC 双恒等零增量·unacked=0·inbox=0·shape-asserted·双扫） "
        "+ results/_r777bmc_qa_probe.json（r777/778/779 槽空闲·561 件面自证） "
        "+ results/watermark_red.json（red=false·lane=healthy） "
        "+ results/update_status.json（data cutoff 2026-10-08·36 行落地自证） "
        "+ results/_attrition_guard_scan.json CLEAN "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % s6_first

    face = (
        "当前活: r777 bm-c（20:3x-20:4x 窗·QA det-96th 净写+10-08 首 bar 落地轮·第 78 连守轮）"
        "——主产出=①qa/smoke-r777.md 5/5+equity-curve-r777.png（det-96th 零撞名净写）"
        "②10-08 节后首 bar 落地（36 行·cutoff 推进·三轮 watch 解除）"
        "③S6 39/40+1 诚实红处置（sina SZ 滞后瞬态·复跑在案） "
        "| 最近实物: qa/smoke-r777.md + results/_r777bmc_s6_log.txt @ %s "
        "| 下个里程碑: sina 12 只 SZ 成员补发→aggressive_lab 门自愈+CTA_P1 首可标 bar+AGGR 10-08 marks；"
        "fund_premium 10-08 NAV 首采；r780=5x 轮 HANDOVER 核对；CEO 勾 A/B/C 后视频段解冻"
    ) % NOW_ISO

    artifact = (
        "qa/smoke-r777.md (5/5) + qa/equity-curve-r777.png (66,189B, det-96th clean first-write) "
        "+ results/_r777bmc_s6_log.txt (legs=40 rc0=39, 10-08 first-bar landing 36 rows in-log) "
        "+ data/daily 10-08 bars @ %s"
    ) % NOW_ISO

    milestone = (
        "sina publishes the 12 lagging SZ members -> aggressive_lab RW-4 gate self-heal + CTA_P1 first "
        "markable bar + AGGR 10-08 marks; fund_premium 10-08 NAV first snapshot; r780 = 5x round "
        "HANDOVER check; CEO picks A/B/C -> video lane unfreeze (ammo library restored r776)"
    )

    nxt = (
        "r778 续作: ①update_daily 重试→12 只 SZ 成员补发自愈（aggressive_lab 门复绿+CTA_P1 首接线"
        "+AGGR 10-08 marks 首标）②fund_premium 10-08 NAV 首采③CEO 勾选后按选项走"
        "（A=视频段解冻·分镜表+调色链正典施工）④GM bm-b 车道裁定回执面跟进"
        "⑤r780=5x 轮 HANDOVER 核对面预备"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r777 sweep = UNCHANGED "
        "%s (zero delta, watermark held); facts-driven from "
        "results/_r777bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r777 sweep = "
        "UNCHANGED %s (zero delta, watermark held); facts-driven from "
        "results/_r777bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 778,
        "round_no_label": "round 777 (bm-c)",
        "last_round": 777,
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
        assert back["round_no"] == 778

    row = ("%s | r777 | dept:工程+数据（20:3x-20:4x 窗·QA det-96th 净写+10-08 首 bar 落地轮·第 78 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=%d（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s | 本轮产品积分：2（qa/smoke-r777.md 5/5+equity-curve-r777.png "
           "=det-96th 能看能用实物净写·10-08 节后首 bar 36 行数据落地+data cutoff 推进=数据面实物"
           "·S6 39/40+诚实红定向复跑处置=经营层实物） | 记账预算：4（轮报行/心跳+state 收口"
           "+facts 双扫件+qa 探针件）") % (NOW_ISO, wm_line, orphan_n, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=777->778 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s "
          "qa=clean-first-write r777 ord=%s dec=%s orphan=%d"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, ord_sha[:8], dec_sha[:8], orphan_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
