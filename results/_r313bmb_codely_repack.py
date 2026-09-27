# -*- coding: utf-8 -*-
"""r313 bm-b CODELY hot/cold repack 7th batch: <=10KB hard line
(D-20260925-01(d) + O-20260927-0230 law; r312 6th-batch precedent script
reused with entry-list delta only). Migrate nine aged 2026-09-27 morning
kenglu/adoption lines verbatim (zero line loss) to
research/memory-archive/202609.md 7th batch. Hot layer keeps r306 (used
this round: MM-scan law), r310 (claim-collision law, this-round active),
r312 x3, r313 + Reference."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")

MIGRATE_PREFIXES = (
    "- [2026-09-27 07:4x r308 bm-b] 坑律：autofill tick 的「corrupt autofill_state」ABORT",
    "- [2026-09-27 07:3x r302 bm-a] 坑律：runner 落产物后池 entry 仍 ready",
    "- [2026-09-27 r298 bm-b] 坑律：冻结血统脚本逐轮复制禁手抄重打",
    "- [2026-09-27 05:0x] D-20260927-05③ 采纳",
    "- [2026-09-27 06:07 r302 bm-b] 坑律：wrap/心跳件生成本机钟 ISO 面",
    "- [2026-09-27 07:5x r303 bm-a] 坑律：PowerShell 嵌套单元素数组",
    "- [2026-09-27 08:2x r304 bm-a] 坑律：**Sobol/网格参数解包禁整列 int()**",
    "- [2026-09-27 08:3x r305 bm-a] 坑律：池注册契约第二例",
    "- [2026-09-27 07:2x r301 bm-a] 坑律：池注册契约——ready 批入 runnable_pool",
)


def main():
    codely = open(CODELY, encoding="utf-8").read()
    archive = open(ARCHIVE, encoding="utf-8").read()
    lines = codely.splitlines()
    migrated = []
    for pref in MIGRATE_PREFIXES:
        hits = [l for l in lines if l.startswith(pref)]
        assert len(hits) == 1, f"prefix not unique/found: {pref[:40]}"
        migrated.append(hits[0])
    kept = [l for l in lines if not any(l == m for m in migrated)]
    assert len(kept) == len(lines) - len(migrated)
    new_codely = "\n".join(kept) + "\n"
    batch_header = ("## 坑律归档 2026-09-27 · 归档七批（r313 bm-b 热冷整编·行级 verbatim 零丢失）")
    archive_new = (archive.rstrip("\n") + "\n\n" + batch_header + "\n\n"
                   + "\n".join(migrated) + "\n")
    for m in migrated:
        assert m in archive_new, "zero-loss check failed"
        assert m not in new_codely, "migration left a copy in CODELY"
    assert len(new_codely.encode("utf-8")) <= 10240, (
        f"CODELY {len(new_codely.encode('utf-8'))}B > 10KB hard line")
    tmp = CODELY + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_codely)
    os.replace(tmp, CODELY)
    tmp = ARCHIVE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(archive_new)
    os.replace(tmp, ARCHIVE)
    print(f"migrated {len(migrated)} lines; "
          f"CODELY={len(new_codely.encode('utf-8'))}B <= 10KB OK; "
          f"archive +{len(migrated)} lines")


if __name__ == "__main__":
    main()
