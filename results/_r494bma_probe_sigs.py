# -*- coding: utf-8 -*-
"""r494 bm-a probe: science_gates DSR/t/bootstrap signatures (throwaway)."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = open("scripts/science_gates.py", encoding="utf-8").read()
for fn in ["def deflated_sharpe_ratio", "def dsr_from_stats",
           "def t_from_sharpe", "def bootstrap_ci_sharpe"]:
    i = src.find(fn)
    j = src.find("\ndef ", i + 10)
    body = src[i:j]
    k = body.find('"""')
    sig_end = body.find("):") + 2
    print(body[:sig_end])
    if k > 0:
        print("   doc:", body[k + 3:k + 300].split('"""')[0][:220])
    print("----")
