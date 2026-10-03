# -*- coding: utf-8 -*-
"""r441 bm-c: D-06 pit-git sub-split batch-2 -- NETPATH/PARSE/STAGED families.

pit-git.md -> research/pit-git-netpath.md (rebase/merge/FF 集成净路族 36 行)
           -> research/pit-git-parse.md   (解析/包装器/对账探针族 20 条)
           -> research/pit-git-staged.md  (staged 吞件与 commit 入场门族 3 条)

Mechanism = r335 machine-migration law (byte-level line surgery, no hand copying);
template = Tools/_r439bmc_pit_git_surgery_split.py (batch-1 canon, 40 entries).
Laws applied: r407 (CJK surgery via script not CLI replace), r614 (os.replace
atomic), r414 (PYTHONIOENCODING/-X utf8), already-migrated law (anchors absent
from sibling pit-*.md), r419 (CRLF triple-count invariance + same-table
anchoring), r420 (needle avoids self-produced furniture; full-line verbatim
criterion), assert-before-write battery (zero partial state).

TREASURE migration ritual (TREASURE_PROTECTION_LAW x D-20261002-06 adjudication,
O-2030 weld owner bm-c r432+): prescan rc3 fired on research/ blanket family
(recorded); zero-loss verbatim migration != deletion class; ritual =
registry 出入记录 pre-registration row (appended in-script AFTER all
assertions pass, BEFORE any file write) + full assertion battery + receipt
+ --verify re-check. pit-git.md stays registered (keeps D-19 watermark family
+ split-assertion increments + append face).

Fused-line adjudication: source line of r315 entry carries a second entry
(r505 bm-b push-dead) glued mid-line (historical union artifact, no own line);
it migrates WITH the r315 line to pit-git-netpath.md as one unit (both are
integration-family content); asserted pre+post.

Modes:
    python -X utf8 Tools/_r441bmc_pit_git_b2_split.py            # do the split
    python -X utf8 Tools/_r441bmc_pit_git_b2_split.py --verify   # independent re-check
"""
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "pit-git.md")
REGISTRY = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r441bmc_pit_git_b2_split.json")
SIBLINGS = ["pit-git-surgery.md", "pit-pool.md", "pit-engine.md",
            "pit-protocol.md", "pit-data.md", "pit-ps.md", "pit-encoding.md",
            "pit-spawn.md", "pit-tooling.md"]

FUSED = "- [2026-10-01 13:2x r505 bm-b] push-dead"

ANCHORS_NETPATH = [
    "- [2026-10-01 02:5x r498 bm-a] AA 双烧产品件信封分歧裁定律",
    "- [2026-10-01 r296 bm-c] 集成三重阻塞面定谳",
    "- [2026-10-01 r299 bm-c] rebase --autostash 长窗衰变坑",
    "- [2026-10-01 08:5x r507 bm-a] r305 假拒绝中段复发+cherry-pick 泛化净路",
    "- [2026-10-01 11:0x r501 bm-b] git 2.55 rebase --continue 拒绝面三变体净路汇总",
    "- [2026-10-01 r512 bm-a] 共享树退避轮正法",
    "- [2026-10-01 12:0x r312 bm-c] 会话 rebase 中途 daemon 抢道劫持三段净路",
    "- [2026-10-01 12:3x r314 bm-c] 三连猝死会话收编+CAS 整合法",
    "- [2026-10-01 13:13:06 r315 bm-c] peer 再归档重写面×追加块 union 断言坑",
    "- [2026-10-01 14:5x r519 bm-a] push 阻塞窗 daemon tick 积压净路",
    "- [2026-10-01 15:5x r510 bm-b] r220 禁 abort 律边界定谳",
    "- [2026-10-01 21:5x r523 bm-b] 活烧窗 pull --rebase 恒脏树+中断 pick 超集收编路由",
    "- [2026-10-01 23:2x r543 bm-a] rebase 中途 --quit 丢余 pick 坑",
    "- [2026-10-02 00:5x r341 bm-c] pull --rebase 多 refspec 撞「Cannot rebase onto multiple branches」坑",
    "- [2026-10-02 10:4x r568 bm-a] rebase --quit 后 HEAD 分离×reset --mixed 移分离 HEAD 非 main=假拒收矛盾表象",
    "- [2026-10-02 19:2x r589 bm-b] 推送窗连发 origin 前进×未推本地单件 commit 的纯 FF 处置律",
    "- [2026-10-02 20:0x r382 bm-c] appender 批量 commit×中窗 origin 前进=结构性双头分叉的 FF 诊断签名",
    "- [2026-10-02 20:5x r593 bm-a] S0 纯 FF 集成窗内 origin 二次前进坑",
    "- [2026-10-03 07:5x r613 bm-a] rebase --continue 假拒绝 daemon 活写变体x手工 commit 重复陷阱",
    "- [2026-10-03 09:1x r405 bm-c] rebase 冲突二次裁决双坑",
    "- [2026-10-03 11:2x r614 bm-b] rebase checkout 截断活写文件坑",
    "- [2026-10-03 14:0x r417 bm-c] diff3 手工解冲突后残留断言须行首匹配律",
    "- [2026-10-01 r294 bm-c] append-only 台账 union 合并去重域坑",
    "- [2026-10-01 r294 bm-c] 共享树 amend 撞劫坑",
    "- [2026-10-03 13:3x r624 bm-a] rebase --quit 后游离 HEAD 提交面坑",
    "- [2026-10-03 14:5x r627 bm-a] merge 向 stage 映射交换律",
    "- [2026-10-03 15:0x r619 bm-b] r543×r614 交互面实弹",
    "- [2026-10-03 15:1x r620 bm-b] churn-absorb commit 轮号前置读律",
    "- [2026-10-03 15:33x r621 bm-b] 多环陈旧tip合并收敛律",
    "- [2026-10-03 16:4x r624 bm-b] rebase 竞态第二形态坑",
    "- [2026-10-03 20:2x r427 bm-c] rebase --continue 净索引双拒坑",
    "- [2026-10-03 18:0x r423 bm-c] merge 窗三连坑",
    "- [2026-10-03 21:5x r643 bm-a] twin regen surface max-ts deep-probe TIE trap",
    "- [2026-10-03 22:3x r433 bm-c] rebase --continue 哑终端 EDITOR 坑+孪生再生面混侧违例自曝",
    "- [2026-10-03 23:5x r639 bm-b] push-race 双活 daemon 态 merge 整合尾步两坑",
    "- [2026-10-04 02:4x r440 bm-c] 预对齐窗内再staging 吞 checkout 净面坑",
]

ANCHORS_PARSE = [
    "- [2026-10-01 10:1x r500 bm-b] resolver 探针 bytes 未解析坑",
    "- [2026-10-01 12:5x r514 bm-a] merge_lane_views resolve/settle 缩进探针双坑",
    "- [2026-10-01 15:4x r320 bm-c] silent-git 包装器 -m 单引号消息 CRT 拆词坑",
    "- [2026-10-01 19:2x r330 bm-c] Invoke-SilentExe/silent-git ArgString=CRT 剥内层双引号坑",
    "- [2026-10-01 23:4x r339 bm-c] silent-git 包装器多命令 PS 批调用整批零输出 rc1 坑",
    "- [2026-10-02 09:2x r359 bm-c] commit 消息含括号/分号时 silent-git 内联 -m 引号面必炸",
    "- [2026-10-02 10:3x r568 bm-a] Python subprocess text=True stdin 转译坑",
    "- [2026-10-02 10:3x r569 bm-b] git diff --name-only HEAD origin/main 对称差集归属误读坑",
    "- [2026-10-02 11:4x r572 bm-b] git status porcelain 固定列解析勿先 strip 坑",
    "- [2026-10-02 13:4x r577 bm-a] md 孪生件冲突 ts 探针=内容 ts 非生成 ts 坑",
    "- [2026-10-02 18:3x r379 bm-c] 猝死会话正典件整文件行尾翻面伪影收养法+silent-git 包装器单串参数坑",
    "- [2026-10-02 01:3x r530 bm-b] python read_text/write_text 整文件 CRLF 翻面坑",
    "- [2026-10-02 14:5x r580 bm-a] PS 5.1 git 批量路径操作 argv 静默失效坑",
    "- [2026-10-02 16:2x r373 bm-c] autocrlf 双空间对账坑",
    "- [2026-10-02 16:5x r375 bm-c] PS 超长命令串解析层静默吞=整段零执行坑",
    "- [2026-10-02 19:1x r380 bm-c] python 解析 git status --porcelain 的 stdout.strip() 剥首行前导空格坑",
    "- [2026-10-02 23:5x r388 bm-c] porcelain D 行解析双列坑",
    "- [2026-10-03 01:5x r600 bm-a] CRLF-正典件 text-mode union 全行失配坑",
    "- [2026-10-03 05:5x r399 bm-c] 复用立法前旧 scratch 脚本=前法 bug 再进口坑",
    "- [2026-10-03 06:3x r400 bm-c] git show 缺失 path 的 stderr 双形态坑",
]

ANCHORS_STAGED = [
    "- [2026-09-30 23:5x r494 bm-a] 共享树 staged-index 吞件变体坑",
    "- [2026-09-30 r293 bm-c] 共享树同号票内容吞噬坑",
    "- [2026-10-03 11:3x r412 bm-c] pre-commit 冲突标记爪×解决器源码假阳性坑",
]

STAY = [
    "- [2026-09-30 r292 bm-c] D-19 决策水位哈希 PS 管道转码假漂移坑",
    "- [2026-09-30 22:4x r481 bm-b] bm-b 无集团树坑+D-19 新鲜读 temp partial clone 配方",
    "- [2026-10-02 19:0x r589 bm-a] D-19 水位键幻影值坑",
    "- [2026-10-03 07:4x r402 bm-c] 字节手术行界终结符双计×孤 CR 抑制 git 清滤=整文件 staged diff 双坑",
    "- [2026-10-03 14:2x r419 bm-c] 拆件脚本断言层假阳性两连坑",
    "- [2026-10-03 14:5x r420 bm-c] 拆件脚本断言层第三连假阳性",
]

DST_NETPATH = os.path.join(ROOT, "research", "pit-git-netpath.md")
DST_PARSE = os.path.join(ROOT, "research", "pit-git-parse.md")
DST_STAGED = os.path.join(ROOT, "research", "pit-git-staged.md")

PTR_NEEDLE = "> 子件分拆行（r439 bm-c"

PTR_BLOCK = (
    "> 子件分拆行（r441 bm-c·T-2026-10-02-144(c)·D-06 sub-split batch-2·迁移仪式=登记册出入记录预登记+零丢失断言）：rebase/merge/FF 集成净路族 36 行〔r315 行内熔合 r505 随行迁移〕verbatim 迁出→**research/pit-git-netpath.md**、解析/包装器/对账探针族 20 条 verbatim 迁出→**research/pit-git-parse.md**、staged 吞件与 commit 入场门族 3 条 verbatim 迁出→**research/pit-git-staged.md**（各件字节对账+md5 行·零丢失断言·receipt _r441bmc_pit_git_b2_split.json）；本件保留 D-19 水位族（r292/r481/r589-bma）+拆件断言层 increment（r402/r419/r420·final-sweep 裁定）+增量回扫 append 面；余=pit-data CRLF 裁定+流水下沉 final sweep（D-06 收口窗 10-07）。"
)

REG_ROW = (
    "- %s（bm-c r441·O-2030 焊面 r432+ 持有人·D-06 sub-split batch-2 迁移仪式）：prescan 实弹 rc3 命中（research/ 全族 fail-closed 面）——D-20261002-06 集团拆件令×本律 §2 门机械交集裁定=零丢失 verbatim 迁移非删除类（batch-1 r439 交付先例·全部字节留仓·三个新子件 pit-git-netpath/parse/staged.md 同入 research/ 保护族·母件 pit-git.md 仍在册：保留 D-19 水位族+拆件断言层 increment+增量回扫 append 面）；仪式四件=prescan rc3 留痕+本预登记行+拆件脚本断言电池（字节对账/md5/零丢失/CRLF 三计数恒等）+receipt results/_r441bmc_pit_git_b2_split.json 与 --verify 复验。"
)

FAMILY_META = [
    ("netpath", DST_NETPATH, ANCHORS_NETPATH,
     "# pit-git-netpath —— rebase/merge/FF 集成净路坑律正典（D-20261002-06 域分件·pit-git sub-split batch-2·集成净路族）",
     "> 执法面：pull --rebase/autostash 长窗/rebase 假拒绝净路（r305/r501/r507/r613/r427/r433）/--quit 与游离 HEAD/cherry-pick 收编与超集路由/纯 FF 处置与 origin 二段前进/merge 三方与 stage 映射/union 与去重域/冲突二次裁决与孪生再生面——S0 集成、推送撞车、断头收养、冲突解与 resolver 编写前必读本件；母件 pit-git.md 保留 D-19 水位族+断言层 increment。"),
    ("parse", DST_PARSE, ANCHORS_PARSE,
     "# pit-git-parse —— 解析/包装器/对账探针坑律正典（D-20261002-06 域分件·pit-git sub-split batch-2·解析族）",
     "> 执法面：git 固定列输出解析（porcelain/diff/ls-tree/stderr 双形态）×零窗包装器（silent-git/Invoke-SilentExe 引号与 CRT 面）×subprocess bytes 通道×autocrlf 双空间对账与 EOL 写入面×探针律（bytes 先解析/缩进探针/孪生 ts/复用前复审）——一切解析 git 输出、经包装器调用、做字节对账的脚本编写与复用前必读本件；母件 pit-git.md 保留 D-19 水位族+断言层 increment。"),
    ("staged", DST_STAGED, ANCHORS_STAGED,
     "# pit-git-staged —— staged 吞件与 commit 入场门坑律正典（D-20261002-06 域分件·pit-git sub-split batch-2·staged 族）",
     "> 执法面：共享树 staged-index 载运（轮 commit 前核 staged 集归属）/同号票内容吞噬（add 前核 type/created_by 归属）/pre-commit 冲突标记爪假阳性（解决器源码标记字面量拼接化+提交前自扫）——轮 commit 前 staged 归属核验、新票件 add 前、解决器/探针件入 git 前必读本件；母件 pit-git.md 保留 D-19 水位族+断言层 increment。"),
]


def md5(b):
    return hashlib.md5(b).hexdigest()


def split_lines(raw: bytes):
    assert raw.count(b"\r\n") >= 10, "not a CRLF-face file"
    assert b"\n" not in raw.replace(b"\r\n", b""), "lone LF found"
    return raw.split(b"\r\n")


def crlf_invariant(body: bytes, name: str):
    n_cr, n_crlf, n_lf = body.count(b"\r"), body.count(b"\r\n"), body.count(b"\n")
    assert n_cr == n_crlf == n_lf, "CRLF triple-count mismatch in %s (%d/%d/%d)" % (name, n_cr, n_crlf, n_lf)


def fuzzy_clock():
    t = time.strftime("%Y-%m-%d %H:%M")
    return t[:-1] + "x"


def main() -> int:
    raw = open(SRC, "rb").read()
    lines = split_lines(raw)
    before = len(raw)
    md5_before = md5(raw)

    # already-migrated law: anchors + fused needle absent from sibling pit files
    sib_raw = {}
    for pf in SIBLINGS:
        p = os.path.join(ROOT, "research", pf)
        if os.path.exists(p):
            sib_raw[pf] = open(p, "rb").read()
    all_needles = ANCHORS_NETPATH + ANCHORS_PARSE + ANCHORS_STAGED + [FUSED]
    for pf, body in sib_raw.items():
        for a in all_needles:
            assert a.encode("utf-8") not in body, "anchor already in %s: %s" % (pf, a[:40])
    for _, dst, _, _, _ in FAMILY_META:
        assert not os.path.exists(dst), "destination already exists: %s" % dst

    # anchor -> exactly-one source line (content-based same-table anchoring, r419)
    # FUSED is mid-line (no own line) -> containment branch below, not startswith
    anchor_line = {}
    for a in ANCHORS_NETPATH + ANCHORS_PARSE + ANCHORS_STAGED:
        hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(a)]
        assert len(hits) == 1, "anchor not-unique in pit-git: %s -> %s" % (a[:40], hits)
        anchor_line[a] = hits[0]

    # fused-line adjudication: FUSED lives inside the r315 physical line
    fused_host = anchor_line["- [2026-10-01 13:13:06 r315 bm-c] peer 再归档重写面×追加块 union 断言坑"]
    assert FUSED.encode("utf-8") in lines[fused_host], "fused r505 not on r315 line"
    assert sum(1 for l in lines if FUSED.encode("utf-8") in l) == 1, "fused r505 multi-line"

    # collect moved lines per family (original order preserved)
    fam_lines, fam_idx = {}, set()
    for fam, dst, anchors, _, _ in FAMILY_META:
        idxs = sorted(anchor_line[a] for a in anchors)
        assert len(idxs) == len(anchors)
        fam_lines[fam] = [lines[i] for i in idxs]
        fam_idx.update(idxs)
    assert len(fam_idx) == len(ANCHORS_NETPATH) + len(ANCHORS_PARSE) + len(ANCHORS_STAGED) == 59, \
        "moved set size mismatch: %d" % len(fam_idx)

    # stay-anchors must all be present (in-place canon guard)
    for s in STAY:
        hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(s)]
        assert len(hits) == 1, "stay anchor not-unique: %s -> %s" % (s[:40], hits)
        assert hits[0] not in fam_idx, "stay anchor scheduled to move: %s" % s[:40]

    moved_sum = sum(len(l) + 2 for fam in fam_lines for l in fam_lines[fam])
    fam_sum = {fam: sum(len(l) + 2 for l in fam_lines[fam])
               for fam, _, _, _, _ in FAMILY_META}
    fam_core_lf = {fam: b"".join(l.replace(b"\r", b"") + b"\n" for l in fam_lines[fam])
                   for fam, _, _, _, _ in FAMILY_META}

    # new pit-git.md: drop moved lines, insert pointer after batch-1 pointer line
    ptr_hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(PTR_NEEDLE)]
    assert len(ptr_hits) == 1, "batch-1 pointer needle not unique: %s" % ptr_hits
    new_lines = [l for i, l in enumerate(lines) if i not in fam_idx]
    j = new_lines.index(lines[ptr_hits[0]])
    new_lines.insert(j + 1, PTR_BLOCK.encode("utf-8"))
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    ptr_len = len(PTR_BLOCK.encode("utf-8")) + 2
    assert after == before - moved_sum + ptr_len, "byte accounting mismatch"

    # compose destination files (CRLF face, entries verbatim, original order)
    dst_raws, dst_meta = {}, {}
    for fam, dst, anchors, title, scope in FAMILY_META:
        n = len(anchors)
        header = "\r\n".join([
            title,
            "",
            "> 来源：research/pit-git.md 整族 verbatim 迁出（2026-10-04 r441 bm-c·T-2026-10-02-144(c)·D-06 sub-split batch-2；机制=r335 机证律·拆件脚本机械迁移非手抄·r416/r439 模板·宝藏迁移仪式=登记册出入记录预登记行）。",
            scope,
            "> 字节对账行（零丢失断言）：本件 %d 条（含熔合随行注记时按物理行计）·条目字节和（含 CRLF 行尾）=%dB==母件净删减分摊；迁移核（LF blob 面）=%dB·md5=%s；母件迁出前 %dB（md5=%s）→迁出后 %dB（净变化=−%dB 迁出+%dB 指针行）；本件由拆件脚本机械迁移非手抄。" % (n, fam_sum[fam], len(fam_core_lf[fam]), md5(fam_core_lf[fam]), before, md5_before, after, moved_sum, ptr_len),
            "> 后续批次：增量回扫 append 面仍在母件 pit-git.md（post-split convention）；本件为 batch-2 终态子件——D-06 收口窗 2026-10-07。",
            "",
        ])
        dst_raw = header.encode("utf-8") + b"\r\n".join(fam_lines[fam]) + b"\r\n"
        dst_raws[dst] = dst_raw
        dst_meta[fam] = {"n": n, "sum_crlf_B": fam_sum[fam],
                         "core_lf_B": len(fam_core_lf[fam]),
                         "core_lf_md5": md5(fam_core_lf[fam]),
                         "file_B": len(dst_raw), "file_md5": md5(dst_raw)}

    # ---- assertion battery (r419/r420 laws) before ANY write ----
    for l in (new_raw, dst_raws[DST_NETPATH], dst_raws[DST_PARSE], dst_raws[DST_STAGED]):
        t = l.decode("utf-8")
        assert t.count("????") == 0, "mojibake gate"
    crlf_invariant(new_raw, "pit-git")
    for dst, dr in dst_raws.items():
        crlf_invariant(dr, os.path.basename(dst))
        assert dr.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR in dst"
    for fam, dst, anchors, _, _ in FAMILY_META:
        dr = dst_raws[dst]
        n = len(anchors)
        assert dr.count(b"\r\n") == n + 6, "line count sanity %s" % fam
        for a in anchors:
            assert a.encode("utf-8") not in new_raw, "residue in pit-git: %s" % a[:40]
            hits = sum(1 for l in dr.split(b"\r\n") if l.decode("utf-8").startswith(a))
            assert hits == 1, "not exactly-once in %s: %s" % (fam, a[:40])
    for s in STAY:
        assert s.encode("utf-8") in new_raw, "stay entry lost: %s" % s[:40]
    for l in fam_lines["netpath"]:
        assert sum(1 for x in dst_raws[DST_NETPATH].split(b"\r\n") if x == l) == 1, \
            "verbatim full-line criterion fail (netpath)"
    assert FUSED.encode("utf-8") not in new_raw, "fused r505 residue in pit-git"
    assert FUSED.encode("utf-8") in dst_raws[DST_NETPATH], "fused r505 not in netpath"
    fused_pair = [l for l in dst_raws[DST_NETPATH].split(b"\r\n")
                  if FUSED.encode("utf-8") in l]
    assert len(fused_pair) == 1 and fused_pair[0].startswith(
        "- [2026-10-01 13:13:06 r315 bm-c]".encode("utf-8")), "fused pair broken"
    assert PTR_BLOCK in new_raw.decode("utf-8"), "pointer line missing"

    # ---- treasure ritual step zero: registry pre-registration row ----
    reg_raw = open(REGISTRY, "rb").read()
    reg_is_crlf = reg_raw.count(b"\r\n") >= 10 and b"\n" not in reg_raw.replace(b"\r\n", b"")
    row = (REG_ROW % fuzzy_clock()).encode("utf-8")
    assert row not in reg_raw, "registry row already appended (rerun?)"
    eol = b"\r\n" if reg_is_crlf else b"\n"
    reg_new = reg_raw + (b"" if reg_raw.endswith(eol) else eol) + row + eol

    # ---- atomic writes (r614 law) ----
    for path, data in ((DST_NETPATH, dst_raws[DST_NETPATH]),
                       (DST_PARSE, dst_raws[DST_PARSE]),
                       (DST_STAGED, dst_raws[DST_STAGED]),
                       (SRC, new_raw),
                       (REGISTRY, reg_new)):
        tmp = path + ".tmp_r441"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r441 bm-c", "ticket": "T-2026-10-02-144(c)",
        "batch": "D-06 pit-git sub-split batch-2 netpath/parse/staged",
        "prescan_rc3_recorded": "research/ blanket family hit; weld-owner migration ritual",
        "registry_row_clock": fuzzy_clock(),
        "families": dst_meta,
        "fused_entry": {"needle": FUSED, "host": "r315 line", "unit_move": "netpath"},
        "entries_moved_total": 59, "entries_stay": [s[:44] for s in STAY],
        "pit_git_before_B": before, "pit_git_before_md5": md5_before,
        "pit_git_after_B": after, "pit_git_after_md5": md5(new_raw),
        "moved_sum_CRLF_B": moved_sum, "pointer_line_B": ptr_len,
        "verdict": "PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT PASS: pit-git %dB->%dB (-%dB moved +%dB ptr) | netpath %d/%dB | parse %d/%dB | staged %d/%dB | registry row appended"
          % (before, after, moved_sum, ptr_len,
             dst_meta["netpath"]["n"], dst_meta["netpath"]["file_B"],
             dst_meta["parse"]["n"], dst_meta["parse"]["file_B"],
             dst_meta["staged"]["n"], dst_meta["staged"]["file_B"]))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    new_raw = open(SRC, "rb").read()
    reg_raw = open(REGISTRY, "rb").read()
    dst_bodies = {dst: open(dst, "rb").read() for _, dst, _, _, _ in FAMILY_META}
    ok = []
    ok.append(("pit_git_after", len(new_raw) == r["pit_git_after_B"]
               and md5(new_raw) == r["pit_git_after_md5"]))
    for fam, dst, _, _, _ in FAMILY_META:
        m = r["families"][fam]
        ok.append((fam + "_file", len(dst_bodies[dst]) == m["file_B"]
                   and md5(dst_bodies[dst]) == m["file_md5"]))
        ok.append((fam + "_crlf_count", dst_bodies[dst].count(b"\r\n") == m["n"] + 6))
    for fam, dst, anchors, _, _ in FAMILY_META:
        for a in anchors:
            ok.append(("absent-in-pit-git " + a[3:26],
                       a.encode("utf-8") not in new_raw))
            ok.append(("once-in-" + fam + " " + a[3:26],
                       sum(1 for l in dst_bodies[dst].split(b"\r\n")
                           if l.decode("utf-8").startswith(a)) == 1))
    for s in STAY:
        ok.append(("stay-in-pit-git " + s[3:26],
                   sum(1 for l in new_raw.split(b"\r\n")
                       if l.decode("utf-8").startswith(s)) == 1))
    for body, name in ((new_raw, "pit-git"),) + tuple(
            (dst_bodies[dst], os.path.basename(dst)) for _, dst, _, _, _ in FAMILY_META):
        ok.append((name + " crlf-invariant",
                   body.count(b"\r") == body.count(b"\r\n") == body.count(b"\n")))
    ok.append(("fused-absent-in-pit-git", FUSED.encode("utf-8") not in new_raw))
    ok.append(("fused-in-netpath", FUSED.encode("utf-8") in dst_bodies[DST_NETPATH]))
    ok.append(("pointer-line-present", PTR_BLOCK in new_raw.decode("utf-8")))
    ok.append(("registry-row-present", (REG_ROW % r["registry_row_clock"]).encode("utf-8") in reg_raw))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL",
                                             len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
