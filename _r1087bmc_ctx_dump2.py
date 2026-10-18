# -*- coding: utf-8 -*-
# _r1087bmc_ctx_dump2.py - supplementary needle verification for the W267
# derive authoring (block classification + zero-floor checks). Read-only.
import io, re

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w267bmc_w266_frozen_face.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

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
    i = T0.index(sm); j = T0.find(em, i) + len(em)
    spans.append((name, i, j))

def cls(pos):
    for name, i, j in spans:
        if i <= pos < j: return name
    return "NON-BLOCK"

print("== simple counts ==")
for n in ("席位时即解锁", "seed_admit_gate rc0 双带 FREE", "（W265 注册+烧录+finalize 全落地）",
          "注册+烧录+finalize 全落地", "MSG-20261018-1025", "942ebd5885",
          "\u22120.09273858", "0.24507392", "\u22120.09878527", "0.3268",
          "604_701..606_700", "604_901..605_100", "578,720", "1,005,135",
          "W266p_", "W265p_", "queue_depth", "GATED on", "finalize PENDING",
          "W136..W265", "W2..W265", "W136..W264", "W2..W264",
          "e57215a2c", "a47517f792", "93298b7e33", "c72805837c", "2e622ee447",
          "（nvidia-smi 实读 3%·3.2G VRAM 常驻", "第十七次连续 above-own-A"):
    print("%04d | %s" % (T0.count(n), n))

print("== classification of band/sha instances ==")
for needle in ("600_501..602_500", "602_501..602_700", "e57215a2c", "a47517f792",
               "93298b7e33", "c72805837c", "2e622ee447", "席位时即解锁",
               "seed_admit_gate rc0 双带 FREE", "注册+烧录+finalize 全落地"):
    counts = {}
    for m in re.finditer(re.escape(needle), T0):
        c = cls(m.start()); counts[c] = counts.get(c, 0) + 1
    print("%s -> %s" % (needle, counts))
