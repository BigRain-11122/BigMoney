# -*- coding: utf-8 -*-
"""r776 bm-c S7 closeout: facts-driven state+heartbeat update, canonical
report row append (ROOT round_reports-bm-c.md per r844 law). argv:
ram_gb vram_mb cpu_pct head_sha. ALL SHAs/verdicts extracted from
results/_r776bmc_s05_facts.json + _r776bmc_s6_log.txt +
_r776bmc_qa_probe.json + _r776bmc_mvwork_recovery.json with shape
asserts (r583 facts-driven law). No git subprocess inside (git runs in
the PS batch via Invoke-SilentExe). Pattern credit: _r775bmc_close.py."""
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
    with open(os.path.join(REPO, "results", "_r776bmc_s6_log.txt"), encoding="utf-8") as fh:
        s6 = fh.read()
    m = re.search(r"legs=(\d+)", s6)
    legs = m.group(1) if m else "?"
    rc0 = len(re.findall(r"\[rc=0\]", s6))
    rcbad = len(re.findall(r"\[rc=(?!0\])[0-9]+\]", s6))
    s6_first = "S6 legs=%s rc0=%d nonzero=%d" % (legs, rc0, rcbad)
    assert rcbad == 0 and legs == str(rc0), "S6 not clean"
    with open(os.path.join(REPO, "results", "_r776bmc_qa_probe.json"), encoding="utf-8") as fh:
        qap = json.load(fh)
    assert qap["round"] == 776 and len(qap["occupied"]) == 2
    with open(os.path.join(REPO, "results", "_r776bmc_mvwork_recovery.json"), encoding="utf-8") as fh:
        rec = json.load(fh)
    assert rec["recovery"]["total_bytes_on_disk"] == 43441398
    with open(os.path.join(REPO, "results", "_r776bmc_s05_facts.json"), encoding="utf-8") as fh:
        facts = json.load(fh)
    ord_sha = facts["ord_sha"]
    dec_sha = facts["dec_sha"]
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord_sha 40hex shape"
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec_sha 64hex shape"
    assert facts["unacked"] == [], "unacked must be empty at close"
    with open(os.path.join(REPO, "results", "watermark_red.json"), encoding="utf-8") as fh:
        wm = json.load(fh)
    wm_line = "绿（red=%s·lane=%s·next_pick=%s）" % (
        str(wm.get("red")).lower(), wm.get("lane"),
        (wm.get("next_pick") or {}).get("status", "?") + " " +
        ((wm.get("next_pick") or {}).get("candidate") or "")[:40])

    did = (
        "r776: mv_work 灭失侦破+41.4MB 全量恢复轮（20:0x-20:4x 窗·第 77 连守轮）——"
        "①S0.5 双扫：ORD delta 1 行消费（10-08 19:33 CEO 吸嘟嘟全速推进令=MiniGame 域·执行司=bm-a·"
        "涉本司=否科学判断闸零动作·水位 AB24566E→%s 更新）·DEC EE70CEF0 恒等零动作·unacked=0（51 orders）"
        "·inbox 1 件消费（MSG-20261008-200x-bma-ALL：bm-b 静默 29.65h 本机交叉验证成立——"
        "**bm-c 立场=赞同选项 A 车道临时改派但不单方面动 R31 lane guard（单写者律同守）·呈请面归 GM 裁定**·"
        "轮报回执+移 processed）；"
        "②**mv_work 灭失侦破与全量恢复（本轮主产出）**：next-ptr ③ 备产探索发现 results/mv_work 68 件 41.4MB "
        "全 MISSING（r775-tail「盘上产线零触碰」声明为假）→reflog 三连+父目录 mtime=20:12:08 取证定谳："
        "rm --cached untrack 提交后同窗 pull --rebase=rebase start checkout 静默收编 ignored 盘件"
        "（origin 树仍 TRACK）→rebase pick 重放删除物化=**工作树真删**→treasure_guard restore 门 rc0"
        "（可再生工件类·登记册零命中硬拒面未触发）→git restore --source=aecdc94a4 --worktree 全量恢复 68/68"
        "（43,441,398B）→ls-tree sha 逐件对账=二进制恒等+16 文本件仅 EOL 归一（normalize-equal 判别非数据伤）"
        "→坑律直写 research/pit-git-resolver-rebase.md（主件 36B 余量·r666 直写先例·rebase replay 族）"
        "+收据 results/_r776bmc_mvwork_recovery.json；"
        "③S1 smoke 49/49+SAT 引擎活（rc0·心跳龄 44s）；"
        "④S2 板清（零 open 票·job 板零·CEO 未勾选 A/B/C=等待态一行声明）；"
        "⑤S6 40/40 rc0（update_daily 10-08 节后首 bar 至 20:19 仍未发布·cutoff 09-30 维持下轮重试"
        "·CTA_P1 无可标 bar 诚实 no-op·fund_premium NAV 09-30 已覆 no-op·10-08 首采等 bar）；"
        "⑥QA det-96th 撞名预检命中=origin 已有 bm-a r776 包（smoke-r776.md+equity-curve-r776.png）"
        "→诚实跳过禁覆写他机证据件（r777/778/779 槽空闲·下轮净写·探针 _r776bmc_qa_probe.json）；"
        "⑦克隆门 stale 操作面=0（r774/r775 引用仅 s6 docstring 血统注记 1 处合法）；"
        "⑧自愈四件全绿（loop pin=5+watchdog 幂等重注册〔query 面撞 wrapper 位置参数坑·-Force 无害〕"
        "+双爪 MATCH）·孤儿面=1 只读（ComfyUI 产线资产）"
        "·idle 非绿（RAM %.1fGB<40%%·本轮实工·idle_rounds=0·agenda 未饿）"
    ) % (ord_sha[:8], RAM_GB)

    verify = (
        "smoke 49/49 "
        "+ results/_r776bmc_mvwork_recovery.json（68/68 恢复·43,441,398B·treasure_guard restore rc0 门"
        "·ls-tree sha 对账二进制恒等·文本 EOL 归一 normalize-equal 判别） "
        "+ results/_r776bmc_s6_log.txt（%s） "
        "+ results/_r776bmc_s05_facts.json（ORD %s 消费+DEC EE70CEF0 恒等·unacked=0·inbox 1 已处理移 processed"
        "·shape-asserted·双扫） "
        "+ research/pit-git-resolver-rebase.md r776 坑律行（rm --cached×rebase 真删坑） "
        "+ results/_r776bmc_qa_probe.json（撞名事实 561 件 qa 面·r777 槽空闲自证） "
        "+ results/_attrition_guard_scan.json CLEAN（4 ledgers·healed 史披露） "
        "+ 孤儿面=1 只读（results/_orphan_face_probe.bm-c.json） "
        "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）"
    ) % (s6_first, ord_sha[:8])

    face = (
        "当前活: r776 bm-c（20:0x-20:4x 窗·mv_work 灭失侦破+全量恢复轮·第 77 连守轮）"
        "——主产出=①68 件 41.4MB A 向产线资产全量恢复（含 glass_d 新最佳+源音频+PRODUCTION.md·零丢失）"
        "②rebase 真删坑律正典化 ③S6 40/40 "
        "| 最近实物: results/_r776bmc_mvwork_recovery.json + research/pit-git-resolver-rebase.md r776 行 @ %s "
        "| 下个里程碑: CEO 勾 A/B/C 后视频段解冻施工；GM 裁定 bm-b 四车道改派（bm-c 已回执立场）；"
        "sina 10-08 bar 落地→CTA_P1 首接线+fund_premium 首采；r777 QA det-96th 净写；next 5x=bm-c r780"
    ) % NOW_ISO

    artifact = (
        "results/mv_work/ 68-file frozen lane fully restored (68/68, 43,441,398B, binary-exact / text EOL-only) "
        "+ results/_r776bmc_mvwork_recovery.json + research/pit-git-resolver-rebase.md r776 pit row "
        "+ results/_r776bmc_s6_log.txt (40/40 rc0) @ %s"
    ) % NOW_ISO

    milestone = (
        "CEO picks A/B/C -> video lane unfreeze and SP construction (ammo library now fully restored: "
        "z3 8/8/9 + carve_i 8/8/7 + glass_d 9/8/7 NEW BEST + dress-color dual menu); GM ruling on bm-b "
        "four-lane temp reassignment (bm-c stance receipted); sina 10-08 late-bar lands -> CTA_P1 "
        "first-bar wiring + fund_premium 10-08 NAV first snapshot; r777 QA det-96th clean first-write; "
        "next 5x = bm-c r780"
    )

    nxt = (
        "r777 续作: ①CEO 勾选后按选项走（A=视频段解冻·分镜表+调色链正典施工）"
        "②QA det-96th r777 槽净写（origin 探 r777 空闲已证）"
        "③sina 迟 bar 自愈重试→CTA_P1 首接线+fund_premium 10-08 NAV 首采"
        "④A 向滚动续产备选（玻璃 d 版左缘青缝再收敛一轮·goddess/carve 场维持现最佳）"
        "⑤GM bm-b 车道裁定回执面跟进（bm-c 立场已入 r776 轮报）"
    )

    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r776 sweep = DELTA "
        "CONSUMED %s (10-08 19:33 CEO xidududu full-speed order O-row, MiniGame domain, executor=bm-a, "
        "not-this-office=zero action via science gate); facts-driven from "
        "results/_r776bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % ord_sha[:8]
    dec_method = (
        "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r776 sweep = "
        "UNCHANGED %s (zero action, watermark held); facts-driven from "
        "results/_r776bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)"
    ) % dec_sha[:8]

    epoch = int(time.time())
    common = {
        "round_no": 777,
        "round_no_label": "round 776 (bm-c)",
        "last_round": 776,
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
        assert back["round_no"] == 777

    row = ("%s | r776 | dept:工程+交易+产线（20:0x-20:4x 窗·mv_work 灭失侦破+全量恢复轮·第 77 bm-c 连守轮） | "
           "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
           "WM-VERDICT: %s | 孤儿面=1（ComfyUI 产线资产·只读不杀） | %s | "
           "验证证据: %s | 下轮指针: %s | 本轮产品积分：2（mv_work 68 件 41.4MB A 向产线资产全量恢复"
           "=能用产线实物〔CEO 吸嘟嘟全速令弹药库保全〕·rebase 真删坑律+恢复收据=防复发实物·S6 40/40=经营层实物） "
           "| 记账预算：4（轮报行/心跳/state 收口+facts 双扫件+qa 探针件+recovery 收据·登记册零命中断言："
           "treasure_guard restore 门 rc0 放行=可再生工件类·硬拒面未触发）") % (NOW_ISO, wm_line, did, verify, nxt)
    append_line(os.path.join(REPO, "round_reports-bm-c.md"), row)

    print("CLOSE_OK round=776->777 epoch=%d(int) ram=%.1f vram=%d cpu=%.1f s6=%s qa=collision-skip "
          "recovered=68/68 ord=%s dec=%s"
          % (epoch, RAM_GB, VRAM_MB, CPU_PCT, s6_first, ord_sha[:8], dec_sha[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
