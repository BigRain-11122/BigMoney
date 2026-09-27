"""R351 bm-a CODELY in-window hot-cold archival (27th batch, <=10KB hard line law).

Post-fold CODELY.md = 10,354B > 10,240B hard line (集团令 O-20260927-0230: append 后超线=当窗即办).
Move 2 oldest full-text pitlaw rows (r96/r99 bm-c) VERBATIM to archive 202609.md
『坑律归档 2026-09-27 二十七批』section; replace with compact pointer rows.
Line-level zero-loss asserts: (a) each moved row byte-identical present in archive after
append; (b) new CODELY size <= 10,240B; (c) all other rows untouched byte-identical.
"""
import io

CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

def rd(p):
    return open(p, "rb").read()

def main():
    cB = rd(CODELY)
    aB = rd(ARCH)
    lines = cB.decode("utf-8").split("\n")

    # locate the two rows by unique prefixes
    def find(prefix):
        for i, l in enumerate(lines):
            if l.startswith(prefix):
                return i
        raise SystemExit(f"row not found: {prefix!r}")

    i96 = find("- [2026-09-27 2026-09-27 18:35 r96 bm-c]")
    i99 = find("- [2026-09-27 19:4x r99 bm-c]")
    row96, row99 = lines[i96], lines[i99]

    ptr96 = "- [r96 bm-c] 坑律（二十七批外迁·指针）：机钟步回拨窗内收尾件复用轮中取时串=同件双时间源互矛（epoch vs clock_read 同件互矛=步回拨指纹；正典=收尾时间戳写入时现取、epoch 与 clock_read 同次取时派生、对外留痕以 git %ci 为锚）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十七批』节。"
    ptr99 = "- [r99 bm-c] 坑律（二十七批外迁·指针）：git 数据面双死窗处置三径（fetch/push 双卡死时：①远端对象已落库=rebase 零网络手术 ②push 走 Git Data API 直构〔base64 blob+base_tree+refs POST〕③tick-lane 漂移=在途态留树勿强并；连带 HEAD^{tree} 裸写 PS 展开坑必加引号）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十七批』节。"

    section = "\n## 坑律归档 2026-09-27 二十七批（r351 bm-a·fold-landing 当窗超线整编·行级零丢失）\n\n" + row96 + "\n" + row99 + "\n"

    # append to archive (LF face, ends with newline)
    assert aB.endswith(b"\n")
    new_a = aB + section.encode("utf-8")
    # (a) zero-loss: moved rows verbatim present in archive
    assert row96.encode("utf-8") in new_a, "r96 row lost"
    assert row99.encode("utf-8") in new_a, "r99 row lost"
    with open(ARCH, "wb") as f:
        f.write(new_a)

    # replace rows in CODELY
    lines[i96] = ptr96
    lines[i99] = ptr99
    new_c = "\n".join(lines)
    # (b) size gate
    nb = len(new_c.encode("utf-8"))
    assert nb <= 10240, f"still over hard line: {nb}B"
    with open(CODELY, "wb") as f:
        f.write(new_c.encode("utf-8"))

    # (c) all other rows untouched: every other line still present
    old_set = set(l for i, l in enumerate(cB.decode('utf-8').split('\n')) if i not in (i96, i99))
    new_list = set(new_c.split("\n"))
    missing = [l for l in old_set if l not in new_list]
    assert not missing, f"rows lost from CODELY: {missing[:2]}"
    print(f"archived 2 rows verbatim ({len(row96.encode('utf-8'))}B + {len(row99.encode('utf-8'))}B) -> 27th batch; CODELY {len(cB)}B -> {nb}B (<=10240 OK); archive +{len(section.encode('utf-8'))}B")

if __name__ == "__main__":
    main()
