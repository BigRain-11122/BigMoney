# -*- coding: utf-8 -*-
"""W213 prereg builder (bm-c loop r908 freeze window, 2026-10-12 03:4x).
Buildgen-face law (r830 E41 / r773 / r781 / r909): every OLD string below is a
physical fragment asserted count==1 against the W212 prereg bytes on disk --
zero visual transcription is trusted; any mismatch = LOUD abort, re-probe.
All NEW facts machine-derived this window (probe receipt
results/_w213bmc_20261012_probe_receipt.json + n1_w212_results.json finalize
fields + saturation_engine live status + seat push 4f3b0d6a8)."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "PERPETUAL_N1_W212_PREREG.md")
DST = os.path.join(ROOT, "research", "PERPETUAL_N1_W213_PREREG.md")
PROBE = os.path.join(ROOT, "results", "_w213bmc_20261012_probe_receipt.json")
W212 = os.path.join(ROOT, "results", "perpetual_faces", "n1_w212_results.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
b = open(SRC, "rb").read()
t = b.decode("utf-8")
eol = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"

rec = json.load(open(PROBE, encoding="utf-8"))
w212 = json.load(open(W212, encoding="utf-8"))
A = rec["bands"]["A"].split("_"); B = rec["bands"]["B"].split("_")
a_lo, a_hi = int(A[0]), int(A[1]); b_lo, b_hi = int(B[0]), int(B[1])
assert (a_lo, a_hi, b_lo, b_hi) == (483_404, 485_403, 485_404, 485_603), rec["bands"]
merged = w212["null_pool_cumulative"]["merged"]
wonly = w212["null_pool_cumulative"]["w212_only"]
skill = w212["skill_line_v2_k_lift"]
famA = w212["families"]["A_random_engine_exit"]
led = w212["science_gates"]["ledger"]
assert led["total"] == 890_189 and merged["n_values"] == 464_320
mu8 = f"\u2212{abs(merged['mu']):.8f}"          # -0.09267005 (U+2212 display form, r833 law)
wo8 = f"\u2212{abs(wonly['mu']):.8f}"          # -0.08721705
sig8 = f"{merged['sigma']:.8f}"                # 0.24512048
assert mu8 == "\u22120.09267005" and wo8 == "\u22120.08721705" and sig8 == "0.24512048"

REP = [
 # A. title pump ordinal + batch name
 ("PERPETUAL-N1-W212 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 210 \u679a",
  "PERPETUAL-N1-W213 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 211 \u679a", 1),
 # A2. §0 batch name (source has 4 PERPETUAL-N1-W212 sites: title/批名/vacancy/ledger)
 ("\u6279\u540d=**PERPETUAL-N1-W212**", "\u6279\u540d=**PERPETUAL-N1-W213**", 1),
 # A3. §0.5 banned gate command path (source has 2 PERPETUAL_N1_W212_PREREG sites: vacancy + gate cmd)
 ("--prereg research/PERPETUAL_N1_W212_PREREG.md", "--prereg research/PERPETUAL_N1_W213_PREREG.md", 1),
 # B. title ordinal faces
 ("engine_owner \u884c 201 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W211 \u884c\u00b7probe leg0 \u673a\u8bc1 197+W208+W209+W210+W211 \u6ce8\u5165\uff09+\u672c\u5019\u9009=bm-c \u7b2c\u56db\u5341\u4e8c\u679a\u81ea\u6709\u6ce2",
  "engine_owner \u884c 202 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W212 \u884c\u00b7probe leg0 \u673a\u8bc1 210 \u884c live \u5355\u6001\u96f6\u6ce8\u5165\u817f\uff09+\u672c\u5019\u9009=bm-c \u7b2c\u56db\u5341\u4e09\u679a\u81ea\u6709\u6ce2", 1),
 # C. title live-derive face
 ("\u5e2d\u9762 prose 41st=seat-time face\uff08r859 \u7a97 W209/W210 \u672a\u6ce8\u518c\u8ba1 attempt-continuity\u00b7r846 \u4e2d\u65ad W208 \u7a3f\u5360\u7528\u7b2c 38 \u69fd\u4f4d\uff09\u00b7W210 r898 takeover \u5f52 bm-c +1 shift\u2192freeze \u65f6 live derive bm-c rows 41+\u5019\u9009=\u7b2c 42 \u679a EXACT",
  "\u5e2d\u9762 prose 42nd=seat-time face\uff08r908 \u7a97 W212 \u6ce8\u518c\u540e live derive\u00b7r906 freeze receipt 42nd owned \u627f\u88ad\uff09\u2192freeze \u65f6 live derive bm-c rows 42+\u5019\u9009=\u7b2c 43 \u679a EXACT", 1),
 # D. title freeze window stamp
 ("\u3010bm-c \u5faa\u73af\u73ed r906 freeze \u7a97\u00b72026-10-12 02:5x\u00b7CEO \u586b\u8f7d\u4ee4",
  "\u3010bm-c \u5faa\u73af\u73ed r908 freeze \u7a97\u00b72026-10-12 03:4x\u00b7CEO \u586b\u8f7d\u4ee4", 1),
 # E. 令源 wave-number vacancy head
 ("**\u6ce2\u53f7 212=\u6ce8\u518c\u8868 W211 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r859 \u7a97\u5b9e\u8dd1\uff1aorigin",
  "**\u6ce2\u53f7 213=\u6ce8\u518c\u8868 W212 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r908 \u7a97\u5b9e\u8dd1\uff1aorigin", 1),
 # E2. vacancy four-check tail
 ("\u96f6 W212 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 212 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W212 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W212_PREREG.md \u56db\u67e5",
  "\u96f6 W213 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 213 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W213 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W213_PREREG.md \u56db\u67e5", 1),
 # H. upstream chain: append W212 finalize landed + roll chain head
 ("\u00b7n1_w211_results.json\u00b701:39:51\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W211 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**",
  "\u00b7n1_w211_results.json\u00b701:39:51\uff09+W212=bm-c r906 \u4e94\u9762\u51bb\u7ed3\uff080f30cb725\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r907 finalize one-pass \u5df2\u843d\uff08K=464,320\u00b7\u8d26\u672c\u5934 890,189 \u673a\u8bfb\u00b7n1_w212_results.json\u00b703:3x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W212 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**", 1),
 # I. seat MSG publication (line-3 face)
 ("\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261011-0732-bmc-w212-seat \u5df2\u63a8 origin dace861b1 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r859 \u7a97\u3011",
  "\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261012-0342-bmc-w213-seat \u5df2\u63a8 origin 4f3b0d6a8 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r908 \u7a97\u3011", 1),
 # J. downstream projection pointer + single-state roll
 ("\u4e0b\u6e38 W213+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W213 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W211 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb",
  "\u4e0b\u6e38 W214+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W214 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W212 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb", 1),
 # K. 带位 ADMIT receipt path
 ("ADMIT \u56de\u6267=results/_w212bmc_20261011_probe_receipt.json \u4e94\u817f\u5355\u7a97",
  "ADMIT \u56de\u6267=results/_w213bmc_20261012_probe_receipt.json \u4e94\u817f\u5355\u7a97", 1),
 # L. A band prose (whole compound, r773 law)
 ("\u672c\u6ce2 **A-ext seed=481_204..483_203**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e8c\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 481_004..483_003\uff08\u81ea\u58f0\u660e W211 A \u5c3e 481_003 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W211 \u58f0\u660e B \u5e26 481_004..481_203 **\u62d2**\uff08W211 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **481_204..483_203**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08481_203+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e03\u5341\u4e8c\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=SEVENTY-SECOND\uff08\u7b2c\u4e03\u5341\u4e8c\u4f8b\uff09",
  "\u672c\u6ce2 **A-ext seed=483_404..485_403**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e09\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 483_204..485_203\uff08\u81ea\u6ce8\u518c W212 A \u5c3e 483_203 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W212 \u6ce8\u518c B \u5e26 483_204..483_403 **\u62d2**\uff08W212 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **483_404..485_403**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08483_403+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e03\u5341\u4e09\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=SEVENTY-THIRD\uff08\u7b2c\u4e03\u5341\u4e09\u4f8b\uff09", 1),
 # M. B band prose (whole compound)
 ("**B-ext exit seed=483_204..483_403**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 481_204..481_403 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 481_204..483_203 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **483_204..483_403**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08483_203+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W211 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W212 \u987b\u5728 post-W211 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97",
  "**B-ext exit seed=485_404..485_603**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 483_404..483_603 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 483_404..485_403 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **485_404..485_603**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08485_403+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W212 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W213 \u987b\u5728 post-W212 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97", 1),
 # N. R250
 ("R250\uff1aW212 \u5e26\u4ece\u672a\u6307\u6d3e", "R250\uff1aW213 \u5e26\u4ece\u672a\u6307\u6d3e", 1),
 # O. seed_admit lines (whole compound)
 ("A base=481204 span=2000 checked=2000 verdict=FREE / B base=483204 span=200 checked=200 verdict=FREE",
  "A base=483404 span=2000 checked=2000 verdict=FREE / B base=485404 span=200 checked=200 verdict=FREE", 1),
 # P. scan face
 ("\u626b\u63cf\u9762=pre-W212 \u5168\u4e8c\u767e\u96f6\u4e5d\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W211 \u884c\u00b7probe leg0 \u673a\u8bc1\u6ce8\u5165\u540e owner rows 201\uff09",
  "\u626b\u63cf\u9762=pre-W213 \u5168\u4e8c\u767e\u4e00\u5341\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W212 \u884c\u00b7probe leg0 \u673a\u8bc1 210 \u884c live \u5355\u6001 owner rows 202\uff09", 1),
 # Q. 复用域 runner span
 ("\uff08W2..W211 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528", "\uff08W2..W212 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528", 1),
 # Q2. §0.5 upstream span
 ("v1 ext\uff1bv2..W211 \u843d\u5730\uff09\u7684\u79cd\u5b50\u5e26\u6269\u5c55\u91cd\u6d4b", "v1 ext\uff1bv2..W212 \u843d\u5730\uff09\u7684\u79cd\u5b50\u5e26\u6269\u5c55\u91cd\u6d4b", 1),
 # R. freeze bundle note (复用域段) — physical face uses U+3014/U+3015 tortoise brackets
 ("selftest W212 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**\u672c\u4ef6\u4e0e results/_w212bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w211bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W211 \u884c+W211 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W211 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r848/W209 \u5148\u4f8b freeze-prep \u540c\u5f0f",
  "selftest W213 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**\u672c\u4ef6\u4e0e results/_w213bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w212bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W212 \u884c+W212 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W212 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r906/W212 \u5148\u4f8b freeze-prep \u540c\u5f0f", 1),
 # S. §0 upstream anchor
 ("**W1..W211 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **887,989**\u00b7K=462,120 \u5408\u5e76\u6c60\u00b7n1_w211_results.json \u673a\u8bfb\u00b7W211 finalize one-pass bm-c r904/r905 \u4fee\u590d\u7a97\u540e 01:39:51\u00b7r902 unfuse+r904 reburn 12/12 \u4fee\u590d\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff08transient mid-surgery SyntaxError fuse\u2192unfuse\u2192fresh 3-fuse budget\u2192reburn\u00b7W211 \u9762\u81ea\u8eab\u5b8c\u6574\u6027\u5df2\u7531 12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\uff09\u3011",
  "**W1..W212 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **890,189**\u00b7K=464,320 \u5408\u5e76\u6c60\u00b7n1_w212_results.json \u673a\u8bfb\u00b7W212 finalize one-pass bm-c r907 \u7a97 03:3x\uff08W212 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7r906 freeze 0f30cb725+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011", 1),
 # T. §0 cumulative projection
 ("\u7d2f\u8ba1 null \u6c60=462,120+2,200\uff08\u672c\u6ce2\uff09=**464,320 \u6295\u5f71**",
  "\u7d2f\u8ba1 null \u6c60=464,320+2,200\uff08\u672c\u6ce2\uff09=**466,520 \u6295\u5f71**", 1),
 # U. §0 认领 seat + downstream projection
 ("\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261011-0732-bmc-w212-seat \u5df2\u63a8 origin dace861b1 r565 \u5f8b\u00b7probe W213+ \u6295\u5f71 A 483_204..485_203 / B 483_404..483_603 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W212 B \u5e26 483_204..483_403 \u6ce8\u518c\u540e\u5c06\u62d2 naive W213 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u4e09\u4f8b\u2014\u2014**W213 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W212 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09",
  "\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261012-0342-bmc-w213-seat \u5df2\u63a8 origin 4f3b0d6a8 r565 \u5f8b\u00b7probe W214+ \u6295\u5f71 A 485_404..487_403 / B 485_604..485_803 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W213 B \u5e26 485_404..485_603 \u6ce8\u518c\u540e\u5c06\u62d2 naive W214 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u56db\u4f8b\u2014\u2014**W214 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W213 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09", 1),
 # V. §0 engine-line ordinal + wave-number restatement
 ("T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 202 \u6ce2\u3010bm-c \u7b2c\u56db\u5341\u4e8c\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=41 seat-time face\uff08r859 \u7a97 attempt-continuity \u8ba1\u6cd5\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 41+\u5019\u9009=\u7b2c 42 \u679a EXACT\uff08W210 r898 takeover +1 shift \u540e\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011\u3002\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W211 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261011-0732-bmc-w212-seat \u5148\u63a8 origin dace861b1 r565 \u5f8b",
  "T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 203 \u6ce2\u3010bm-c \u7b2c\u56db\u5341\u4e09\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=42 live face\uff08r908 \u7a97 live \u5355\u6001\u8ba1\u6cd5\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 42+\u5019\u9009=\u7b2c 43 \u679a EXACT\uff08\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011\u3002\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W212 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261012-0342-bmc-w213-seat \u5148\u63a8 origin 4f3b0d6a8 r565 \u5f8b", 1),
 # V2. §0 engine live-read stamp
 ("saturation_engine.py status live-read r906\uff1aburns_active", "saturation_engine.py status live-read r908\uff1aburns_active", 1),
 # V3. §0 RAM face
 ("\u672c\u7a97 free RAM ~0.8GB\uff08MV \u5f71\u7247\u94fe=CEO \u4f18\u5148\u4ee4\u5728\u98de\u5360\u7528\u00b7O-20261011-0012 sec.2.3 \u5f71\u7247\u94fe\u4f18\u5148\u4e0d\u53d8\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\uff09",
  "\u672c\u7a97 free RAM ~1.6GB\uff08MV XQ i2v \u5f71\u7247\u94fe=CEO \u4f18\u5148\u4ee4\u5728\u98de\u5360\u7528\u00b7O-20261011-0012 sec.2.3 \u5f71\u7247\u94fe\u4f18\u5148\u4e0d\u53d8\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211/W212 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\uff09", 1),
 # MM. §0 materializer mtime face
 ("\u81ea\u89c1 W212 \u884c\u5e76\u70b9\u706b\u81ea\u70e7", "\u81ea\u89c1 W213 \u884c\u5e76\u70b9\u706b\u81ea\u70e7", 1),
 # W. §3 A 档
 ("entry rng seed=**481_204+j**\uff08\u6cd5\u5178 \u00a74 W212 \u884c A=481_204..483_203\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e8c\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 481_004..483_003 \u8d77\u70b9\u5373\u88ab W211 \u58f0\u660e B \u5e26 481_004..481_203 \u62d2\u21921 hop \u843d 481_204..483_203",
  "entry rng seed=**483_404+j**\uff08\u6cd5\u5178 \u00a74 W213 \u884c A=483_404..485_403\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e09\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 483_204..485_203 \u8d77\u70b9\u5373\u88ab W212 \u6ce8\u518c B \u5e26 483_204..483_403 \u62d2\u21921 hop \u843d 483_404..485_403", 1),
 # X. §3 B 档
 ("entry rng=**481_204+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**483_204+j**\uff08\u6cd5\u5178 \u00a74 W212 \u884c B=483_204..483_403\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e26 481_204..481_403 \u5728\u58f0\u660e\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 481_204..483_203 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 483_204..483_403\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W211 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b",
  "entry rng=**483_404+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**485_404+j**\uff08\u6cd5\u5178 \u00a74 W213 \u884c B=485_404..485_603\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e24 483_404..483_603 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 483_404..485_403 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 485_404..485_603\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W212 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b", 1),
 # Y. §3 disjoint + probe receipt + selftest face + estate note
 ("selftest \u5f3a\u5236\uff09\uff1aW212 \u5e26\u4e0e v1 \u5728\u7528\u5e26", "selftest \u5f3a\u5236\uff09\uff1aW213 \u5e26\u4e0e v1 \u5728\u7528\u5e26", 1),
 ("W2..W211 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09", "W2..W212 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09", 1),
 ("\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w212bmc_20261011 \u63a2\u9488\u7a97", "\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w213bmc_20261012 \u63a2\u9488\u7a97", 1),
 ("selftest W212 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W211 \u884c parity \u817f",
  "selftest W213 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W212 \u884c parity \u817f", 1),
 ("\u4ece**\u672c\u673a W211 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W211 \u5757\u7684 W210 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W211 leg \u6784\u6210 W212 \u5757 parity 70 \u884c\uff08W138..W206+W211\uff09",
  "\u4ece**\u672c\u673a W212 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W212 \u5757\u7684 W211 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W211+W212 leg \u6784\u6210 W213 \u5757 parity 71 \u884c\uff08W138..W206+W211+W212\uff09", 1),
 # Z. §4 merged pool
 ("\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W211 \u5df2\u843d\u8d26 462,120 \u5b9e\u6d4b", "\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W212 \u5df2\u843d\u8d26 464,320 \u5b9e\u6d4b", 1),
 # AA. §4 ledger call
 ('append_ledger(batch_name="PERPETUAL-N1-W212", batch_trials=2200, file_name="results/perpetual_faces/n1_w212_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W213", batch_trials=2200, file_name="results/perpetual_faces/n1_w213_results.json"', 1),
 # BB. §5 anchor preface
 ("\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W211 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 887,989\u00b7**K=462,120 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W211 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w211_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b701:39:51 finalize one-pass\u3011",
  "\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W212 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 890,189\u00b7**K=464,320 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W212 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w212_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b703:3x finalize one-pass\u3011", 1),
 # CC. §5.1
 ("1. W212-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W211 \u5b9e\u6d4b\u952e **\u22120.09269601**\u00b7K=462,120 \u5408\u5e76\u6c60\u00b7W211-only \u5b9e\u6d4b **\u22120.09479655**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W211 \u5171\u4e8c\u767e\u96f6\u4e5d\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW211-only vs merged \u5b9e\u5dee 0.0021 \u5728\u5e26\u5185\uff09\u3002",
  "1. W213-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W212 \u5b9e\u6d4b\u952e **\u22120.09267005**\u00b7K=464,320 \u5408\u5e76\u6c60\u00b7W212-only \u5b9e\u6d4b **\u22120.08721705**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W212 \u5171\u4e8c\u767e\u4e00\u5341\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW212-only vs merged \u5b9e\u5dee 0.0055 \u5728\u5e26\u5185\uff09\u3002", 1),
 # DD. §5.2
 ("\u952e **0.24510876**=W211 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002", "\u952e **0.24512048**=W212 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002", 1),
 # EE. §5.3
 ("3. A \u6863 full_sharpe_p95 \u4e0e W211 A \u6863 p95\uff08**0.3134** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**",
  "3. A \u6863 full_sharpe_p95 \u4e0e W212 A \u6863 p95\uff08**0.3282** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**", 1),
 # FF. §5.4 (physical ends \u3011\uff09\u3002)
 ("W136..W211 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W211 \u5b9e\u6d4b K-lift **0.0002**\u00b7line_merged@K462,120 **1.1901**\u00b7line_pre_w211 1.1899\u00b7n_eff_held_equal 885,789\uff1bse_mu \u6536\u7a84\u94fe \u2026\u2192W209 0.000362\u2192W211 **0.000361**\u3011\uff09\u3002",
  "W136..W212 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W212 \u5b9e\u6d4b K-lift **0.0001**\u00b7line_merged@K464,320 **1.1903**\u00b7line_pre_w212 1.1902\u00b7n_eff_held_equal 887,989\uff1bse_mu \u6536\u7a84\u94fe \u2026\u2192W209 0.000362\u2192W211 0.000361\u2192W212 **0.000360**\u3011\uff09\u3002", 1),
 # GG. §5.5 downstream projection (whole compound)
 ("5. **W213+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 483_204..485_203 CLEAN\uff08hops=0\u00b7pre-W212 \u5b87\u5b99\uff09\uff1bB naive first-clean **483_404..483_603 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W213\uff1aW213 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W212 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W212 B \u5e26 483_204..483_403 \u6ce8\u518c\u540e\u5c06\u62d2 naive W213 A \u7a97**\u2014\u2014W213 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W212 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u4e09\u4f8b\uff09\uff1bverify at W213 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002",
  "5. **W214+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 485_404..487_403 CLEAN\uff08hops=0\u00b7pre-W213 \u5b87\u5b99\uff09\uff1bB naive first-clean **485_604..485_803 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W214\uff1aW214 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W213 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W213 B \u5e26 485_404..485_603 \u6ce8\u518c\u540e\u5c06\u62d2 naive W214 A \u7a97**\u2014\u2014W214 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W213 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u56db\u4f8b\uff09\uff1bverify at W214 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002", 1),
 # HH. §6 runner wave args
 ("--shard k --of 12 --wave 212/finalize --wave 212", "--shard k --of 12 --wave 213/finalize --wave 213", 1),
 # II. §6 ignition evidence path
 ("\u3010n1_w212/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011", "\u3010n1_w213/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011", 1),
 # JJ. §6 shard deliverable path
 ("`results/p2cal_ext/n1_w212/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w213/shard-<k>-of-12.json`", 1),
 # KK. §6 finalize deliverable + deps span
 ("`results/perpetual_faces/n1_w212_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W211 \u5168\u843d\uff09**",
  "`results/perpetual_faces/n1_w213_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W212 \u5168\u843d\uff09**", 1),
 # LL. §6 engine ledger owner rows (physical face uses U+3014/U+3015 tortoise brackets)
 ("engine_owner==bm-c 41 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009", "engine_owner==bm-c 42 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009", 1),
]

for i, (old, new, expect) in enumerate(REP):
    c = t.count(old)
    assert c == expect, f"REP[{i}] count {c} != {expect}: {old[:60]}..."
    t = t.replace(old, new, 1)
print(f"applied {len(REP)} count-asserted replacements")

# ---------- §7/§8 cut + pending stubs (W213 fresh freeze face) ----------
marker = "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011"
pos = t.find(marker)
assert pos > 0, "section-7 marker not found"
t = t[:pos].rstrip("\r\n") + eol + eol
stubs = [
 "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011",
 "- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f/\u5408\u5e76\u6c60 K/merged mu\u00b7sigma\u00b7se_mu/K-lift \u5bf9\u7167/\u00a75 \u4e94\u9884\u952e\u673a\u8bc1\u4ef6/\u516d\u95e8\u63a2\u9488/canon flip \u6001/audit \u6bb5\u2014\u2014r907 W212 \u00a77 \u8303\u5f0f\uff09",
 "",
 "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u3011",
 "- \uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W214+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r907 W212 \u00a78 \u8303\u5f0f\uff09",
 "",
 "- **\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit**\uff08freeze hash \u5f52\u7a97\u62a5\u544a\u4e0e\u6cd5\u5178 \u00a74 \u884c\uff1b\u51bb\u7ed3\u540e\u8981\u6539\u5224\u636e=\u7981\uff08\u56de\u586b\u9650 \u00a77/\u00a78\uff09\u3002",
 "",
]
t += eol.join(stubs)

# ---------- DRY gates ----------
GATES = [
 ("PERPETUAL-N1-W213", 4), ("PERPETUAL-N1-W212", 0),
 ("PERPETUAL_N1_W213_PREREG", 2), ("PERPETUAL_N1_W212_PREREG", 0),
 ("483_404..485_403", 6), ("485_404..485_603", 6),
 ("483_204..485_203", 2), ("483_204..483_403", 2),
 ("483_404..483_603", 2), ("485_404..487_403", 2), ("485_604..485_803", 2),
 ("481_204", 0), ("481_004", 0), ("481_203", 0), ("483_203+1", 0),
 ("\u7b2c 211 \u679a", 1), ("\u7b2c 210 \u679a", 0),
 ("\u7b2c\u4e03\u5341\u4e09\u4f8b", 4), ("\u7b2c\u4e03\u5341\u56db\u4f8b", 2),
 ("\u7b2c\u4e03\u5341\u4e8c\u4f8b", 0), ("SEVENTY-THIRD", 1), ("SEVENTY-SECOND", 0),
 ("MSG-20261012-0342-bmc-w213-seat", 3), ("MSG-20261011-0732-bmc-w212-seat", 0),
 ("4f3b0d6a8", 3), ("dace861b1", 0),
 ("_w213bmc_20261012_probe_receipt.json", 1), ("_w212bmc_20261011_probe_receipt.json", 0),
 ("_w213bmc_20261012 \u63a2\u9488\u7a97", 1), ("_w212bmc_20261011 \u63a2\u9488\u7a97", 0),
 ("n1_w213_results.json", 2), ("n1_w212_results.json", 3), ("n1_w211_results.json", 1),
 ("890,189", 3), ("887,989", 2), ("464,320", 7), ("462,120", 1), ("466,520", 1),
 ("\u22120.09267005", 1), ("\u22120.08721705", 1), ("0.24512048", 1), ("0.3282", 1),
 ("0.000360", 1), ("1.1903", 1),
 ("\u8868\u5c3e W212 \u884c", 2), ("\u884c 202 \u6ce8\u518c\u5728\u518c", 1),
 ("--wave 213", 2), ("--wave 212", 0),
 ("r908 freeze \u7a97", 1), ("r906 freeze \u7a97", 0),
 ("\u5360\u4f4d\u00b7finalize one-pass \u540e\u56de\u586b", 1),
 ("\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit", 1),
]
for s, expect in GATES:
    c = t.count(s)
    assert c == expect, f"GATE {s!r}: count {c} != {expect}"
# malformed-window scan (r773 law)
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", t):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, f"malformed window {m.group(0)}"
print(f"DRY gates {len(GATES)} all green; no malformed windows")

open(DST, "wb").write(t.encode("utf-8"))
print(f"WRITTEN {DST} ({len(t.encode('utf-8'))} bytes, eol={'CRLF' if eol == chr(13) + chr(10) else 'LF'})")
