"""r983 bm-b: CODELY.md hot-cold reorganization (D-20260924-01 + D-20261002-06 paradigm).

Debt face: main file 78,033B > 50KB watermark (recovery-period r947-r982 accumulation,
state.next item 0 = current-window debt). Structure diagnosis (r983 round):
  main = BlockA + BlockB(byte-identical duplicate, corruption face) + dated tail(18 rows).

Faces:
  1. dedup: BlockB removed under byte-exact identity assertion (zero info loss by
     definition; git history preserves the pre-dedup state).
  2. dated flow entries r947-r982 (tail) -> archive 202610.md verbatim + 1 cold
     pointer row (P1) in main.
  3. mini-split provenance rows r700..r943 (contiguous block incl. r800 row) ->
     archive verbatim + 1 compact routing row (P2); old cold-pointer merge rows
     r829x2/r779/r812 -> archive verbatim + 1 merge pointer row (P3).

Zero-loss assertions: every removed byte-range verbatim-in-archive; retained rows
verbatim-in-new-main; new-main strict UTF-8; new-main <= 30,720B (mini-split cap).
Receipt: results/_r983bmb_codely_minisplit.json. rc0 = done, rc2 = assertion fault
(no write on fault paths except receipt).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAIN = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202610.md")
RCPT = os.path.join(HERE, "_r983bmb_codely_minisplit.json")
CAP = 30720
WM = 50 * 1024

P1 = ("- 冷层指针（r983 bm-b 热冷整编·D-20260924-01/D-20261002-06 范式·prescan rc3 双命中=记忆/坑律类·"
      "D-20260206 集团拆件令授权迁移面）：r947-r982 恢复期 18 条判例/坑律行（git 仓二灭 forensics/r949 勘误/"
      "r950 冷索引树手术/r951 双段 closeout/r953 树杀软帽+fetch-建基座/r954-r955 回填与打捞/r956 软著布局/"
      "r957 ls-tree 空名+r958 census 分块/r959 逐文件懒取/r960 rc255 半成功/r962 混合编码 binary edit/"
      "r968 令件送达/r972 双管道死锁/r973 pythonw 流守卫/r974 MSG 送达/r982 祖先目录缺口）——原行全文 "
      "verbatim=archive 202610.md『热冷整编 2026-10-15 r983 bm-b 窗批』节（receipt=results/"
      "_r983bmb_codely_minisplit.json）；执行面法条仍活=冷索引提交一律树手术（r950）/closeout 双段式+"
      "fetch-建基座+树杀软帽（r951/r953）/恢复逐文件懒取+tmp_pack 打捞+同文件重试（r955/r959/r960）/"
      "轮报告 binary edit（r962）/每轮收口核令件+自产 MSG origin 在位性（r968/r974）/树手术 dirs 全祖先链+"
      "内容级送达断言（r982·修复版=results/_r982bmb_surgery.py）；域件归位=后续 mini-split 回扫（r747 范式）。")

P2 = ("- 域指针·r983 bm-b mini-split 史行合并（r700/r703/r731/r735/r736/r739/r747/r783/r789/r816/r833/"
      "r836/r870/r879/r885/r888/r889/r896/r939/r943 二十行——原行全文 verbatim=archive 202610.md"
      "『热冷整编 2026-10-15 r983 bm-b 窗批』节·各 receipt=results/_rNNN*.json git 史保全）：执法面路由存续"
      "——git 域动作前必读 pit-git.md 子件族+pit-git-resolver-rebase2.md〔rebase/sequencer child-2·竞速环/"
      "stash-pop/settle 面〕+pit-git-parse/staged〔porcelain 多行解析/commit 入场门/爪删集 push range〕；"
      "prereg 闸/judged 判决消费前改读 pit-protocol-judge.md·D-19 水位消费/水位探针前改读 pit-protocol-d19.md·"
      "state 簿记/QA 证据包收口前改读 pit-protocol-lane.md；machine-state/Ollama/GPU/任务健康审计面动作前改读 "
      "pit-machine.md；工具血统克隆/needle 步进/代际步进动作前改读 pit-lineage.md 与 pit-lineage-legdiff.md；"
      "selftest 接线/多入口脚本/census 判决门/转换选件动作前改读 pit-tooling.md；池文件字节编辑/settle/烧录机械/"
      "点火闸/双烧接管动作前改读 pit-pool-edit.md 与 pit-pool-burn.md；新坑律仍先入本件后回扫（直写例外 r666 范式）。")

P3 = ("- 冷层指针（r983 合并·指针合并归档 r444/r779/r800/r812 范式）：r829×2/r779/r800/r812 五条旧合并指针行"
      "——原行全文 verbatim=archive 202610.md『热冷整编 2026-10-15 r983 bm-b 窗批』节（receipt=results/"
      "_r983bmb_codely_minisplit.json）；各所指正文另在 archive 202609.md/202610.md 对应『窗批』节与各 pit-* "
      "域件；坑律本体全部在 pit-* 域件与正典件，指针行仅导航用。")

SECTION = ("\n## 热冷整编 2026-10-15 r983 bm-b 窗批（CODELY.md 78,033B>50KB 水位债清偿·主件双写去重+"
           "流水判例 18 条迁档+史行合并 25 行·D-20260924-01/D-20261002-06 范式·prescan rc3 双命中=记忆/"
           "坑律类·D-20260206 集团拆件令授权迁移面）\n\n")

RETAINED_PREFIXES = [
    b"- [2026-09-24 16:07:32] CEO \xe6\x9c\x80\xe9\xab\x98\xe5\x88\xa4\xe6\x8d\xae\xe5\xae\xa3\xe8\xa8\x80",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7git \xe5\x9f\x9f\xe9\xa6\x96\xe6\x8b\x86\xe4\xbb\xb6\xe5\xaf\xbc\xe8\x88\xaa\xe8\xa1\x8c",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 \xe6\xb1\xa0\xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 \xe5\xbc\x95\xe6\x93\x8e\xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 \xe5\x8d\x8f\xe8\xae\xae\xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- [2026-10-02 12:5x r575 bm-a]",
    b"- [2026-10-02 12:3x r365 bm-c]",
    b"- \xe5\x9d\x91\xe5\xbe\x8b\xe6\xad\xa3\xe5\x85\xb8\xe5\x85\xa8\xe9\x87\x8f\xe5\xbd\x92\xe6\xa1\xa3",
    b"- \xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xef\xbc\x9a\xe6\xb5\x81\xe6\xb0\xb4\xe5\x9e\x8b\xe6\x9d\xa1\xe7\x9b\xae",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 \xe6\x95\xb0\xe6\x8d\xae\xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 PS \xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 \xe7\xbc\x96\xe7\xa0\x81\xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 spawn/tooling \xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
    b"- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7D-20261002-06 census/tooling \xe5\x9f\x9f\xe6\x8b\x86\xe4\xbb\xb6",
]


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def splice(buf, start, end, repl):
    assert 0 <= start <= end <= len(buf)
    return buf[:start] + repl + buf[end:]


def main():
    rc = {"law": "D-20260924-01 + D-20261002-06 (r444/r812/r829 paradigms)",
          "pre_main_bytes": None, "pre_arch_bytes": None, "post_main_bytes": None,
          "post_arch_bytes": None, "dedup": {}, "blocks": [], "assertions": {},
          "retained_ok": None, "errors": []}
    try:
        m0 = open(MAIN, "rb").read()
        a0 = open(ARCH, "rb").read()
        rc["pre_main_bytes"] = len(m0)
        rc["pre_arch_bytes"] = len(a0)
        m0.decode("utf-8")
        a0.decode("utf-8")

        # ---- anchors ----
        hdr = "## Codely Structured Memories### Project".encode()
        first = m0.find(hdr)
        second = m0.find(hdr, first + 1)
        assert first == 0, "header not at offset 0"
        assert second > 0, "duplicate block header not found"
        blockA = m0[:second]

        tail_anchor = "[2026-10-14 20:41]".encode()
        tail_start = m0.find(tail_anchor)
        assert tail_start > second, "dated tail missing/misplaced"

        # dup region = [second, tail_start): CRLF-variant copy of blockA + line separator
        dup_region = m0[second:tail_start]
        # r983 diagnosis: BlockB is a CRLF-variant copy of BlockA (48 \r insertions)
        # -> identity assertion on CR-normalized bytes (line-ending-invariant identical)
        blockA_norm = blockA.replace(b"\r\n", b"\n")
        dup_norm = dup_region.replace(b"\r\n", b"\n")
        rc["dedup"] = {"blockA_len": len(blockA), "dup_start": second,
                       "dup_region_len": len(dup_region),
                       "byte_identical": dup_region == blockA,
                       "cr_normalized_identical": dup_norm in (blockA_norm, blockA_norm + b"\n"),
                       "blockA_sha16": sha16(blockA), "dup_region_sha16": sha16(dup_region),
                       "blockA_norm_sha16": sha16(blockA_norm),
                       "dup_norm_sha16": sha16(dup_norm)}
        assert rc["dedup"]["cr_normalized_identical"], "dup region not CR-normalized identical - abort"

        m1_start = m0.find("- 域指针·r700 bm-b CODELY 主件回弹热冷整编批".encode())
        assert m1_start > 0 and m1_start < second, "M1 anchor missing"
        m1 = m0[m1_start:second]
        assert m1.endswith("复述禁律）。\n".encode()) or m1.rstrip().endswith("复述禁律）。".encode()), "M1 tail mismatch"

        m2_start = m0.find("- 冷层指针（r812 合并".encode())
        kzc = m0.find("- 坑律正典全量归档".encode())
        assert 0 < m2_start < kzc < m1_start, "M2 anchors missing"
        m2 = m0[m2_start:kzc]

        m3_start = m0.find("- 冷层指针（r829 bm-b 最小冷迁".encode())
        ref_hdr = m0.find("### Reference".encode())
        assert 0 < m3_start < ref_hdr < m2_start, "M3 anchors missing"
        m3 = m0[m3_start:ref_hdr]

        m4 = m0[tail_start:]

        for tag, blk in (("M1_mini_split_rows", m1), ("M2_old_merge_ptrs_r812_r779", m2),
                         ("M3_old_cold_ptrs_r829", m3), ("M4_dated_flow_r947_r982", m4)):
            rc["blocks"].append({"tag": tag, "bytes": len(blk), "sha16": sha16(blk)})

        # ---- build new faces ----
        p1e = (P1 + "\n").encode()
        p2e = (P2 + "\n").encode()
        p3e = (P3 + "\n").encode()

        # archive append (verbatim blocks + provenance notes)
        arch_add = SECTION.encode()
        arch_add += ("### 迁档块 A：r947-r982 恢复期流水判例 18 条（CODELY 主件尾段 verbatim·"
                     "执行面活性摘录见主件 P1 冷层指针行）\n\n").encode() + m4 + b"\n"
        arch_add += ("### 迁档块 B：mini-split 史行 20 行（r700..r943 含 r800 冷指针行·原行 verbatim·"
                     "路由存续见主件 P2 合并行）\n\n").encode() + m1 + b"\n"
        arch_add += ("### 迁档块 C：旧冷指针合并行（r812/r779 两行+r829 两行·原行 verbatim·"
                     "导航存续见主件 P3 合并行）\n\n").encode() + m2 + b"\n" + m3 + b"\n"
        arch_add += ("### 去重面：主件双写块（BlockB 区 %dB=CRLF 行尾变体+分隔行）与 BlockA CR 归一化字节恒等"
                     "（norm sha16 %s 一致）——零信息损失去除，git 史保全双写前态\n"
                     % (len(dup_region), sha16(blockA_norm))).encode()
        a1 = a0 + arch_add

        # new main: splice from END to START (descending start offsets, original coords)
        nm = m0
        nm = splice(nm, tail_start, len(nm), p1e)              # M4 -> P1
        nm = splice(nm, second, tail_start, b"")               # dup region -> ""
        nm = splice(nm, m1_start, second, p2e)                  # M1 -> P2
        nm = splice(nm, m2_start, kzc, p3e)                     # M2 -> P3
        nm = splice(nm, m3_start, ref_hdr, b"")                 # M3 -> ""

        # ---- assertions ----
        rc["assertions"]["M4_verbatim_in_arch"] = a1.find(m4) >= 0
        rc["assertions"]["M1_verbatim_in_arch"] = a1.find(m1) >= 0
        rc["assertions"]["M2_verbatim_in_arch"] = a1.find(m2) >= 0
        rc["assertions"]["M3_verbatim_in_arch"] = a1.find(m3) >= 0
        rc["assertions"]["arch_size_identity"] = len(a1) == len(a0) + len(arch_add)
        rc["assertions"]["main_utf8_strict"] = True
        nm.decode("utf-8")
        rc["post_main_bytes"] = len(nm)
        rc["post_arch_bytes"] = len(a1)
        rc["assertions"]["main_le_cap_30720"] = len(nm) <= CAP
        rc["assertions"]["main_le_watermark_50KB"] = len(nm) <= WM
        rc["assertions"]["P1_in_main"] = nm.find(p1e) >= 0
        rc["assertions"]["P2_in_main"] = nm.find(p2e) >= 0
        rc["assertions"]["P3_in_main"] = nm.find(p3e) >= 0
        rc["assertions"]["dup_gone"] = nm.count(hdr) == 1
        rc["assertions"]["dated_gone"] = nm.find(tail_anchor) < 0
        rc["retained_ok"] = all(p in nm for p in RETAINED_PREFIXES)
        rc["assertions"]["retained_rows_verbatim"] = rc["retained_ok"]
        # byte arithmetic: removed == dup_region + M1..M4 ; added == P1..P3
        removed = len(dup_region) + len(m1) + len(m2) + len(m3) + len(m4)
        added = len(p1e) + len(p2e) + len(p3e)
        rc["byte_math"] = {"removed_bytes": removed, "added_bytes": added,
                           "expected_post": len(m0) - removed + added,
                           "identity": len(m0) - removed + added == len(nm)}
        rc["assertions"]["byte_math_identity"] = rc["byte_math"]["identity"]

        ok = (all(rc["assertions"].values()) and rc["retained_ok"]
              and rc["dedup"]["cr_normalized_identical"])
        rc["verdict"] = "PASS" if ok else "FAIL"
        if not ok:
            json.dump(rc, open(RCPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("ASSERTION FAULT - no write; see receipt")
            return 2

        # snapshots (rollback face)
        open(os.path.join(HERE, "_r983bmb_codely_pre.bin"), "wb").write(m0)
        open(os.path.join(HERE, "_r983bmb_arch202610_pre.bin"), "wb").write(a0)
        open(MAIN, "wb").write(nm)
        open(ARCH, "ab").write(arch_add)
        json.dump(rc, open(RCPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("PASS main %d->%dB (cap %d) arch %d->%dB blocks=%d dedup=%dB" % (
            len(m0), len(nm), CAP, len(a0), len(a1), len(rc["blocks"]), len(dup_region)))
        return 0
    except AssertionError as e:
        rc["errors"].append("assert: %s" % e)
        rc["verdict"] = "FAULT"
        json.dump(rc, open(RCPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("FAULT: %s" % e)
        return 2
    except Exception as e:
        rc["errors"].append(repr(e))
        rc["verdict"] = "FAULT"
        json.dump(rc, open(RCPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("FAULT: %r" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
