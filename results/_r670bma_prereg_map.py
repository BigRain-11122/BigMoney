# r670 bm-a: locate prereg sec.7/sec.8 backfill anchors (file output, GBK console bypass)
import re, io

src = open("research/THEME_JUDGE_P1.md", encoding="utf-8").read()
with open("results/_r670bma_prereg_map.txt", "w", encoding="utf-8") as fh:
    fh.write(f"file chars: {len(src)}\n")
    for m in re.finditer(r"^#+\s*[^\n]*$", src, re.M):
        fh.write(f"{m.start():7d}  {m.group(0)[:100]}\n")
    fh.write("--- tail 600 chars ---\n")
    fh.write(src[-600:])
print("map written")
