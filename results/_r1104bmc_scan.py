# -*- coding: utf-8 -*-
# r1104 bm-c: span-text scan for the W274 derive builder (read-only evidence gathering).
import io
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
S = io.open(REPO + r"\results\_w273bmc_prereg_derive.py", encoding="utf-8", newline="").read()
print("=== ordinal faces:")
for k in ["第二十二次连续 A-hop", "第二十三次连续 A-hop", "第二十一次连续 A-hop",
          "第二十三次连续 above-own-A", "第二十二次连续 above-own-A",
          "〔第二十二次连续〕", "〔第二十三次连续〕", "连续二十二波", "连续二十一波",
          "共二百七十一面", "共二百七十面", "TWENTY-SECOND consecutive A-hop",
          "TWENTY-THIRD consecutive above-own-A", "TWENTY-THIRD consecutive A-hop",
          "TWENTY-FOURTH consecutive A-hop"]:
    print(" ", k, S.count(k))
print("=== RAM/estate/engine faces:")
for k in ["本窗 free RAM ~0.3GB", "本窗 free RAM ~1.4GB", "estate chain r1099/r1100",
          "wave-3 收官烧批在飞", "i2v wave-1 烧批在飞", "CLEAN-AT-BIRTH 5th gen",
          "CLEAN-AT-BIRTH 6th gen", "~0.3G bm-c 实锚", "~1.4G bm-c 实锚",
          "35th consecutive", "36th consecutive", "setwave root-cure", "surgery-delivered"]:
    print(" ", k, S.count(k))
print("=== gate compound faces:")
for k in ['"line_pre_w272"], 4) == 1.1965', '"line_merged_596320"], 4) == 1.1965',
          "== 0.0,", "se_mu_at_k596320", "se_mu_at_k594120", '"w272_finalize_landed"',
          '"w272_finalize_anchors"', "w272_finalize", "key1_w272_vs", "行 261 注册在册",
          "行 262 注册在册", "617_901+j", "615_901+j", "_r1100bmc_w272_fivekeys.json",
          "_w273bmc_20261018", "1.1965", "1.1966", "1.1967", "1.1964"]:
    print(" ", k, S.count(k))
print("=== RAM POST_LEG tuple verbatim:")
i = S.find('("本窗 free RAM ~1.4GB')
print(repr(S[i:i + 1500]))
print("=== estate line:")
i = S.find("estate chain")
print(repr(S[i - 100:i + 220]))
print("=== header (10):")
i = S.find("(10) RAM face")
print(repr(S[i - 30:i + 480]))
print("=== header (1) stamp disclosure:")
i = S.find("(1) finalize-window stamp roll")
print(repr(S[i - 30:i + 420]))
print("=== b5 wave-list line:")
i = S.find("W251 起 staircase")
print(repr(S[i - 30:i + 520]))
print("=== header title line:")
print(repr(S[:200]))
print("=== probe receipt load + leg4 gate:")
i = S.find("W274p_A_naive")
print(repr(S[i - 200:i + 300]))
