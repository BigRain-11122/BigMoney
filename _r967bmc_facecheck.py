# -*- coding: utf-8 -*-
import subprocess, re, sys
sys.stdout.reconfigure(encoding="utf-8")
t = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C",
                   r"K:\Fluxgroup\FluxGroup\quant\bigmoney", "show",
                   "aebe0a5ac:research/PERPETUAL_N1_W231_PREREG.md"],
                  capture_output=True).stdout.decode("utf-8")
pats = ["W230-only 实测", "A 面算术继续带", "第 229 枚", "engine_owner 行 220",
        "W230 合并池实测", "实差 0.0019", "（523_003+1）", "（525_003+1）",
        "W229 块的 W228 leg", "W231 块 parity", "K-lift **", "自注册 W230 A 尾",
        "W136..W230 先例链披露", "MSG-20261013-1155", "r963 窗 11:5x",
        "2026-10-13 10:3x", "se_mu 收窄链"]
for pat in pats:
    m = re.search(re.escape(pat), t)
    if m:
        print(">>", pat, "::", t[max(0, m.start()-70):m.end()+90].replace("\n", " | ")[:260])
    else:
        print(">>", pat, ":: NOT FOUND")
