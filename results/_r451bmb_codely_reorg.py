"""r451 bm-b CODELY.md hot-cold reorg (O-20260927-0230 law: >10KB hard line).

Water line: 10,894B pre-append. This window: append r451 P0 lesson (fixture
topology + batch-level accrual anchor law), then pointer-merge two cold
groups (r444-r457 bm-a probe/surgery family + r229-r440 09-29 era family)
into two consolidated pointer lines. Zero-loss discipline: every dropped
pointer line is (a) verified to reference an archive section that EXISTS
in research/memory-archive/202609.md and (b) migrated verbatim into a new
archive window section as migration trace. Final size asserted <=10,000B.
"""
import re
import sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
NEW_SECTION = "## 热冷整编 2026-09-30 r451 bm-b 窗批（指针合并归档 r444 范式）"

GROUP_A_KEYS = [
    "r445 采集器无超时挂死盲区坑",
    "r445 dual-nulls seed",
    "r444 S6 批跑器无参腿伪参数坑",
    "r456 a158 冻结面抽位点对账",
    "r457 风暴 resolver 非幂等追加坑",
    "r446 bm-b 手术过继残漏三连坑",
]
GROUP_B_KEYS = [
    "r440 撞批三查律+r449 风暴 union",
    "r440 bm-b 初筛富集面",
    "r242 bm-c runner 外科手术四连坑族",
    "r229 LHB 源改史+r235 core48 源分层+r237",
]
MERGED_A = (
    "- 冷层指针（r451 合并·r444 范式）：r444 S6 批跑器无参腿伪参数坑（r457 bm-a 节）+r445 采集器无超时挂死盲区坑"
    "（r457 bm-a 节·conn-fuse 对 hang 失明）+r445 dual-nulls seed 声明≠实跑基坑（r455 bm-a 节）+r456 a158 冻结面"
    "抽位点对账 eps 分母坑（r459 bm-a 节）+r457 风暴 resolver 非幂等追加坑（r253 bm-c 节）+r446 bm-b 手术过继残漏"
    "三连坑（r459 bm-a 窗批三节·r446 三命令实弹首跑律）六条全文 verbatim=archive 202609.md 各对应节。"
)
MERGED_B = (
    "- 冷层指针（r451 合并·r444 范式）：r440 撞批三查律+r449 风暴 union 复活去重律（r245 bm-c 节）+r440 bm-b 初筛"
    "富集面≠注册级增量律（r449 bm-a 节）+r242 bm-c runner 外科手术四连坑族（r449 bm-a 节）+r229 LHB 源改史+r235 "
    "core48 源分层+r237 波级泊位窗先例三律（r447 bm-a 节）四条全文 verbatim=archive 202609.md 各对应节。"
)
R451_LESSON = (
    "- [2026-09-30 08:5x r451 bm-b] 合成夹具拓扑坑+批级 accrual 锚定律（W8 首烧 GATE-REFUSE 实弹·35s exit2 零污染）："
    "selftest 夹具不还原真实面关键拓扑（本例=首锚奇异 2021-01-18·冻结面明文「预热段奇异锚=1」）时，自派生门"
    "（lo_a==lo_b）在真实面首跑构造性永拒——B 臂 LW 恒 PD 无奇异概念，自派生 lo=首锚≠冻结批级 lo=首有效锚 2021-02-23。"
    "修法=批级 lo 由 cmd_run 单点派生传入全部格（arm_series 增 lo_ts 参·预热段块不记成本不记事件）+冻结名义断言"
    "（lo≠2021-02-23 即拒烧）。How to apply：①runner 自派生门必配真实面冻结名义断言；②夹具必植真实面关键拓扑"
    "（首锚奇异类），selftest 绿≠真实面可烧——三命令实弹首跑律（r446）不可省；③spec 与 gate 冲突时以冻结 spec "
    "为真值源修 runner 禁动判据。"
)


def main():
    codely = open(CODELY, encoding="utf-8").read()
    archive = open(ARCHIVE, encoding="utf-8").read()
    lines = codely.split("\n")

    dropped = []
    kept = []
    for ln in lines:
        hit = None
        for grp, keys in (("A", GROUP_A_KEYS), ("B", GROUP_B_KEYS)):
            if any(k in ln for k in keys) and ln.startswith("- 冷层指针"):
                hit = grp
                break
        if hit:
            dropped.append((hit, ln))
        else:
            kept.append(ln)

    # zero-loss face 1: every dropped pointer's referenced archive section exists
    for _, ln in dropped:
        m = re.search(r"『([^』]+)』", ln)
        assert m, f"no archive section ref in dropped line: {ln[:60]}"
        assert m.group(1) in archive, f"archive section missing: {m.group(1)}"

    out = []
    for ln in kept:
        out.append(ln)
        if ln.strip() == "### Feedback":
            pass  # lesson appended after existing feedback block below
    txt = "\n".join(out)

    # insert merged pointers at the positions of their groups' first dropped line
    # (simplest: append merged A after the Feedback cold-pointer block, merged B
    #  in the Project section) -- place both right after their section headers'
    # existing content; deterministic anchor = insert before "### Project" for A,
    # before "### Reference" for B.
    txt = txt.replace("### Project\n", MERGED_A + "\n### Project\n", 1)
    txt = txt.replace("### Reference\n", MERGED_B + "\n### Reference\n", 1)

    # append r451 lesson at end of Feedback section (before blank line + ### Project)
    idx = txt.find("### Project")
    head, tail = txt[:idx], txt[idx:]
    # drop the trailing blank line of head into the lesson insert
    head = head.rstrip("\n")
    txt = head + "\n" + R451_LESSON + "\n\n" + tail

    size = len(txt.encode("utf-8"))
    assert size <= 10000, f"post-reorg size {size} > 10KB hard line"

    # zero-loss face 2: migration trace -- dropped pointer lines verbatim to archive
    trace = ["", NEW_SECTION, ""]
    for grp, ln in dropped:
        trace.append(f"- [迁移留痕·组{grp}] {ln.strip()}")
    trace.append("")
    with open(ARCHIVE, "a", encoding="utf-8") as fh:
        fh.write("\n".join(trace))
    with open(CODELY, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)

    # verify: every dropped line byte-present in archive trace
    new_archive = open(ARCHIVE, encoding="utf-8").read()
    for _, ln in dropped:
        assert ln.strip() in new_archive, f"dropped line not in archive: {ln[:40]}"
    print(f"reorg OK: dropped {len(dropped)} pointer lines (A={sum(1 for g,_ in dropped if g=='A')} "
          f"B={sum(1 for g,_ in dropped if g=='B')}), merged 2, lesson appended; "
          f"CODELY {len(codely.encode('utf-8'))} -> {size}B; archive sections verified; "
          f"trace appended to archive")


if __name__ == "__main__":
    main()
