# -*- coding: utf-8 -*-
"""r753 W145 prereg xform MEASUREMENT (2-key blanket per r752 bloodline:
W144->W145 own + W143->W144 prior; W142/W141 = historical precedent refs,
NOT blanket-shifted)."""
import io
import subprocess

SRC_REF = "ff6d2f918:research/PERPETUAL_N1_W144_PREREG.md"
src = subprocess.run(["git", "show", SRC_REF], capture_output=True,
                    check=True).stdout.decode("utf-8")
n_w144 = src.count("W144")
n_w143 = src.count("W143")
s = src.replace("W144", "W145").replace("W143", "W144")
print("blanket: W144=%d -> W145, W143=%d -> W144 (2-key)" % (n_w144, n_w143))

needles = [
    # phase 2a: §5.5 W146+ projection rewrite
    "W145+ 投影（gate 机证",
    "A first-clean 333_604..335_603 **CLEAN**（hops=0）",
    "B first-clean **333_804..334_003 CLEAN**（hops=0）",
    "W141 同窗互斥先例适用于 W145：W145 冻结方",
    "拒 naive W145 A 窗",
    "verify at W145 prereg",
    "W145+ 投影承接",
    "W145 A 重 derive 同强制",
    # phase 2b: claim seat
    "r750 席位 MSG-2026-10-06-002x",
    "投影 W145+ A 331_404..333_403 naive",
    # phase 2c: own-B replace-all then prior-B
    "333_604..333_803",
    "331_404..331_603",
    "B 带 331_404..331_603 **拒**",
    "（r750 W144 gate 尾投影注记所预言）",
    "r750 W144 gate 尾投影 re-derive-MANDATORY",
    "r750 席位",
    # phase 2c-2: history tail
    "W144=bm-a r750 freeze（86d3b070c·表尾）",
    # phase 2d: A-window / continuation / machine-check
    "331_604..333_603",
    "331_404..333_403",
    "331_604..331_803",
    "（331_603+1）机检关系",
    "（333_603+1）机检关系",
    "seed=**331_604+j**",
    "entry rng=**331_604+j**",
    "exit rng=**333_604+j**",
    "阶梯第三例",
    # phase 2e: seat/probe/receipt
    "_r752bma_w144_band_gate.py",
    "_r751bma_w144_probe_receipt.json",
    "_r751bma_w144_probe.py",
    "MSG-2026-10-06-011x-bma-w144-seat",
    "plain fast-forward delivery 送达 **2ba4a613f**（零 UU·零竞态·零 --no-verify·干净快进）",
    "已推 origin 2ba4a613f 先于本冻结【r565 律·推送窗=plain fast-forward delivery·behind 0 at fetch·零 UU·零 --no-verify】",
    "先推 origin 2ba4a613f r565 律",
    "bm-a r751 6d93bd7ba",
    # phase 2f: ledger/K
    "710,611",
    "n_eff 708,411",
    "312,520",
    "314,720 投影",
    # phase 2g: §5 keys
    "−0.0928",
    "−0.0958",
    "**0.2450**",
    "**0.3051**",
    "**1.1787**·line_pre 1.1786",
    "W136..W144 先例",
    "W136 +0.0000/W137",
    "W144 **+0.0001** 如实披露",
    "键 W144 实测 K-lift **+0.0001**",
    "se_mu 收窄键 W139 0.000444→W140 0.000443→W141 0.000441→W142 0.000440→W144 **0.000438**",
    "共一百四十二面",
    # phase 2h: ordinals
    "泵第 142 枚",
    "行 133+本候选",
    "第六十枚",
    "【r752】",
    "第一百三十四引擎波",
    "引擎线第 134 波",
    "行 59+本候选",
    "59 行注册",
    "全一百四十一行",
    "leg0 机证 141 行",
    "同 W140/W141/W142/W144",
    "r752 bm-a 冻结窗",
    "（r751 窗口实况）",
    # phase 2i: runner
    "n1_w144_results.json",
    "n1_w143_results.json",
    "n1_w144/shard",
    "--wave 144",
]
for nd in needles:
    print(f"{s.count(nd):3d}  {nd[:70]}")
