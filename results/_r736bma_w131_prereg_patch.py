# -*- coding: utf-8 -*-
"""r736 W131 prereg residue patch: 9 measured residues from the full
wave-mention audit (fail-fast needle asserts)."""
import io

P = "research/PERPETUAL_N1_W131_PREREG.md"
t = io.open(P, encoding="utf-8").read()

def rep(t, pairs):
    for old, new, expect in pairs:
        n = t.count(old)
        assert n == expect, "needle count=%d expect=%d: %r" % (n, expect, old[:60])
        t = t.replace(old, new)
    return t

t = rep(t, [
    ("批名=**PERPETUAL-N1-W130**", "批名=**PERPETUAL-N1-W131**", 1),
    ("-prereg research/PERPETUAL_N1_W130_PREREG.md`", "-prereg research/PERPETUAL_N1_W131_PREREG.md`", 1),
    ("扫描面=pre-W130 全一百二十七行注册 N1 带表（表尾=W129 行·leg0 机证 127 行）",
     "扫描面=pre-W131 全一百二十八行注册 N1 带表（表尾=W130 行·leg0 机证 128 行）", 1),
    ("（W2..W129 落地 runner 的 wave 参数化复用", "（W2..W130 落地 runner 的 wave 参数化复用", 1),
    ("（p2_calibration v1/v2 canon；W1 ext；W2..W129 落地）", "（p2_calibration v1/v2 canon；W1 ext；W2..W130 落地）", 1),
    ("防证伪模式词面自害，W2..W129 同法先例", "防证伪模式词面自害，W2..W130 同法先例", 1),
    ("本波设计=W2..W129 逐字复用", "本波设计=W2..W130 逐字复用", 1),
    ("R250：W130 带从未指派", "R250：W131 带从未指派", 1),
    ("读活树自见 W130 行并点火", "读活树自见 W131 行并点火", 1),
])

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("9 residues patched; len=%d" % len(t))
