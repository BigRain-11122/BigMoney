# -*- coding: utf-8 -*-
"""r669 bm-c: D-06 pit-git-resolver over-cap sub-split + main increment batch.

Trigger: bm-a r817 10:06 increment pushed pit-git-resolver.md to a MEASURED
30,850B > 30,720B domain cap (r668 close face claimed 'room 308B' from stale
30,412B receipt = live recurrence of the r653 receipt-vs-measured law; this
batch measures at use time). Main CODELY.md at 30,719B (1B headroom) gets the
r659 entry out per r668 next-pointer candidate.

Phase A (split, r441 ritual): rebase/sequencer netpath family 9 entries
(r516/r782-bma/r642/r787/r648/r794/r808/r658/r817) verbatim OUT ->
research/pit-git-resolver-rebase.md (new sub-file, research/ protection
family). Mother keeps merge-resolver decisioner core (ts-newer-wins/twin/
block-face/assert-layer) + S0-dirty-window worksnap + increment append face.
Phase B (increment, r668 ritual): main r659 entry (rebase --continue no-EDITOR
Terminal-dumb -> r808 three-step cure) 994B verbatim OUT of main ->
mother append face + in-file accounting line (r653 live-case annotated).

Laws: r335 machine-migration (byte surgery, no hand copy), r614 atomic
os.replace, r402 CRLF triple-count + preserved-face identity, r419/r420
assertion battery + needle-avoid-furniture, r441 treasure migration ritual
(prescan rc3 + registry pre-registration row + receipt + --verify),
r583 facts-driven never hand-typed, r653 measure-at-use-time.

Modes:
    python -X utf8 Tools/_r669bmc_pit_resolver_split.py            # do batch
    python -X utf8 Tools/_r669bmc_pit_resolver_split.py --verify   # re-check
"""
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
MOTHER = os.path.join(ROOT, "research", "pit-git-resolver.md")
SUB = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")
REGISTRY = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r669bmc_pit_resolver_split.json")
CAP = 30720

MOVE_NEEDLES = [
    "[2026-10-05 05:5x r516 bm-c]",
    "[2026-10-06 16:3x r782 bm-a]",
    "[2026-10-06 23:4x r642 bm-c]",
    "[2026-10-06 23:5x r787 bm-b]",
    "[2026-10-07 02:4x r648 bm-c]",
    "[2026-10-07 04:2x r794 bm-b]",
    "[2026-10-07 04:4x r808 bm-a]",
    "[2026-10-07 06:1x r658 bm-c]",
    "[2026-10-07 10:4x r817 bm-a]",
]
R659_NEEDLE = "[2026-10-07 06:3x r659 bm-c]"
R653_NEEDLE = "[2026-10-07 04:3x r653 bm-c]"
R668_NEEDLE = "[2026-10-07 10:2x r668 bm-c]"
STAY_NEEDLES = [R653_NEEDLE, R668_NEEDLE]  # main-side stay anchors
STAY_MOTHER_NEEDLES = [
    "[2026-10-05 08:1x r522 bm-c]",
    "[2026-10-05 00:5x r704 bm-a]",
    "[2026-10-05 01:3x r506 bm-c]",
    "[2026-10-05 03:43 r510 bm-c]",
    "[2026-10-05 03:5x r708 bm-b]",
    "[2026-10-05 04:0x r511 bm-c]",   # bullet-less form, containment match
    "[2026-10-05 04:16 r709 bm-b]",
    "[2026-10-05 05:2x r515 bm-c]",
    "[2026-10-05 06:1x r710 bm-a]",
    "[2026-10-05 07:0x r711 bm-a]",   # bullet-less form, containment match
    "[2026-10-06 01:2x r584 bm-c]",
    "[2026-10-06 02:1x r756 bm-b]",
    "[2026-10-06 11:4x r773 bm-b]",
    "[2026-10-06 04:4x r756 bm-a]",
    "[2026-10-06 08:1x r764 bm-a]",
    "[2026-10-06 09:16 r609 bm-c]",
    "[2026-10-06 10:0x r611 bm-c]",
    "[2026-10-06 19:2x r637 bm-c]",
    "[2026-10-06 21:3x r782 bm-b]",
]


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
            if os.path.abspath(p) != os.path.abspath(exclude):
                out[f] = open(p, "rb").read()
    return out


PTR_ROW = (
    "> 子件分拆行（r669 bm-c·D-20261002-06 域件 ≤30KB 判据腿·实测触发=bm-a r817 10:06 增量致本件 30,850B>30,720B 超线〔r668 收据面「room 308B」声明=陈旧收据假设·r653 收据-实测律活案例·当场实测 derive〕·迁移仪式 r441 同款）："
    "rebase/sequencer 净路族 9 条（r516/r782-bma/r642/r787/r648/r794/r808/r658/r817）verbatim 迁出→**research/pit-git-resolver-rebase.md**"
    "（件内字节对账+md5 行·零丢失断言·receipt results/_r669bmc_pit_resolver_split.json）；"
    "本件保留 merge resolver 决策器核心族（ts-newer-wins/孪生分派/块界解析/断言层假阳性）+S0 脏窗 worksnap 族+S7 集成窗 merge-mode 正典+增量回扫 append 面（r659 同窗迁入）；"
    "rebase continue/quit/pick/autostash/假拒绝净路与 sequencer 拒进动作前改读 pit-git-resolver-rebase.md。"
)

SUB_TITLE = (
    "# pit-git-resolver-rebase —— rebase/sequencer 净路与 continue/autostash/quit 族坑律正典"
    "（D-20261002-06 域分件·pit-git-resolver sub-split·2026-10-07 r669 bm-c 新立）"
)
SUB_SRC = (
    "> 来源：research/pit-git-resolver.md 整族 9 条 verbatim 迁出（2026-10-07 r669 bm-c·超线 sub-split；机制=r335 机证律·拆件脚本机械迁移非手抄·r441 模板·宝藏迁移仪式=登记册出入记录预登记行）。"
)
SUB_SCOPE = (
    "> 执法面：rebase --continue 一切拒进形态（假「You must edit all merge conflicts」/Terminal is dumb 无 EDITOR/复跑三步=no change 恒拒）·r808 三步治愈律（author-script 注入+commit -F+再 continue）·--quit 与游离 HEAD·pick 窗 git show :N: 空读·autostash pop 冲突致死与 EOL pop·冲突窗 add -u 循环污染·host-ours 宿主面取侧——rebase 冲突收口、continue 拒进诊断、autostash/quit 处置前必读本件；母件 pit-git-resolver.md 保留 merge resolver 决策器核心+append 面。"
)


def build_sub_accounting(n, sum_crlf, core_lf, mother_before, mother_after, moved_sum, ptr_len):
    return (
        "> 字节对账行（零丢失断言）：本件 %d 条·条目字节和（含 CRLF 行尾）=%dB==母件净删减分摊；迁移核（LF blob 面）=%dB·md5=%s；母件迁出前 %dB→迁出后 %dB（净变化=−%dB 迁出+%dB 指针行）；本件由拆件脚本机械迁移非手抄·receipt results/_r669bmc_pit_resolver_split.json。"
        % (n, sum_crlf, len(core_lf), md5(core_lf), mother_before, mother_after, moved_sum, ptr_len)
    )


SUB_POST = "> 后续批次：增量回扫 append 面仍在母件 pit-git-resolver.md（post-split convention·r441）；本件为 sub-split 终态子件——再超线时由下一让位窗处置。"

ACCT_LINE = (
    "增量回扫行（r669 bm-c·D-20261002-06 主件 ≤30KB 判据腿·迁移仪式 r668 同款）：主件 CODELY.md r659 坑（rebase --continue 无 EDITOR 拒进新形态·Terminal is dumb→r808 三步治愈律再实证·pit-git-resolver 族新症状面）994B verbatim 迁入本件 append 面——逐条字节+sha16 对账=receipt results/_r669bmc_pit_resolver_split.json"
    "（零丢失断言=bytes in target verbatim+主件保留面恒等式+主件 ≤30KB+全域件 ≤30KB·prescan rc3 留痕）；"
    "r653 收据-实测律同窗活案例勘注：r668 收据面「pit-git-resolver room 308B」声明=陈旧收据假设——bm-a r817 同窗 10:06 增量后本件实测 30,850B 超线，close/指针面一切尺寸声明一律当场 git cat-file 实测 derive 禁跨轮复制上轮收据；"
    "主件余 r653 收据坑（676B）待 pit-lineage.md 域件让位窗迁出（30,552B 满员）。"
)

REG_ROW = (
    "- %s bm-c r669 D-06 resolver 超线 sub-split+主件增量回扫迁移仪式（实测触发=bm-a r817 增量致 pit-git-resolver.md 30,850B>30,720B 域线〔r668 收据面 room-308B 声明=陈旧收据假设·r653 活案例〕）：rebase/sequencer 净路族 9 条 verbatim 零丢失迁出→research/pit-git-resolver-rebase.md（新子件同入 research/ 保护族）+CODELY.md 主件 r659 坑 994B verbatim 迁入母件 append 面；prescan 实弹 rc3 命中三路径留痕（CODELY.md/pit-git-resolver.md/pit-lineage.md）——D-20261002-06 集团拆件令×TREASURE_PROTECTION_LAW §2 门机械交集裁定=零丢失 verbatim 迁移非删除类（r441/r651/r654/r662 交付先例·全部字节留仓·登记册属主行不动）；仪式四件=prescan rc3 留痕+本预登记行+断言电池（needle count==1/字节对账/md5/CRLF 三计数/保留面恒等/全件 ≤30,720B）+receipt results/_r669bmc_pit_resolver_split.json 与 --verify 复验。"
)


def main():
    main_raw = open(MAIN, "rb").read()
    mom_raw = open(MOTHER, "rb").read()
    main_before, mom_before = len(main_raw), len(mom_raw)
    assert mom_before == 30850, "mother measured-size gate: %d != 30850 (derive at use time, r653)" % mom_before
    assert main_before == 30719, "main measured-size gate: %d" % main_before
    assert not os.path.exists(SUB), "sub-file already exists (rerun?)"

    # ---------- Phase A: split ----------
    crlf_invariant(mom_raw, "mother")
    lines = mom_raw.split(b"\r\n")
    assert lines[-1] == b"", "trailing element gate"
    real = lines[:-1]
    assert len(real) == 31, "mother line count gate: %d" % len(real)

    # needle -> exactly one containing line, bullet form
    move_idx = {}
    for nd in MOVE_NEEDLES:
        assert mom_raw.count(nd.encode("utf-8")) == 1, "raw needle count!=1: %s" % nd
        hits = [i for i, l in enumerate(real) if nd.encode("utf-8") in l]
        assert len(hits) == 1, "needle line!=1: %s -> %s" % (nd, hits)
        assert real[hits[0]].startswith(b"- ["), "bullet form gate: %s" % nd
        move_idx[nd] = hits[0]
    assert len(set(move_idx.values())) == 9, "move index overlap"
    mv_sorted = sorted(move_idx.values())
    assert mv_sorted == [11, 21, 24, 25, 26, 27, 28, 29, 30], "move index set drift: %s" % mv_sorted

    # stay anchors intact (19; two bullet-less via containment)
    stay_hits = {}
    for nd in STAY_MOTHER_NEEDLES:
        hits = [i for i, l in enumerate(real) if nd.encode("utf-8") in l]
        assert len(hits) == 1, "stay anchor not unique: %s -> %s" % (nd, hits)
        assert hits[0] not in move_idx.values(), "stay anchor scheduled to move: %s" % nd
        stay_hits[nd] = hits[0]
    assert len(set(stay_hits.values())) == 19, "stay overlap"
    assert set(stay_hits.values()) | set(move_idx.values()) == set(range(3, 31)), "header+entry coverage gate"

    # already-migrated law: move needles + r659 absent from sibling pit files
    for fname, body in sibling_bodies(MOTHER).items():
        for nd in MOVE_NEEDLES + [R659_NEEDLE]:
            assert nd.encode("utf-8") not in body, "needle already in sibling %s: %s" % (fname, nd)

    moved_lines = [real[i] for i in mv_sorted]
    moved_sum = sum(len(l) + 2 for l in moved_lines)
    assert moved_sum == 10014, "moved sum gate: %d" % moved_sum
    core_lf = b"".join(l.replace(b"\r", b"") + b"\n" for l in moved_lines)

    # new mother: header 3 lines + PTR + surviving ENTRY lines (original order) + trailing
    ptr_b = PTR_ROW.encode("utf-8")
    ptr_len = len(ptr_b) + 2
    survivors = [l for i, l in enumerate(real) if i >= 3 and i not in move_idx.values()]
    assert len(survivors) == 19, "survivor count gate: %d" % len(survivors)
    new_real = real[:3] + [ptr_b] + survivors
    assert len(new_real) == 23, "new mother real-line count gate: %d" % len(new_real)
    mom_new = b"\r\n".join(new_real + [b""])
    mom_after = len(mom_new)
    assert mom_after == mom_before - moved_sum + ptr_len, "mother byte equation: %d" % mom_after
    assert mom_after <= CAP, "mother cap gate A: %d" % mom_after

    # sub-file compose
    n = len(moved_lines)
    sub_accounting = build_sub_accounting(n, moved_sum, core_lf, mom_before, mom_after, moved_sum, ptr_len)
    hdr = [s.encode("utf-8") for s in (SUB_TITLE, "", SUB_SRC, SUB_SCOPE, sub_accounting, SUB_POST, "")]
    sub_new = b"\r\n".join(hdr + moved_lines + [b""])

    # Phase A gates
    for nd in MOVE_NEEDLES:
        assert nd.encode("utf-8") not in mom_new, "residue in mother: %s" % nd
        assert sum(1 for l in sub_new.split(b"\r\n") if l.startswith(b"- [") and nd.encode("utf-8") in l) == 1, "not once in sub: %s" % nd
    for nd in STAY_MOTHER_NEEDLES:
        assert sum(1 for l in mom_new.split(b"\r\n") if nd.encode("utf-8") in l) == 1, "stay lost from mother: %s" % nd
    crlf_invariant(mom_new, "mother-new")
    crlf_invariant(sub_new, "sub")
    assert sub_new.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR in sub"
    sub_new.decode("utf-8")
    mom_new.decode("utf-8")
    assert b"????" not in sub_new and b"????" not in mom_new, "mojibake gate"
    assert sub_new.count(b"\r\n") == len(hdr) + n, "sub line count gate"
    assert ptr_b in mom_new, "pointer row missing"
    # preserved-face identity (survivors byte-identical, order preserved)
    assert [l for l in mom_new.split(b"\r\n") if l in survivors] == survivors, "preserved-face order gate"

    # ---------- Phase B: main r659 -> mother ----------
    crlf_invariant(main_raw, "main")
    assert main_raw.count(R659_NEEDLE.encode("utf-8")) == 1, "r659 raw needle count gate"
    mlines = main_raw.split(b"\n")
    assert mlines[-1] == b"", "main trailing gate"
    mbody = mlines[:-1]
    hits = [i for i, l in enumerate(mbody) if R659_NEEDLE.encode("utf-8") in l]
    assert len(hits) == 1, "r659 line count gate: %s" % hits
    i659 = hits[0]
    r659_line = mbody[i659]
    assert r659_line.endswith(b"\r"), "r659 CR-tail gate"
    assert len(r659_line) == 994, "r659 byte gate: %d" % len(r659_line)
    assert r659_line.startswith(b"- ["), "r659 bullet gate"
    r659_sha16 = sha16(r659_line)
    # stay anchors in main survive untouched
    for nd in STAY_NEEDLES:
        assert main_raw.count(nd.encode("utf-8")) == 1, "main stay anchor gate: %s" % nd

    mbody2 = mbody[:i659] + mbody[i659 + 1:]
    main_new = b"\n".join(mbody2) + b"\n"
    main_after = len(main_new)
    assert main_after == main_before - (len(r659_line) + 1), "main byte equation: %d" % main_after
    assert main_after == 29724, "main after gate: %d" % main_after
    assert main_after <= CAP, "main cap gate"

    acct_b = ACCT_LINE.encode("utf-8") + b"\r"
    mom_final = mom_new + r659_line + b"\n" + acct_b + b"\n"
    mom_final_after = len(mom_final)
    assert mom_final_after == mom_after + (len(r659_line) + 1) + (len(acct_b) + 1), "mother final equation: %d" % mom_final_after
    assert mom_final_after <= CAP, "mother cap gate B: %d" % mom_final_after

    # Phase B gates
    assert r659_line in mom_final, "r659 verbatim-in-target gate"
    assert R659_NEEDLE.encode("utf-8") not in main_new, "marker-absence gate"
    assert main_new.split(b"\n") == mbody2 + [b""], "main preserved-face identity"
    crlf_invariant(main_new, "main-new")
    crlf_invariant(mom_final, "mother-final")
    main_new.decode("utf-8")
    mom_final.decode("utf-8")
    for nd in STAY_NEEDLES:
        assert main_new.count(nd.encode("utf-8")) == 1, "main stay survived gate: %s" % nd
    assert mom_final.count(R659_NEEDLE.encode("utf-8")) == 1, "r659 once-in-mother gate"

    # ---------- registry pre-registration row ----------
    reg_raw = open(REGISTRY, "rb").read()
    reg_is_crlf = reg_raw.count(b"\r\n") >= 10 and b"\n" not in reg_raw.replace(b"\r\n", b"")
    row_clock = fuzzy_clock()
    row = (REG_ROW % row_clock).encode("utf-8")
    assert row not in reg_raw, "registry row already appended (rerun?)"
    eol = b"\r\n" if reg_is_crlf else b"\n"
    reg_new = reg_raw + (b"" if reg_raw.endswith(eol) else eol) + row + eol
    crlf_invariant(reg_new, "registry") if reg_is_crlf else None
    reg_new.decode("utf-8")

    # ---------- atomic writes (r614) ----------
    for path, data in ((SUB, sub_new), (MOTHER, mom_final), (MAIN, main_new), (REGISTRY, reg_new)):
        tmp = path + ".tmp_r669"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r669 bm-c",
        "batch": "D-06 pit-git-resolver over-cap sub-split + main increment",
        "prescan_rc": 3,
        "prescan_note": "registry hits CODELY.md + research/pit-git-resolver.md + research/pit-lineage.md; r441/r651/r654/r662/r668 operative precedent: verbatim zero-loss relocation, not deletion; registry owner rows untouched; live case of r653 receipt-vs-measured law (r668 close face claimed room 308B from stale 30,412B receipt; bm-a r817 10:06 increment made measured 30,850B > 30,720B; this batch derives all sizes at use time)",
        "trigger": "pit-git-resolver.md measured 30,850B > 30,720B domain cap after bm-a r817 increment (git 9f9ce25ca 10:06)",
        "phase_a_split": {
            "moved_entries": 9,
            "moved_needles": MOVE_NEEDLES,
            "moved_sum_crlf_B": moved_sum,
            "moved_core_lf_md5": md5(core_lf),
            "sub_file": "research/pit-git-resolver-rebase.md",
            "sub_B": len(sub_new),
            "sub_md5": md5(sub_new),
            "mother_before_B": mom_before,
            "mother_after_split_B": mom_after,
            "pointer_row_B": ptr_len,
            "mother_equation": "%d - %d + %d = %d" % (mom_before, moved_sum, ptr_len, mom_after),
        },
        "phase_b_increment": {
            "entry": "r659 bm-c rebase --continue no-EDITOR Terminal-dumb pit",
            "bytes_incl_cr": len(r659_line),
            "sha16": r659_sha16,
            "from": "CODELY.md",
            "to": "research/pit-git-resolver.md (append face, post-split convention)",
            "accounting_line_B": len(acct_b),
            "accounting_line_sha16": sha16(acct_b),
            "main_before_B": main_before,
            "main_after_B": main_after,
            "main_equation": "%d - %d = %d" % (main_before, len(r659_line) + 1, main_after),
            "mother_after_split_B": mom_after,
            "mother_final_B": mom_final_after,
            "mother_final_equation": "%d + %d + %d = %d" % (mom_after, len(r659_line) + 1, len(acct_b) + 1, mom_final_after),
            "mother_final_md5": md5(mom_final),
            "main_final_md5": md5(main_new),
        },
        "registry_row_clock": row_clock,
        "stay_in_main": ["r653 (676B, pending pit-lineage relief window)", "r668 calendar-law pit"],
        "cap": CAP,
        "gates": ["mother measured 30850", "main measured 30719", "needle count==1 x10",
                  "move index set pin", "stay anchor x19", "sibling already-migrated x10",
                  "mother byte equation", "mother cap A/B", "sub cap", "sub line count",
                  "residue-absence x9", "once-in-sub x9", "stay-in-mother x19",
                  "CRLF triple-count x4", "strict reparse x4", "mojibake gate",
                  "pointer-row present", "preserved-face identity x2",
                  "r659 byte gate 994", "main equation 29725", "main cap",
                  "verbatim-in-target", "marker-absence", "main stay x2",
                  "r659 once-in-mother", "registry rerun guard"],
        "zero_loss": True,
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT+INCREMENT PASS: mother %d->%d(-%d moved +%d ptr) then +r659 994B+acct -> %d | sub %dB/%d entries | main %d->%d"
          % (mom_before, mom_after, moved_sum, ptr_len, mom_final_after, len(sub_new), n, main_before, main_after))
    print("receipt", RECEIPT)
    return 0


def verify():
    r = json.load(open(RECEIPT, encoding="utf-8"))
    ok = []
    main_raw = open(MAIN, "rb").read()
    mom_raw = open(MOTHER, "rb").read()
    sub_raw = open(SUB, "rb").read()
    reg_raw = open(REGISTRY, "rb").read()
    pa, pb = r["phase_a_split"], r["phase_b_increment"]
    ok.append(("main_size", len(main_raw) == pb["main_after_B"]))
    ok.append(("main_md5", md5(main_raw) == pb["main_final_md5"]))
    ok.append(("mother_size", len(mom_raw) == pb["mother_final_B"]))
    ok.append(("mother_md5", md5(mom_raw) == pb["mother_final_md5"]))
    ok.append(("sub_size", len(sub_raw) == pa["sub_B"]))
    ok.append(("sub_md5", md5(sub_raw) == pa["sub_md5"]))
    ok.append(("main_cap", len(main_raw) <= CAP))
    ok.append(("mother_cap", len(mom_raw) <= CAP))
    ok.append(("sub_cap", len(sub_raw) <= CAP))
    ok.append(("r659_absent_in_main", R659_NEEDLE.encode("utf-8") not in main_raw))
    ok.append(("r659_once_in_mother", mom_raw.count(R659_NEEDLE.encode("utf-8")) == 1))
    for nd in MOVE_NEEDLES:
        ok.append(("move_absent_in_mother " + nd[-20:], nd.encode("utf-8") not in mom_raw))
        ok.append(("move_once_in_sub " + nd[-20:], sub_raw.count(nd.encode("utf-8")) == 1))
    for nd in STAY_MOTHER_NEEDLES:
        ok.append(("stay_in_mother " + nd[-20:], mom_raw.count(nd.encode("utf-8")) == 1))
    for nd in STAY_NEEDLES:
        ok.append(("stay_in_main " + nd[-20:], main_raw.count(nd.encode("utf-8")) == 1))
    for name, body in (("main", main_raw), ("mother", mom_raw), ("sub", sub_raw)):
        ok.append((name + "_crlf", body.count(b"\r") == body.count(b"\r\n") == body.count(b"\n")))
    ok.append(("registry_row", (REG_ROW % r["registry_row_clock"]).encode("utf-8") in reg_raw))
    ok.append(("acct_line_present", pb["accounting_line_sha16"] in [sha16(l + b"\r") for l in mom_raw.split(b"\r\n") if ACCT_LINE[:30].encode("utf-8") in l]))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL", len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
