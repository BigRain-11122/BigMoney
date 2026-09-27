# -*- coding: utf-8 -*-
"""r359 bm-a fixer pass 2. Root causes from pass 1: (a) archive appends used
newline=anl translation param PLUS explicit '+anl' concatenation -> every
appended line got double-CR (b'\\r\\r\\n') which renders as phantom blank
lines; (b) the conditional r359 verbatim append landed BEFORE the 30th-batch
section header; (c) CODELY.md still 10,925B > 10,240B hard line. Fix: (1)
rebuild the archive tail byte-precisely -- cut everything after the 29th
batch section's last row (r355) and re-append the 30th-batch section with
raw \\r\\n bytes in canonical order (blank, header, r109, r342, r359);
(2) CODELY.md: second-stage pointer folding (canon precedent: 27th batch
'指针行二次折叠') -- shorten '全文 verbatim=research/memory-archive/202609.md'
boilerplate to '全文=archive 202609.md' on all pointer rows + tighten the
30th-batch summary row. Fail-closed verifications on both files."""
import io
import sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

R355_ANCHOR = "- [2026-09-27 21:1x r355 bm-a] 坑律：同轮连续风暴的 resolver 重跑防护"


def main():
    # ---------- (1) archive tail rebuild, byte-precise ----------
    raw = open(ARCHIVE, "rb").read()
    txt = raw.decode("utf-8")
    i = txt.index(R355_ANCHOR)
    end = txt.index("\n", i) + 1          # end of r355 row line (incl newline)
    head = txt[:end]
    tail_artifacts = txt[end:]
    n_double_cr = tail_artifacts.count("\r\r\n")
    # collect the three verbatim row texts from the artifact region
    segs = [s for s in tail_artifacts.replace("\r\r\n", "\n").split("\n")
            if s.strip()]
    r109 = [s for s in segs if s.startswith("- [2026-09-27 21:3x r109 bm-c]")]
    r342 = [s for s in segs if s.startswith("- [2026-09-27 21:15 r342 bm-b]")]
    r359 = [s for s in segs if s.startswith("- [2026-09-27 22:1x r359 bm-a] 坑律：共享控制面")]
    assert len(r109) == 1 and len(r342) == 1 and len(r359) == 1, \
        f"artifact rows r109={len(r109)} r342={len(r342)} r359={len(r359)}"
    assert n_double_cr >= 3, f"double-CR count={n_double_cr} (expected >=3)"
    header = ("## 坑律归档 2026-09-27 三十批"
              "（r359 bm-a·CODELY.md 10KB 硬线当窗整编·行级零丢失）")
    rebuilt = (head + "\r\n" + header + "\r\n" + "\r\n"
               + r109[0] + "\r\n" + r342[0] + "\r\n" + r359[0] + "\r\n")
    # head must itself be CRLF-consistent; verify no lone LF got introduced
    assert "\r\r" not in rebuilt, "double-CR leaked into rebuilt tail"
    with open(ARCHIVE, "wb") as fh:
        fh.write(rebuilt.encode("utf-8"))

    # ---------- (2) CODELY.md second-stage pointer folding ----------
    raw_c = open(CODELY, "rb").read()
    c_txt = raw_c.decode("utf-8")
    n_boiler = c_txt.count("全文 verbatim=research/memory-archive/202609.md")
    c_txt = c_txt.replace("全文 verbatim=research/memory-archive/202609.md",
                          "全文=archive 202609.md")
    # tighten the 30th-batch summary row (mine, this round)
    old_sum_start = "- 三十批外迁（r359 bm-a·2026-09-27·10KB 硬线当窗整编·行级零丢失）："
    j = c_txt.index(old_sum_start)
    j_end = c_txt.index("\n", j)
    new_sum = ("- 三十批外迁（r359 bm-a·2026-09-27·10KB 硬线当窗整编·行级零丢失）："
               "r96/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 十条全文行=二十九批 "
               "union 再 materialize 面，折叠回指针（verbatim 已在二十九批节）"
               "+r109bmc/r342bmb/r359bma 三行 verbatim 入三十批节；"
               "保留=User 元律+法行 2+批指针行族。")
    c_txt = c_txt[:j] + new_sum + c_txt[j_end:]
    with open(CODELY, "wb") as fh:
        fh.write(c_txt.encode("utf-8"))

    # ---------- verify ----------
    a2 = open(ARCHIVE, "rb").read().decode("utf-8")
    hh = a2.index("## 坑律归档 2026-09-27 三十批")
    section = a2[hh:]
    order = [section.index("21:3x r109 bm-c]"),
             section.index("21:15 r342 bm-b]"),
             section.index("22:1x r359 bm-a] 坑律：共享控制面")]
    assert order == sorted(order), "30th-batch row order wrong"
    assert "\r\r" not in a2[hh:], "double-CR still in rebuilt section"
    assert R355_ANCHOR in a2, "r355 anchor lost"
    size = len(open(CODELY, "rb").read())
    assert size <= 10240, f"CODELY.md still over hard line: {size}B"
    print(f"fixer2 OK: archive tail rebuilt byte-precise "
          f"(double-CR artifacts {n_double_cr} purged, section order "
          f"header->r109->r342->r359), CODELY.md boilerplate folded "
          f"x{n_boiler} -> {size}B <= 10,240B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
