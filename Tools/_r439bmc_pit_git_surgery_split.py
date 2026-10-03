# -*- coding: utf-8 -*-
"""r439 bm-c: D-06 pit-git sub-split batch-1 -- SURGERY family, pit-git.md -> research/pit-git-surgery.md.

Scope (hand-curated surgery/closeout/yield/phantom-D/CAS/temp-index family, 40 entries):
让路手术 + closeout 扫树 + 外科推送/CAS 直投/temp-index + 删除集自证/pre-push 爪归属门 +
术后 realign M 面分类族 (r365/r369-claw/r374/r387-CAS/r516/r518/r524/r525/r530/r540/r559/r561/
r563/r568-fork/r574/r578/r585/r586/r588/r589-realign/r590/r595/r604/r607/r612/r615/r636 ...).
Mechanism = r335 machine-migration law (byte-level line surgery, no hand copying);
template = Tools/_r416bmc_pit_spawn_split.py (D-06 batch-3 canon).
Modes:
    python Tools/_r439bmc_pit_git_surgery_split.py            # do the split
    python Tools/_r439bmc_pit_git_surgery_split.py --verify    # independent re-check
Laws applied: r407 (CJK surgery via script not CLI replace), r614 (os.replace atomic),
r414 (PYTHONIOENCODING=utf-8), already-migrated law (anchors absent from sibling pit-*.md).
Source face: research/pit-git.md is CRLF (146 CR == 146 LF lines at r439 probe).
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "pit-git.md")
DST = os.path.join(ROOT, "research", "pit-git-surgery.md")
RECEIPT = os.path.join(ROOT, "results", "_r439bmc_pit_git_surgery_split.json")
SIBLINGS = ["pit-pool.md", "pit-engine.md", "pit-protocol.md", "pit-data.md",
            "pit-ps.md", "pit-encoding.md", "pit-spawn.md", "pit-tooling.md"]

ANCHORS = [
    "- [2026-10-02 12:3x r365 bm-c] 整树面 phantom-D 回退",
    "- [2026-10-02 14:1x r369 bm-c] pre-push claw 竞速窗 bad-object 误拦坑",
    "- [2026-10-02 13:1x r366 bm-c] 外科 update-index ls-tree 列位切错坑",
    "- [2026-10-01 16:3x r323 bm-c] 让路手术三增量坑",
    "- [2026-10-01 16:5x r524 bm-a] 外科推送后 reset --mixed 工作树滞后窗坑",
    "- [2026-10-01 17:2x r513 bm-b] closeout 跨机误删",
    "- [2026-10-01 17:0x r525 bm-a] yield 弃置删件必逐件验归属坑",
    "- [2026-10-01 17:4x r326 bm-c] closeout 扫树病第三犯治愈实录",
    "- [2026-10-01 18:1x r516 bm-b] temp-index 外科 payload 删除 staging 坑",
    "- [2026-10-01 19:0x r518 bm-b] 同窗双冻撞带让路手术三坑合订",
    "- [2026-10-01 19:1x r531 bm-a] 同锚双加冲突机械 hunk-union 乱序穿插坑",
    "- [2026-10-01 19:5x r331 bm-c] 外科 rebroadcast 整树面 stale 基",
    "- [2026-10-01 20:1x r519 bm-b] closeout 扫树第 4 犯",
    "- [2026-10-01 22:1x r540 bm-a] r519 族第 5 犯",
    "- [2026-10-02 01:4x r530 bm-b] 外科重父复用 stale tree",
    "- [2026-10-02 01:5x r343 bm-c] git diff-index 缺 --cached",
    "- [2026-10-02 06:0x r559 bm-a] git push 漏 remote 名",
    "- [2026-10-02 06:5x r561 bm-b] reset --soft 让路重落",
    "- [2026-10-02 07:1x r354 bm-c] 猝死会话 S0 外科脚本",
    "- [2026-10-02 07:5x r563 bm-b] 验属×树变交割窗坑",
    "- [2026-10-02 10:4x r568 bm-a] 外科推送 payload 必须从 fork 点 derive",
    "- [2026-10-02 12:1x r574 bm-a] 外科 commit-tree message 源盲取 HEAD 坑",
    "- [2026-10-02 18:5x r588 bm-a] 外科 reset --mixed 后 M 面前缀分类驱动坑",
    "- [2026-10-02 18:1x r378 bm-c] 外科 temp-index 文件清点禁无参 ls-tree",
    "- [2026-10-02 19:0x r589 bm-a] 外科后 realign M 面分类 raw hash-object 误判坑",
    "- [2026-10-02 10:1x r569 bm-a] 让路手术窗三写者面序律",
    "- [2026-10-02 14:1x r578 bm-a] CAS update-ref 后 checkout 同名分支",
    "- [2026-10-02 16:3x r374 bm-c] pre-push 爪删除集×分叉基座假阳性面",
    "- [2026-10-02 18:0x r585 bm-b] 术后工作树陈旧面伪装成本轮新增行",
    "- [2026-10-02 18:0x r586 bm-b] 外科/FF 收口 commit 的 file-move 落盘滞后",
    "- [2026-10-02 19:4x r590 bm-a] 外科推送陈旧基 D 伪影判别律",
    "- [2026-10-02 21:2x r595 bm-b] FF/reset 对齐后 D 面未清零",
    "- [2026-10-02 23:0x r387 bm-c] GM CAS 直投×tick 本地 commit 双落竞态坑",
    "- [2026-10-02 23:2x r387 bm-c] r595 复犯+pre-push 爪 inbox 白名单互作用坑",
    "- [2026-10-03 05:5x r604 bm-b] r589 重落环分面恢复×载荷内配对移动自撞坑",
    "- [2026-10-03 05:0x r607 bm-a] S0 分面判别=属主门优先于 blob 新近度",
    "- [2026-10-03 07:0x r612 bm-a] reland 环他机属主面 origin-verbatim 恢复",
    "- [2026-10-03 08:3x r615 bm-a] 外科 hash-object 默认过 autocrlf check-in 滤镜坑",
    "- [2026-10-03 11:0x r411 bm-c] 已提交 blob 孤 CR 抑制转换面",
    "- [2026-10-03 22:3x r636 bm-b] pre-push 爪删除集两分法",
]

# pointer block inserted into pit-git.md header, right after the last existing
# "> 直写行" / "> 增量回扫行" header line (needle = the r420 direct-write line start)
PTR_NEEDLE = "> 直写行（r420 bm-c·post-split convention direct-write）：+1 条（拆件脚本断言层第三连假阳性"

PTR_BLOCK = (
    "> 子件分拆行（r439 bm-c·T-2026-10-02-144(c)·D-06 sub-split batch-1）：让路手术/closeout 扫树/外科推送（CAS 直投·temp-index·reland 环）/删除集自证与 pre-push 爪归属门/术后 realign M 面分类——外科族 40 条已整族 verbatim 迁出→**research/pit-git-surgery.md**（件内字节对账+md5 行·零丢失断言）；上述动作前改读该子件（本件保留 rebase/集成净路/staged 吞件/解析/包装器/D-19 水位各族+增量回扫 append 面）；余=sub-split batch-2+（rebase/净路族+解析族+staged 族裁定·D-06 全线收口窗 10-07）。"
)


def md5(b):
    return hashlib.md5(b).hexdigest()


def split_lines(raw: bytes):
    assert raw.count(b"\r\n") >= 10, "not a CRLF-face file"
    assert b"\n" not in raw.replace(b"\r\n", b""), "lone LF found"
    return raw.split(b"\r\n")


def main() -> int:
    raw = open(SRC, "rb").read()
    lines = split_lines(raw)
    before = len(raw)
    md5_before = md5(raw)

    # already-migrated law: anchors must be absent from sibling pit files
    for pf in SIBLINGS:
        p = os.path.join(ROOT, "research", pf)
        if os.path.exists(p):
            body = open(p, "rb").read()
            for a in ANCHORS:
                assert a.encode("utf-8") not in body, "anchor already in %s" % pf
    assert not os.path.exists(DST), "pit-git-surgery.md already exists"

    idx = {}
    for a in ANCHORS:
        hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(a)]
        assert len(hits) == 1, "anchor not-unique: %s -> %s" % (a[:40], hits)
        idx[a] = hits[0]
    moved_idx = sorted(idx.values())

    moved = [lines[i] for i in moved_idx]
    moved_sum = sum(len(l) + 2 for l in moved)          # CRLF terminators included
    core_lf = b"".join(l.replace(b"\r", b"") + b"\n" for l in moved)
    core_md5 = md5(core_lf)

    # new pit-git.md: drop moved lines, insert pointer block after PTR_NEEDLE line
    ptr_hits = [i for i, l in enumerate(lines)
               if l.decode("utf-8").startswith(PTR_NEEDLE)]
    assert len(ptr_hits) == 1, "header needle not unique: %s" % ptr_hits
    new_lines = [l for i, l in enumerate(lines) if i not in set(moved_idx)]
    j = new_lines.index(lines[ptr_hits[0]])            # same content, new position
    new_lines.insert(j + 1, PTR_BLOCK.encode("utf-8"))
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    ptr_len = len(PTR_BLOCK.encode("utf-8")) + 2
    assert after == before - moved_sum + ptr_len, "byte accounting mismatch"

    # compose pit-git-surgery.md (CRLF face, entries verbatim, original order)
    header = "\r\n".join([
        "# pit-git-surgery —— 让路/closeout/外科推送坑律正典（D-20261002-06 域分件·pit-git sub-split batch-1·外科族）",
        "",
        "> 来源：research/pit-git.md 整族 verbatim 迁出（2026-10-04 r439 bm-c·T-2026-10-02-144(c)·D-06 sub-split batch-1；机制=r335 机证律·拆件脚本机械迁移非手抄）。",
        "> 执法面：让路手术（yield/弃置/验属/让路重基带位）/closeout 扫树收口（他机属主/audit.machine 归属/单写者簿记）/外科推送（CAS 直投·temp-index·commit-tree·reland 环·撤-FF-重落）/删除集自证与 pre-push 爪归属门/术后 realign M 面分类与 D 伪影判别——上述动作前必读本件；母件 pit-git.md 保留 rebase/集成净路/staged 吞件/解析/包装器/D-19 水位各族。",
        "> 字节对账行（零丢失断言）：pit-git.md 迁出前 %dB（md5=%s·CRLF 工作树面）→迁出后 %dB（md5=%s·CRLF 工作树面·净变化=−%dB 迁出+%dB 指针行·blob=LF 规范化面）；移出 40 条·条目字节和（含 CRLF 行尾）=%dB==母件净删减字节·逐字节恒等零丢失；迁移核（LF blob 面）=%dB·md5=%s；本件由拆件脚本机械迁移非手抄（r335 机证律同源·r416 模板）。",
        "> 后续批次：sub-split batch-2+（rebase/集成净路族+解析/包装器族+staged 吞件族裁定·pit-git.md 增量回扫 append 面不变）——D-06 全线收口窗 2026-10-07。",
        "",
    ], ) % (before, md5_before, after, md5(new_raw), moved_sum, ptr_len,
            moved_sum, len(core_lf), core_md5)
    header_b = header.encode("utf-8")
    dst_raw = header_b + b"\r\n".join(moved) + b"\r\n"

    # ---- assertion battery before any write ----
    for l in moved:
        assert dst_raw.count(l) == 1, "moved line not exactly-once in pit-git-surgery"
        assert l.decode("utf-8")                                    # strict utf-8
    for a in ANCHORS:
        assert a.encode("utf-8") not in new_raw, "residue in pit-git: %s" % a[:40]
    for body in (new_raw, dst_raw):
        t = body.decode("utf-8")                                   # strict decode
        assert t.count("????") == 0, "mojibake gate: ???? run found"
        assert body.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR found"
    assert dst_raw.count(b"\r\n") == len(ANCHORS) + 6, "line count sanity"

    # ---- atomic writes (r614 law) ----
    for path, data in ((SRC, new_raw), (DST, dst_raw)):
        tmp = path + ".tmp_r439"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r439 bm-c", "ticket": "T-2026-10-02-144(c)",
        "batch": "D-06 pit-git sub-split batch-1 surgery family",
        "entries_moved": [a.split("]")[0] + "]" for a in ANCHORS],
        "n_moved": len(ANCHORS),
        "pit_git_before_B": before, "pit_git_before_md5": md5_before,
        "pit_git_after_B": after, "pit_git_after_md5": md5(new_raw),
        "moved_sum_CRLF_B": moved_sum, "pointer_line_B": ptr_len,
        "core_lf_B": len(core_lf), "core_lf_md5": core_md5,
        "pit_git_surgery_B": len(dst_raw), "pit_git_surgery_md5": md5(dst_raw),
        "verdict": "PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT PASS: pit-git %dB->%dB (-%dB moved +%dB ptr) | core LF %dB md5 %s | "
          "pit-git-surgery %dB md5 %s | entries=%d"
          % (before, after, moved_sum, ptr_len, len(core_lf), core_md5,
             len(dst_raw), md5(dst_raw), len(ANCHORS)))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    new_raw = open(SRC, "rb").read()
    dst_raw = open(DST, "rb").read()
    ok = []
    ok.append(("pit_git_after", len(new_raw) == r["pit_git_after_B"]
               and md5(new_raw) == r["pit_git_after_md5"]))
    ok.append(("pit_git_surgery", len(dst_raw) == r["pit_git_surgery_B"]
               and md5(dst_raw) == r["pit_git_surgery_md5"]))
    for a in ANCHORS:
        ok.append(("absent-in-pit-git " + a[3:26],
                   a.encode("utf-8") not in new_raw))
        ok.append(("exactly-once-in-surgery " + a[3:26],
                   sum(1 for l in dst_raw.split(b"\r\n")
                       if l.decode("utf-8").startswith(a)) == 1))
    t_s, t_d = new_raw.decode("utf-8"), dst_raw.decode("utf-8")
    ok.append(("strict-utf8+no-mojibake", "????" not in t_s and "????" not in t_d))
    ok.append(("pointer-line-present", PTR_BLOCK in t_s))
    ok.append(("surgery-line-count", dst_raw.count(b"\r\n") == r["n_moved"] + 6))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL",
                                              len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
