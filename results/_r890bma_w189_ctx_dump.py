# -*- coding: utf-8 -*-
"""r890 bm-a: dump src context of the live session stamps + corrected scanface
old sides, to pin S86 pair semantics before writing the buildgen."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results/_r890bma_w189_prereg_src.txt", encoding="utf-8").read()

for needle in ("（r888 承袭", "r887 seat push", "自 r887 收口", "bm-a r887 窗自移",
               "本机 r887 席位", "（r887 seat push·r565 律）", "（r885 冻结件）",
               "r885 probe leg4"):
    k = src.find(needle)
    print("=== %s (count %d) ===" % (needle, src.count(needle)))
    print(repr(src[max(0, k - 90):k + 130]))
    print()

for old in ("一百八十五行注册", "机证 185 行", "表尾 W187 行", "r886",
            "第五十例", "engine_owner 行 177", "第一百零三枚"):
    print("%3d  %s" % (src.count(old), old))
