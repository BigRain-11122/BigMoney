# -*- coding: utf-8 -*-
# _r1087bmc_ctx_dump.py - dump every W267 / 07:0x / W254 occurrence in the
# W266 frozen face with context (UTF-8 proper), and classify block-interior
# vs non-block using the eight block markers (read-only diagnostic).
import io, re

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w267bmc_w266_frozen_face.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

# block spans per the W267 derive plan (markers on T0; same as W266 family)
BLOCKS = [
    ("b_title", "engine_owner 行 255 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**600_501+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**602_501+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W267+ 投影 A naive 602_501..604_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W267+ 投影（probe 机证 leg4", "verify at W267 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]
spans = []
for name, sm, em in BLOCKS:
    c = T0.count(sm)
    i = T0.index(sm)
    j = T0.find(em, i) + len(em)
    spans.append((name, i, j))
    print("BLOCK %s: count(start)=%d span=%d..%d len=%d" % (name, c, i, j, j - i))

def in_block(pos):
    for name, i, j in spans:
        if i <= pos < j:
            return name
    return "NON-BLOCK"

for needle in ("W267", "07:0x", "W254", "第 85 枚", "W265 finalize one-pass"):
    print("==== %s ====" % needle)
    for m in re.finditer(re.escape(needle), T0):
        a = max(0, m.start() - 55)
        b = min(len(T0), m.end() + 55)
        ctx = T0[a:b].replace("\n", "|")
        print("[%s] ...%s..." % (in_block(m.start()), ctx))
