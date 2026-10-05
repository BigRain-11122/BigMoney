# -*- coding: utf-8 -*-
"""r753 bm-a W145 prereg transform MEASUREMENT PASS (r735 law): count every
candidate needle on the freeze-time W144 prereg source (commit ff6d2f918,
NOT the §7/§8-backfilled current blob) + simulate the blanket shift."""
import io
import subprocess

SRC_REF = "ff6d2f918:research/PERPETUAL_N1_W144_PREREG.md"
src = subprocess.run(["git", "show", SRC_REF], capture_output=True,
                     check=True).stdout.decode("utf-8")
assert "## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】" in src, \
    "source must be the freeze-time version (placeholders intact)"
print("source bytes:", len(src.encode("utf-8")), "| lines:", src.count(chr(10)) + 1)

n_w144 = src.count("W144")
n_w143 = src.count("W143")
n_w142 = src.count("W142")
n_w141 = src.count("W141")
print("blanket counts: W144=%d W143=%d W142=%d W141=%d" % (n_w144, n_w143, n_w142, n_w141))
s = src.replace("W144", "W145").replace("W143", "W144").replace("W142", "W143").replace("W141", "W142")

needles = [
    # phase 2a: §5.5 W146+ projection rewrite (BEFORE window replace-alls)
    "W145+ 投影（gate 机证",
    "A first-clean 333_604..335_603 **CLEAN**（hops=0）",
    "B first-clean **333_804..334_003 CLEAN**（hops=0）",
    "同窗互斥先例适用于 W145：W145 冻结方",
    "拒 naive W145 A 窗",
    "verify at W145 prereg",
    "W145+ 投影承接",
    # phase 2b: claim seat
    "r750 席位 MSG-2026-10-06-011x",
    "投影 W145+ A 331_404..333_403 naive",
    # phase 2c: B-window replace-all then fixes
    "331_604..331_603",
    "333_604..333_803",
    "331_604..333_603",
    "B 带 331_404..331_603 **拒**",
    "（r750 W144 gate 尾投影注记所预言）",
    "r750 W144 gate 尾投影 re-derive-MANDATORY",
    "r750 席位",
    # phase 2c-2: history tail
    "W144=bm-a r750 freeze（86d3b070c·表尾）",
    # phase 2d: A-window / continuation / machine-check
    "329_404..331_403",
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
    "2ba4a613f",
    "bm-a r751 6d93bd7ba",
    # phase 2f: ledger/K
    "710,611",
    "n_eff 708,411",
    "312,520",
    "312,520 投影",
    "314,720 投影",
    # phase 2g: §5 keys
    "−0.0928",
    "−0.1049",
    "**0.2450**",
    "**0.3029**",
    "**0.3051**",
    "**1.1788**·line_pre 1.1788",
    "**1.1787**·line_pre 1.1786",
    "se_mu 收窄键",
    "W135..W144 先例",
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
    "同 W140/W141/W142/W143",
    "同 W141/W142/W143",
    "r752 bm-a 冻结窗",
    "（r752 窗口实况）",
    "（r751 窗口实况）",
    # phase 2i: runner
    "n1_w144_results.json",
    "n1_w143_results.json",
    "n1_w144/shard",
    "n1_w145/shard",
    "--wave 144",
    "--wave 145",
    # anchors for prose around the seat push line
    "pre-freeze push plain fast-forward delivery",
    "to origin 2ba4a613f",
    "pushed to origin 2ba4a613f",
    "席位 MSG-2026-10-06-011x-bma-w144-seat",
]
for nd in needles:
    print(f"{s.count(nd):3d}  {nd[:64]}")
# dump key contexts for needle construction
for marker in ["r752 席位", "席位 MSG", "W145+ 投影（gate", "阶梯第三例",
               "r750 席位", "bm-a r751", "net chain head", "链头",
               "第 134", "134 波", "59+本候选", "141 行", "133+本候选"]:
    j = s.find(marker)
    print(f"---- ctx @ {marker!r} (count={s.count(marker)}) ----")
    print(repr(s[max(0, j - 100):j + 300]) if j >= 0 else "ABSENT")
