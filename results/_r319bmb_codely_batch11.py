"""R319 bm-b: CODELY.md hot-cold reorg batch-11 (10KB hardline, in-window law).

Moves four pit-law entries verbatim (line-level zero-loss, asserted) from
repo-root CODELY.md Project section to research/memory-archive/202609.md as
『十一批外迁』section; leaves a one-line batch index in the Reference
section. Keeps r317/r318/r319 recent entries in-file.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODELY = ROOT / "CODELY.md"
ARCHIVE = ROOT / "research" / "memory-archive" / "202609.md"

MOVE_PREFIXES = [
    "- [2026-09-27 10:5x r316 bm-b] 坑律：**TTS mastered 链 crest 物理律三面",
    "- [2026-09-27 11:1x r76 bm-c] 坑律：**门控批 selftest",
    "- [2026-09-27 11:5x r78 bm-c] 坑律：**冻结面测量批的 rail 输入",
    "- [2026-09-27 11:5x r78 bm-c] 坑律补遗：**PS Add-Content 长中文串",
]
INDEX_LINE = (
    "十一批外迁（r319 bm-b·水位律当窗整编）：r316 TTS crest 物理律三面/r76 bm-c "
    "门控批 selftest happy-path 双例律/r78 bm-c 冻结面 rail 输入钉 commit blob/"
    "r78 bm-c PS Add-Content 粘尾补遗=归档十一批节·行级零丢失。"
)
SECTION_HEADER = "\n\n## 十一批外迁（r319 bm-b·2026-09-27 热冷整编·行级零丢失）\n"


def main():
    src = CODELY.read_text(encoding="utf-8")
    lines = src.split("\n")
    moved, kept = [], []
    for ln in lines:
        if any(ln.startswith(p) for p in MOVE_PREFIXES):
            moved.append(ln)
        else:
            kept.append(ln)
    assert len(moved) == 4, f"expected 4 entries, got {len(moved)}"
    # verbatim zero-loss: each moved line byte-equal in archive after write
    arch = ARCHIVE.read_text(encoding="utf-8")
    if "十一批外迁（r319 bm-b" not in arch:
        block = SECTION_HEADER + "\n".join(moved) + "\n"
        ARCHIVE.write_text(arch.rstrip("\n") + block, encoding="utf-8")
    arch2 = ARCHIVE.read_text(encoding="utf-8")
    for m in moved:
        assert m in arch2, f"zero-loss violation: entry missing in archive: {m[:50]}"
        assert (arch2.count(m) == 1), f"archive dup: {m[:50]}"
    # splice index line after the 十批 index line in Reference section
    out = "\n".join(kept)
    m = re.search(r"十批外迁（r78 bm-c）：[^\n]*\n", out)
    assert m, "十批 index anchor not found"
    out = out[:m.end()] + INDEX_LINE + "\n" + out[m.end():]
    CODELY.write_text(out, encoding="utf-8")
    # final gates
    final = CODELY.read_text(encoding="utf-8")
    for p in MOVE_PREFIXES:
        assert p not in final, f"source still holds moved entry: {p[:40]}"
    size = CODELY.stat().st_size
    print(f"moved 4 entries verbatim; archive batch-11 appended; "
          f"CODELY.md now {size/1024:.2f}KB (hardline 10KB)")
    assert size < 10 * 1024, "still over hardline"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
