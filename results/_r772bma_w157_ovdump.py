# -*- coding: utf-8 -*-
# r772 bm-a: dump the pairs156 NEW sides targeted for W157 overrides (verbatim extract, r745 law)
import io

R769 = "results/_r769bma_w156_prereg_xform.py"
src769 = io.open(R769, encoding="utf-8").read()
cut = src769.find("\n# --- sec7/sec8 span replacement")
assert cut > 0
ns = {}
exec(compile(src769[:cut], R769, "exec"), ns)
pairs156 = ns["pairs156"] if "pairs156" in ns else ns["pairs"]

MARKERS = [
    ("DAIWEI", "席位 leg4+r768 gate leg3"),
    ("FREEZELIST", "W152=bm-a r764 freeze"),
    ("SEATNARR", "全 inbox/processed/ W156 席位零外机命中"),
    ("PUSHREC", "席位推送窗实录"),
    ("KLIFT", "K-lift 线移动幅度"),
    ("S0ROW", "引擎线第 146 波"),
    ("S6ROW", "71 行注册 + 本候选"),
    ("S0CLAIM", "投影 W157+ A 357_804"),
    ("SS55", "W157+ 投影（gate 机证"),
    ("S3A", "entry rng seed=**358_004+j**"),
    ("S3B", "exit rng=**360_004+j**"),
]
for tag, m in MARKERS:
    hits = [i for i, (o, n) in enumerate(pairs156) if m in n]
    live = io.open(r"research/PERPETUAL_N1_W156_PREREG.md", encoding="utf-8").read()
    for i in hits:
        o, n = pairs156[i]
        print(f"===== [{tag}] pair#{i} NEW side ({len(n)} chars) =====")
        print(n)
        print(f"===== live count of NEW side: {live.count(n)} =====")
        print()
