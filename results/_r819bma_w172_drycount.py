# -*- coding: utf-8 -*-
"""r819 W172 prereg build -- dry analysis pass: apply the planned composite
consumptions on the W171 source and count the REMAINING generic faces, so
the build script's EXPECT table can be machine-derived (not hand-counted).
Zero-write: prints counts only."""
import io
import re

SRC = r"results\_r819bma_w172_prereg_src.txt"
src = io.open(SRC, encoding="utf-8").read()

COMPOSITES = [
    # (name, needle) -- needles byte-exact from the freeze-time W171 blob
    ("TITLE", "# PERPETUAL-N1-W171 预注册 · N1 nulls-deepening 泵第 169 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 160+本候选=bm-a 第八十七枚自有波【r815】）"),
    ("WAVEFREE", "波号 171=注册表 W170 行后首个自由号"),
    ("VAC", "（r814 probe leg2/leg3 实跑）"),
    ("MERGE", "（r814 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）"),
    ("WAVECLI", "--wave 171/finalize --wave 171"),
    ("EOB", "engine_owner==bm-a 86 行注册"),
    ("V2W", "v2..W170 落地"),
    ("W136TO", "W136..W170"),
    ("S51B", "（W2..W170 共一百六十九面实测 mu 稳定先例·单波跨键微）"),
    ("OWNCHAIN", "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波"),
    ("SCANFACE", "扫描面=pre-W171 全一百六十八行注册 N1 带表（表尾 W170 行·leg0 机证 168 行）"),
    ("R250", "R250：W171 带从未指派·测量面零结果可锁"),
    ("PRC", "results/_r814bma_w171_probe_receipt.json"),
    ("KLCHAIN_HEAD", "W118=bm-b r678 freeze"),
]

out = src
for name, needle in COMPOSITES:
    n = out.count(needle)
    print(f"COMPOSITE {name}: count={n}")
    assert n >= 1, (name, n)
    out = out.replace(needle, "@" + name + "@")

# remaining generic token counts
for t in ["W172", "W171", "W170", "W169", "W2..W170", "W1..W170", "W5..W170",
          "n1_w171", "n1_w170", "n1w171", "PERPETUAL_N1_W171_PREREG.md",
          "PERPETUAL-N1-W171", "371,920", "374,120", "779,412", "777,212",
          "171", "170", "169", "172", "168",
          "391_004", "393_004", "391_003", "393_003", "393_204", "395_204",
          "r814", "r813", "r812", "r815", "3290e586b",
          "MSG-2026-10-07-0843", "bma-w171-seat",
          "W171+ 投影", "W172+ 投影",
          "1.184", "1.1841", "0.245153", "0.2931", "−0.0927", "−0.0928",
          "0.000402", "0.000403"]:
    print(f"REMAIN {t!r}: {out.count(t)}")
