# -*- coding: utf-8 -*-
"""r670 bm-c: D-06 pit-lineage relief sub-split + main increment batch.

Trigger: main CODELY.md MEASURED 30,527B (193B headroom, r669 S4 pit appended)
+ r653 close-size entry (676B) pending pit-lineage.md relief per r669
next-pointer candidate; pit-lineage.md MEASURED 30,552B (168B headroom, full).
All sizes derived at use time (r653 receipt-vs-measured law).

Phase A (split, r441/r669 ritual): receipt-reviewable family 12 entries
(r554/r555-ephemeral/r559/r560/r569/r570/r578/r583/r587/r629/r637/r646)
verbatim OUT -> research/pit-lineage-receipt.md (new sub-file, research/
protection family). Mother keeps lineage-copy core (full-command-diff /
needle / strip / porcelain / UU-probe) + close/bookkeeping script family +
fact-extractor leg-anchor family + increment append face.
Phase B (increment, r668/r669 ritual): main r653 entry (close size claim =
stale prior receipt assumption) 676B OUT -> receipt sub-file (r646 same
family homecoming); main r669 entry (split-script list-composition =
line-anchor-gate blind spot, construct-vs-equation dual-derive identity
gate) 803B OUT -> pit-git.md (split-script assertion-layer family, r651
precedent) + in-file direct-write accounting line. Main gets the r670
increment pointer row.

Laws: r335 machine-migration (byte surgery, no hand copy), r614 atomic
os.replace, r402 CRLF triple-count + preserved-face identity, r419/r420
assertion battery + needle-avoid-furniture, r441 treasure migration ritual
(prescan rc3 + registry pre-registration row + receipt + --verify), r669
construct-vs-equation dual-derive identity gate (this batch's battery is
its first operative implementation), r583 facts-driven never hand-typed,
r653 measure-at-use-time, r668/pit hard-gate sizes len()-derived.

Modes:
    python -X utf8 Tools/_r670bmc_lineage_receipt_split.py            # do batch
    python -X utf8 Tools/_r670bmc_lineage_receipt_split.py --verify   # re-check
"""
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
MOTHER = os.path.join(ROOT, "research", "pit-lineage.md")
SUB = os.path.join(ROOT, "research", "pit-lineage-receipt.md")
PITGIT = os.path.join(ROOT, "research", "pit-git.md")
REGISTRY = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r670bmc_lineage_receipt_split.json")
CAP = 30720

MOVE_NEEDLES = [
    "[2026-10-05 15:5x r554 bm-c] **lineage 复制替换链 double-apply",
    "[2026-10-05 16:2x r555 bm-c] **lineage 收据引用 ephemeral 件",
    "[2026-10-05 17:4x r559 bm-c] **S6 链血统文件三连窗内自灭坑",
    "[2026-10-05 17:5x r560 bm-c] **双 scratch 路径分叉误诊勘误",
    "[2026-10-05 20:0x r569 bm-c] **S0 churn-absorb 后 pull --rebase 改写 sha",
    "[2026-10-05 20:2x r570 bm-c] **链血统复制 needle 跨物理换行",
    "[2026-10-05 23:1x r578 bm-c] **会话 shell glob 工具大目录零命中",
    "[2026-10-06 00:5x r583 bm-c] **bookkeeping 硬编码水位字面量手抄眼跳坑",
    "[2026-10-06 02:3x r587 bm-c] **S0.5 facts 收据 scratch",
    "[2026-10-06 16:5x r629 bm-c] **lineage 复制器 SCRQ 同根漂移",
    "[2026-10-06 19:2x r637 bm-c] **预派生血统件数据值锚滞代坑",
    "[2026-10-07 01:5x r646 bm-c] **D-06 尺寸收据量面",
]
STAY_LINEAGE_NEEDLES = [
    "[2026-10-04 23:5x r503 bm-c]",
    "[2026-10-05 06:1x r517 bm-c]",
    "[2026-10-05 10:5x r531 bm-c]",
    "[2026-10-05 11:0x r532 bm-c]",
    "[2026-10-05 11:2x r533 bm-c]",
    "[2026-10-05 14:10x r547 bm-c]",
    "[2026-10-05 14:3x r548 bm-c]",
    "[2026-10-05 14:5x r549 bm-c] **S6 链 legdiff 血统断言层阈值假阳性",
    "[2026-10-05 14:5x r549 bm-c] **close 面清单消费三连坑",
    "[2026-10-05 15:4x r553 bm-c]",
    "[2026-10-05 16:2x r555 bm-c] **血统 git() helper",
    "[2026-10-05 17:1x r558 bm-c]",
    "[2026-10-05 18:1x r561 bm-c]",
    "[2026-10-05 18:2x r739 bm-b]",
    "[2026-10-05 18:3x r563 bm-c]",
    "[2026-10-05 19:5x r567 bm-c]",
    "[2026-10-05 22:4x r576 bm-c]",
]
R653_LINE_NEEDLE = "- [2026-10-07 04:3x r653 bm-c] **close 尺寸声明"
R669_LINE_NEEDLE = "- [2026-10-07 10:4x r669 bm-c] **拆件脚本列表构成错误"
R668_LINE_NEEDLE = "- [2026-10-07 10:2x r668 bm-c]"
MAIN_STAY_NEEDLES = [R668_LINE_NEEDLE, "域指针·r654 bm-c 增量回扫批", "域指针·r667 bm-c", "[2026-10-07 10:2x r668 bm-c] **未来日历事实"]


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def md5(b):
    return hashlib.md5(b).hexdigest()


def crlf_invariant(body, name):
    n_cr, n_crlf, n_lf = body.count(b"\r"), body.count(b"\r\n"), body.count(b"\n")
    assert n_cr == n_crlf == n_lf, "CRLF triple-count mismatch %s (%d/%d/%d)" % (name, n_cr, n_crlf, n_lf)


def fuzzy_clock():
    t = time.strftime("%Y-%m-%d %H:%M")
    return t[:-1] + "x"


def sibling_bodies(exclude):
    out = {}
    rd = os.path.join(ROOT, "research")
    for f in sorted(os.listdir(rd)):
        if f.startswith("pit-") and f.endswith(".md"):
            p = os.path.join(rd, f)
            if os.path.abspath(p) not in [os.path.abspath(x) for x in exclude]:
                out[f] = open(p, "rb").read()
    return out


PTR_ROW = (
    "> 子件分拆行（r670 bm-c·D-20261002-06 域件 ≤30KB 判据腿·触发=主件 r653 close-size 坑 676B 迁入需求+本件 30,552B 满员待让位〔r669 next 指针窗〕·迁移仪式 r441/r669 同款）："
    "收据可复核律族 12 条（r554/r555/r559/r560/r569/r570/r578/r583/r587/r629/r637/r646）verbatim 迁出→**research/pit-lineage-receipt.md**"
    "（件内字节对账+md5 行·零丢失断言·receipt results/_r670bmc_lineage_receipt_split.json）；"
    "本件保留链/工具血统复制核心族（命令全串 diff/needle/strip/porcelain/UU 探针）+close/簿记脚本血统族（marker 自洽/尾行/面清单）+事实提取器腿锚族+增量回扫 append 面；"
    "收据书写/水位值锚/双镜像/尺寸声明核验动作前改读 pit-lineage-receipt.md。"
)

SUB_TITLE = (
    "# pit-lineage-receipt —— 收据可复核/水位值锚/双镜像/尺寸收据面坑律正典"
    "（D-20261002-06 域分件·pit-lineage sub-split·2026-10-07 r670 bm-c 新立）"
)
SUB_SRC = (
    "> 来源：research/pit-lineage.md 收据可复核律族 12 条 verbatim 迁出+CODELY.md 主件 r653 close-size 坑同窗迁入（2026-10-07 r670 bm-c·让位窗 sub-split；机制=r335 机证律·拆件脚本机械迁移非手抄·r441/r669 模板·宝藏迁移仪式=登记册出入记录预登记行）。"
)
SUB_SCOPE = (
    "> 执法面：收据书写与核验（ephemeral 引用/幻影 sha/自引用锚/收据禁预写模板）·水位值锚（facts 驱动/形态门/值锚滞代）·双镜像与存留（SCRQ 同根/链件存留/双根在位性）·尺寸收据面（量面≠提交面/close 陈旧收据假设 gate-pin 实测）——一切收据/水位/双镜像/尺寸声明书写与核验、legdiff OLD 锚定性、在位性定性前必读本件；母件 pit-lineage.md 保留链/工具血统复制核心+close/簿记脚本血统+事实提取器腿锚+append 面。"
)
SUB_POST = "> 后续批次：增量回扫 append 面仍在母件 pit-lineage.md（post-split convention·r441）；本件为 sub-split 终态子件——再超线时由下一让位窗处置。"

MAIN_PTR_ROW = (
    "- 域指针·r670 bm-c 增量批（D-20261002-06 主件 ≤30KB 判据腿·2026-10-07 r670 bm-c·触发=主件实测 30,527B 余量 193B 红线〔r669 S4 坑 append 后〕·迁移仪式 r441/r669 同款·prescan rc3 留痕）："
    "主件 2 行/2 坑 verbatim 迁出——r653 close 尺寸声明陈旧收据坑（677B 实测·声明 676B 陈旧收据假设又一活例·r653 律当场再现）→pit-lineage-receipt.md〔收据可复核族·r646 同族变体·与 r646 尺寸收据面同窗归位〕"
    "+r669 拆件脚本列表构成错误双 derive 恒等门坑（802B 实测·声明 803B 陈旧）→pit-git.md〔拆件脚本断言层族·r651 前例同域〕；"
    "pit-lineage.md 同窗让位 sub-split（收据可复核族 12 条→pit-lineage-receipt.md 新子件）——"
    "逐条字节+sha16 对账=receipt results/_r670bmc_lineage_receipt_split.json"
    "（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等式+构造式×方程式双 derive 恒等门+主件 ≤30KB+全域件 ≤30KB·prescan rc3 留痕）；新坑律仍先入本件后回扫。"
)


def build_sub_accounting(n_moved, moved_sum, moved_core_lf, mother_before, mother_after, ptr_len, r653_len):
    return (
        "> 字节对账行（零丢失断言）：本件 %d 条母件迁出·条目字节和（含 CRLF 行尾）=%dB==母件净删减分摊；迁移核（LF blob 面）=%dB·md5=%s；母件迁出前 %dB→迁出后 %dB（净变化=−%dB 迁出+%dB 指针行）；主件 r653 close-size 坑 %dB 同窗迁入（字节恒等 verbatim·来源 CODELY.md）；本件由拆件脚本机械迁移非手抄·receipt results/_r670bmc_lineage_receipt_split.json。"
        % (n_moved, moved_sum, len(moved_core_lf), md5(moved_core_lf), mother_before, mother_after, moved_sum, ptr_len, r653_len)
    )


PITGIT_ACCT_PREFIX = "> 直写行（r670 bm-c·post-split convention direct-write）：+1 条（r669 拆件脚本列表构成错误=逐行锚点门盲区·构造式×方程式双 derive 恒等门正法）——本件拆件脚本断言层族（r651 前例同域），本轮 r670 拆件脚本电池即按该门实装首验"


def build_pitgit_acct(r669_len):
    return (
        PITGIT_ACCT_PREFIX + "·来源=CODELY.md 主件 %dB verbatim 迁出·追加核 %dB·件尾整行追加·件内对账行为准。"
        % (r669_len, r669_len)
    )


REG_ROW = (
    "- %s bm-c r670 D-06 lineage 让位 sub-split+主件增量批迁移仪式（触发=主件实测 30,527B 余量 193B 红线+pit-lineage.md 30,552B 满员·r669 next 指针窗）："
    "收据可复核律族 12 条 verbatim 零丢失迁出→research/pit-lineage-receipt.md（新子件同入 research/ 保护族）"
    "+主件 r653/r669 两坑 verbatim 迁出（→receipt 子件/pit-git.md 拆件断言层族）+pit-lineage.md 指针行；"
    "prescan 实弹 rc3 命中四路径留痕（CODELY.md/pit-lineage.md/pit-lineage-receipt.md/pit-git.md）——D-20261002-06 集团拆件令×TREASURE_PROTECTION_LAW §2 门机械交集裁定=零丢失 verbatim 迁移非删除类（r441/r651/r654/r662/r669 交付先例·全部字节留仓·登记册属主行不动）；"
    "仪式四件=prescan rc3 留痕+本预登记行+断言电池（needle count==1/字节对账/md5/CRLF 三计数/保留面恒等/构造式×方程式双 derive 恒等门/全件 ≤30,720B·尺寸当场 len() derive 禁手算）+receipt results/_r670bmc_lineage_receipt_split.json 与 --verify 复验。"
)


def main():
    main_raw = open(MAIN, "rb").read()
    mom_raw = open(MOTHER, "rb").read()
    pitgit_raw = open(PITGIT, "rb").read()
    main_before, mom_before, pitgit_before = len(main_raw), len(mom_raw), len(pitgit_raw)
    assert main_before == 30527, "main measured-size gate: %d (derive at use time, r653)" % main_before
    assert mom_before == 30552, "mother measured-size gate: %d" % mom_before
    assert not os.path.exists(SUB), "sub-file already exists (rerun?)"

    # ---------- Phase A: split ----------
    crlf_invariant(mom_raw, "mother")
    lines = mom_raw.split(b"\r\n")
    assert lines[-1] == b"", "trailing element gate"
    real = lines[:-1]
    header_n = 6
    assert real[0].startswith(b"# pit-lineage"), "header title gate"
    assert real[1] == b"", "header blank gate"
    assert real[2].startswith(b"> ") and real[3].startswith(b"> "), "scope rows gate"
    assert real[4].startswith(b"> "), "scene row gate"
    assert real[5] == b"", "header blank2 gate"
    entries = real[header_n:]
    assert entries[0].startswith(b"- [2026-10-04 23:5x r503"), "first entry gate"

    move_idx = {}
    for nd in MOVE_NEEDLES:
        assert mom_raw.count(nd.encode("utf-8")) == 1, "raw needle count!=1: %s" % nd
        hits = [i for i, l in enumerate(entries) if nd.encode("utf-8") in l]
        assert len(hits) == 1, "needle line!=1: %s -> %s" % (nd, hits)
        move_idx[nd] = hits[0]
    assert len(set(move_idx.values())) == 12, "move index overlap"

    stay_idx = {}
    for nd in STAY_LINEAGE_NEEDLES:
        hits = [i for i, l in enumerate(entries) if nd.encode("utf-8") in l]
        assert len(hits) == 1, "stay anchor not unique: %s -> %s" % (nd, hits)
        assert hits[0] not in move_idx.values(), "stay anchor scheduled to move: %s" % nd
        stay_idx[nd] = hits[0]
    assert len(set(stay_idx.values())) == 17, "stay overlap"

    # coverage gate: every entry line is either move, stay or blank separator
    blank_rows = [i for i, l in enumerate(entries) if l.strip() == b""]
    covered = set(move_idx.values()) | set(stay_idx.values()) | set(blank_rows)
    assert covered == set(range(len(entries))), "entry coverage gate: missing %s" % (
        sorted(set(range(len(entries))) - covered))
    n_blank = len(blank_rows)
    assert n_blank >= 0, "blank count sanity"

    # already-migrated law: needles absent from sibling pit files
    for fname, body in sibling_bodies([MOTHER, SUB]).items():
        for nd in MOVE_NEEDLES + [R653_LINE_NEEDLE, R669_LINE_NEEDLE]:
            assert nd.encode("utf-8") not in body, "needle already in sibling %s: %s" % (fname, nd)

    moved_lines = [entries[i] for i in sorted(move_idx.values())]
    moved_sum = sum(len(l) + 2 for l in moved_lines)
    moved_core_lf = b"".join(l.replace(b"\r", b"") + b"\n" for l in moved_lines)

    ptr_b = PTR_ROW.encode("utf-8")
    ptr_len = len(ptr_b) + 2
    survivors = [l for i, l in enumerate(entries) if i not in move_idx.values()]
    assert len(survivors) == len(entries) - 12, "survivor count gate: %d" % len(survivors)
    new_real = real[:header_n] + [ptr_b] + survivors
    mom_new = b"\r\n".join(new_real + [b""])
    mom_after = len(mom_new)
    # construct-vs-equation dual-derive identity gate (r669 S4 law, first operative use)
    eq_derive = mom_before - moved_sum + ptr_len
    assert mom_after == eq_derive, "mother construct-vs-equation identity: %d != %d" % (mom_after, eq_derive)
    assert mom_after <= CAP, "mother cap gate A: %d" % mom_after
    # preserved-face identity: entry region after pointer row == survivors verbatim order
    assert new_real[header_n + 1:] == survivors, "mother preserved-face identity (region slice)"

    # ---------- Phase B-1: main r653/r669 OUT ----------
    crlf_invariant(main_raw, "main")
    mlines = main_raw.split(b"\n")
    assert mlines[-1] == b"", "main trailing gate"
    mbody = mlines[:-1]
    hits653 = [i for i, l in enumerate(mbody) if R653_LINE_NEEDLE.encode("utf-8") in l]
    hits669 = [i for i, l in enumerate(mbody) if R669_LINE_NEEDLE.encode("utf-8") in l]
    hits668 = [i for i, l in enumerate(mbody) if R668_LINE_NEEDLE.encode("utf-8") in l]
    assert len(hits653) == 1 and len(hits669) == 1 and len(hits668) == 1, "main needle count gates: %s %s %s" % (hits653, hits669, hits668)
    i653, i669, i668 = hits653[0], hits669[0], hits668[0]
    assert i653 < i668 < i669, "main row order gate"
    r653_line = mbody[i653]
    r669_line = mbody[i669]
    assert r653_line.endswith(b"\r") and r669_line.endswith(b"\r"), "CR-tail gates"
    assert r653_line.startswith(b"- [") and r669_line.startswith(b"- ["), "bullet gates"
    assert len(r653_line) == 677, "r653 byte gate (measured at use, CR-tail face): %d" % len(r653_line)
    assert len(r669_line) == 802, "r669 byte gate (measured at use, CR-tail face): %d" % len(r669_line)
    for nd in MAIN_STAY_NEEDLES:
        assert main_raw.count(nd.encode("utf-8")) >= 1, "main stay anchor gate: %s" % nd

    mbody2 = [l for i, l in enumerate(mbody) if i not in (i653, i669)]
    j668 = [j for j, l in enumerate(mbody2) if R668_LINE_NEEDLE.encode("utf-8") in l]
    assert len(j668) == 1, "r668 relocate gate"
    ptr670_b = MAIN_PTR_ROW.encode("utf-8") + b"\r"
    mbody3 = mbody2[:j668[0] + 1] + [ptr670_b] + mbody2[j668[0] + 1:]
    main_new = b"\n".join(mbody3) + b"\n"
    main_after = len(main_new)
    eq_main = main_before - (len(r653_line) + 1) - (len(r669_line) + 1) + (len(ptr670_b) + 1)
    assert main_after == eq_main, "main construct-vs-equation identity: %d != %d" % (main_after, eq_main)
    assert main_after <= CAP, "main cap gate: %d" % main_after

    # ---------- Phase B-2: receipt sub-file compose ----------
    # r653_line comes from LF-split (CR kept in line tail); strip the CR for the
    # CRLF-join composition to avoid a lone/double-CR seam (r553 EOL seam family)
    assert r653_line.endswith(b"\r"), "r653 CR-tail pre-strip gate"
    r653_line_sub = r653_line[:-1]
    assert r653_line_sub.count(b"\r") == 0, "r653 interior CR gate"
    sub_acct = build_sub_accounting(12, moved_sum, moved_core_lf, mom_before, mom_after, ptr_len, len(r653_line) + 1)
    hdr = [s.encode("utf-8") for s in (SUB_TITLE, "", SUB_SRC, SUB_SCOPE, sub_acct, SUB_POST, "")]
    sub_new = b"\r\n".join(hdr + moved_lines + [r653_line_sub] + [b""])

    # ---------- Phase B-3: pit-git.md append ----------
    crlf_invariant(pitgit_raw, "pit-git")
    pg_lines = pitgit_raw.split(b"\r\n")
    assert pg_lines[-1] == b"", "pit-git trailing gate"
    pitgit_acct = build_pitgit_acct(len(r669_line) + 1).encode("utf-8") + b"\r"
    pitgit_new = pitgit_raw + r669_line + b"\n" + pitgit_acct + b"\n"
    pitgit_after = len(pitgit_new)
    eq_pg = pitgit_before + (len(r669_line) + 1) + (len(pitgit_acct) + 1)
    assert pitgit_after == eq_pg, "pit-git construct-vs-equation identity: %d != %d" % (pitgit_after, eq_pg)
    assert pitgit_after <= CAP, "pit-git cap gate: %d" % pitgit_after

    # ---------- battery ----------
    for nd in MOVE_NEEDLES:
        assert nd.encode("utf-8") not in mom_new, "residue in mother: %s" % nd
        assert sub_new.count(nd.encode("utf-8")) == 1, "not once in sub: %s" % nd
    for nd in STAY_LINEAGE_NEEDLES:
        assert mom_new.count(nd.encode("utf-8")) == 1, "stay lost from mother: %s" % nd
    assert R653_LINE_NEEDLE.encode("utf-8") not in main_new, "r653 residue in main"
    assert R669_LINE_NEEDLE.encode("utf-8") not in main_new, "r669 residue in main"
    assert sub_new.count(R653_LINE_NEEDLE.encode("utf-8")) == 1, "r653 once-in-sub gate"
    assert pitgit_new.count(R669_LINE_NEEDLE.encode("utf-8")) == 1, "r669 once-in-pitgit gate"
    assert r653_line in sub_new, "r653 verbatim-in-target gate"
    assert r669_line in pitgit_new, "r669 verbatim-in-target gate"
    assert ptr_b in mom_new, "pointer row missing in mother"
    assert ptr670_b in main_new, "r670 pointer row missing in main"
    # preserved-face identity: mother region slice done above; main region slice here
    assert mbody3[:j668[0] + 1] + mbody3[j668[0] + 2:] == mbody2, "main preserved-face identity (region slice)"
    for name, body in (("mother-new", mom_new), ("sub", sub_new), ("main-new", main_new), ("pit-git-new", pitgit_new)):
        crlf_invariant(body, name)
        body.decode("utf-8")
    assert sub_new.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR in sub"
    # whole-domain cap gate: every pit-*.md <= 30,720B measured now (len() derive);
    # in-flight faces (MOTHER/SUB/MAIN/PITGIT) use their in-memory post-op bytes
    mem_faces = {"pit-lineage.md": mom_new, "pit-lineage-receipt.md": sub_new,
                 "pit-git.md": pitgit_new}
    rd = os.path.join(ROOT, "research")
    for f in sorted(os.listdir(rd)):
        if f.startswith("pit-") and f.endswith(".md"):
            sz = len(mem_faces[f]) if f in mem_faces else len(open(os.path.join(rd, f), "rb").read())
            assert sz <= CAP, "domain cap gate: %s %dB" % (f, sz)
    assert len(main_new) <= CAP, "main post-op cap gate (len() derive)"

    # ---------- registry pre-registration row ----------
    reg_raw = open(REGISTRY, "rb").read()
    row_clock = fuzzy_clock()
    row = (REG_ROW % row_clock).encode("utf-8")
    assert row not in reg_raw, "registry row already appended (rerun?)"
    eol = b"\r\n" if reg_raw.count(b"\r\n") >= 10 else b"\n"
    reg_new = reg_raw + (b"" if reg_raw.endswith(eol) else eol) + row + eol
    if eol == b"\r\n":
        crlf_invariant(reg_new, "registry")
    reg_new.decode("utf-8")

    # ---------- atomic writes (r614) ----------
    for path, data in ((SUB, sub_new), (MOTHER, mom_new), (MAIN, main_new), (PITGIT, pitgit_new), (REGISTRY, reg_new)):
        tmp = path + ".tmp_r670"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r670 bm-c",
        "batch": "D-06 pit-lineage relief sub-split + main increment (r653+r669 out)",
        "prescan_rc": 3,
        "prescan_note": "registry hits CODELY.md + research/pit-lineage.md + research/pit-lineage-receipt.md + research/pit-git.md; r441/r651/r654/r662/r669 operative precedent: verbatim zero-loss relocation, not deletion; registry owner rows untouched; all sizes derived at use time (r653)",
        "trigger": "main measured 30,527B (193B headroom) + pit-lineage.md measured 30,552B full; r669 next-pointer candidate window",
        "phase_a_split": {
            "moved_entries": 12,
            "moved_needles": MOVE_NEEDLES,
            "moved_sum_crlf_B": moved_sum,
            "moved_core_lf_md5": md5(moved_core_lf),
            "sub_file": "research/pit-lineage-receipt.md",
            "sub_B": len(sub_new),
            "sub_md5": md5(sub_new),
            "mother_before_B": mom_before,
            "mother_after_B": mom_after,
            "pointer_row_B": ptr_len,
            "mother_equation": "%d - %d + %d = %d (construct==equation, r669 dual-derive gate)" % (mom_before, moved_sum, ptr_len, mom_after),
            "blank_rows_kept": n_blank,
        },
        "phase_b_increment": {
            "r653": {
                "bytes_incl_cr": len(r653_line),
                "sha16": sha16(r653_line),
                "from": "CODELY.md",
                "to": "research/pit-lineage-receipt.md",
            },
            "r669": {
                "bytes_incl_cr": len(r669_line),
                "sha16": sha16(r669_line),
                "from": "CODELY.md",
                "to": "research/pit-git.md (split-script assertion-layer family, r651 precedent)",
            },
            "main_before_B": main_before,
            "main_after_B": main_after,
            "main_ptr_row_B": len(ptr670_b) + 1,
            "main_equation": "%d - %d - %d + %d = %d (construct==equation)" % (
                main_before, len(r653_line) + 1, len(r669_line) + 1, len(ptr670_b) + 1, main_after),
            "main_final_md5": md5(main_new),
            "pitgit_before_B": pitgit_before,
            "pitgit_after_B": pitgit_after,
            "pitgit_equation": "%d + %d + %d = %d (construct==equation)" % (
                pitgit_before, len(r669_line) + 1, len(pitgit_acct) + 1, pitgit_after),
            "pitgit_final_md5": md5(pitgit_new),
            "pitgit_acct_sha16": sha16(pitgit_acct),
        },
        "registry_row_clock": row_clock,
        "cap": CAP,
        "gates": ["main measured 30527", "mother measured 30552", "needle count==1 x12",
                  "stay anchor x17", "entry coverage gate", "sibling already-migrated x14",
                  "mother construct==equation", "mother cap", "sub cap", "main construct==equation",
                  "main cap", "pit-git construct==equation", "pit-git cap",
                  "residue-absence x14", "once-in-target x14", "stay-in-mother x17",
                  "CRLF triple-count x5", "strict reparse x4", "mojibake-free decode x4",
                  "pointer-row present x2", "preserved-face identity x2",
                  "r653 byte gate 677 (measured, claim was 676)", "r669 byte gate 802 (measured, claim was 803)",
                  "whole-domain cap gate (len() derive)", "registry rerun guard"],
        "zero_loss": True,
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT+INCREMENT PASS: mother %d->%d(-%d moved +%d ptr) | sub %dB/12+r653 | main %d->%d | pit-git %d->%d"
          % (mom_before, mom_after, moved_sum, ptr_len, len(sub_new), main_before, main_after, pitgit_before, pitgit_after))
    print("receipt", RECEIPT)
    return 0


def verify():
    r = json.load(open(RECEIPT, encoding="utf-8"))
    ok = []
    main_raw = open(MAIN, "rb").read()
    mom_raw = open(MOTHER, "rb").read()
    sub_raw = open(SUB, "rb").read()
    pg_raw = open(PITGIT, "rb").read()
    reg_raw = open(REGISTRY, "rb").read()
    pa, pb = r["phase_a_split"], r["phase_b_increment"]
    ok.append(("main_size", len(main_raw) == pb["main_after_B"]))
    ok.append(("main_md5", md5(main_raw) == pb["main_final_md5"]))
    ok.append(("mother_size", len(mom_raw) == pa["mother_after_B"]))
    ok.append(("sub_size", len(sub_raw) == pa["sub_B"]))
    ok.append(("sub_md5", md5(sub_raw) == pa["sub_md5"]))
    ok.append(("pitgit_size", len(pg_raw) == pb["pitgit_after_B"]))
    ok.append(("pitgit_md5", md5(pg_raw) == pb["pitgit_final_md5"]))
    ok.append(("main_cap", len(main_raw) <= CAP))
    ok.append(("mother_cap", len(mom_raw) <= CAP))
    ok.append(("sub_cap", len(sub_raw) <= CAP))
    ok.append(("pitgit_cap", len(pg_raw) <= CAP))
    ok.append(("r653_absent_in_main", R653_LINE_NEEDLE.encode("utf-8") not in main_raw))
    ok.append(("r669_absent_in_main", R669_LINE_NEEDLE.encode("utf-8") not in main_raw))
    ok.append(("r653_once_in_sub", sub_raw.count(R653_LINE_NEEDLE.encode("utf-8")) == 1))
    ok.append(("r669_once_in_pitgit", pg_raw.count(R669_LINE_NEEDLE.encode("utf-8")) == 1))
    for nd in MOVE_NEEDLES:
        ok.append(("move_absent_in_mother " + nd[-14:], nd.encode("utf-8") not in mom_raw))
        ok.append(("move_once_in_sub " + nd[-14:], sub_raw.count(nd.encode("utf-8")) == 1))
    for nd in STAY_LINEAGE_NEEDLES:
        ok.append(("stay_in_mother " + nd[-14:], mom_raw.count(nd.encode("utf-8")) == 1))
    for nd in MAIN_STAY_NEEDLES:
        ok.append(("stay_in_main " + nd[-14:], main_raw.count(nd.encode("utf-8")) >= 1))
    for name, body in (("main", main_raw), ("mother", mom_raw), ("sub", sub_raw), ("pit-git", pg_raw)):
        ok.append((name + "_crlf", body.count(b"\r") == body.count(b"\r\n") == body.count(b"\n")))
    ok.append(("registry_row", (REG_ROW % r["registry_row_clock"]).encode("utf-8") in reg_raw))
    rd = os.path.join(ROOT, "research")
    for f in sorted(os.listdir(rd)):
        if f.startswith("pit-") and f.endswith(".md"):
            ok.append(("domain_cap " + f, len(open(os.path.join(rd, f), "rb").read()) <= CAP))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL", len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
