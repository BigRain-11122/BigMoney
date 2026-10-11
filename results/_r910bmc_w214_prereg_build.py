# -*- coding: utf-8 -*-
"""W214 prereg builder (bm-c loop r910 freeze window, 2026-10-12 04:5x).
Buildgen-face law (r830 E41 / r773 / r781 / r908): every OLD string below is a
physical fragment asserted count==1 against the W213 prereg bytes on disk --
zero visual transcription is trusted; any mismatch = LOUD abort, re-probe.
All NEW facts machine-derived this window (probe receipt
results/_w214bmc_20261012_probe_receipt.json (r909 seat window, origin d55a6b58b)
+ n1_w213_results.json finalize fields + saturation_engine live status +
seat push d55a6b58b)."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "PERPETUAL_N1_W213_PREREG.md")
DST = os.path.join(ROOT, "research", "PERPETUAL_N1_W214_PREREG.md")
PROBE = os.path.join(ROOT, "results", "_w214bmc_20261012_probe_receipt.json")
W213 = os.path.join(ROOT, "results", "perpetual_faces", "n1_w213_results.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
b = open(SRC, "rb").read()
t = b.decode("utf-8")
eol = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"

rec = json.load(open(PROBE, encoding="utf-8"))
w213 = json.load(open(W213, encoding="utf-8"))
A = rec["bands"]["A"].split("_"); B = rec["bands"]["B"].split("_")
a_lo, a_hi = int(A[0]), int(A[1]); b_lo, b_hi = int(B[0]), int(B[1])
assert (a_lo, a_hi, b_lo, b_hi) == (485_604, 487_603, 487_604, 487_803), rec["bands"]
assert [a_lo, a_hi] == rec["legs"]["leg1"]["A"] and [b_lo, b_hi] == rec["legs"]["leg1"]["B"]
merged = w213["null_pool_cumulative"]["merged"]
wonly = w213["null_pool_cumulative"]["w213_only"]
skill = w213["skill_line_v2_k_lift"]
famA = w213["families"]["A_random_engine_exit"]
led = w213["science_gates"]["ledger"]
assert led["total"] == 892_389 and merged["n_values"] == 466_520
mu8 = f"\u2212{abs(merged['mu']):.8f}"          # -0.09268619 (U+2212 display form, r833 law)
wo8 = f"\u2212{abs(wonly['mu']):.8f}"          # -0.09609245
sig8 = f"{merged['sigma']:.8f}"                # 0.24512063
assert mu8 == "\u22120.09268619" and wo8 == "\u22120.09609245" and sig8 == "0.24512063"
assert skill["line_pre_w213"] == 1.1904 and skill["line_merged_466520"] == 1.1904
assert skill["line_delta_k_lift"] == 0.0 and skill["n_eff_held_equal"] == 890_189
assert famA["full_sharpe_p95"] == 0.3056
semu = w213["null_pool_cumulative"]["se_mu_at_k466520"]
assert semu == 0.000359

REP = [
 # A. title pump ordinal + batch name
 ("PERPETUAL-N1-W213 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 211 \u679a",
  "PERPETUAL-N1-W214 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 212 \u679a", 1),
 # B. title engine_owner face + freeze window stamp
 ("engine_owner \u884c 202 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W212 \u884c\u00b7probe leg0 \u673a\u8bc1 210 \u884c live \u5355\u6001\u96f6\u6ce8\u5165\u817f\uff09+\u672c\u5019\u9009=bm-c \u7b2c\u56db\u5341\u4e09\u679a\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 prose 42nd=seat-time face\uff08r908 \u7a97 W212 \u6ce8\u518c\u540e live derive\u00b7r906 freeze receipt 42nd owned \u627f\u88ad\uff09\u2192freeze \u65f6 live derive bm-c rows 42+\u5019\u9009=\u7b2c 43 \u679a EXACT\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\u3011\u3010bm-c \u5faa\u73af\u73ed r908 freeze \u7a97\u00b72026-10-12 03:4x\u00b7CEO \u586b\u8f7d\u4ee4",
  "engine_owner \u884c 203 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W213 \u884c\u00b7probe leg0 \u673a\u8bc1 211 \u884c live \u5355\u6001\u96f6\u6ce8\u5165\u817f\uff09+\u672c\u5019\u9009=bm-c \u7b2c\u56db\u5341\u56db\u679a\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 prose 43rd=seat-time face\uff08r909 \u7a97 W213 \u6ce8\u518c\u540e live derive\u00b7r908 freeze receipt 43rd owned \u627f\u88ad\uff09\u2192freeze \u65f6 live derive bm-c rows 43+\u5019\u9009=\u7b2c 44 \u679a EXACT\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\u3011\u3010bm-c \u5faa\u73af\u73ed r910 freeze \u7a97\u00b72026-10-12 05:0x\u00b7CEO \u586b\u8f7d\u4ee4", 1),
 # C. 令源 satengine stamp
 ("saturation_engine.py status live-read r908\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb",
  "saturation_engine.py status live-read r910\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb", 1),
 # D. 波号 + vacancy four-check
 ("**\u6ce2\u53f7 213=\u6ce8\u518c\u8868 W212 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r908 \u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W213 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 213 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W213 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W213_PREREG.md \u56db\u67e5\uff09",
  "**\u6ce2\u53f7 214=\u6ce8\u518c\u8868 W213 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r909 \u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W214 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 214 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W214 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W214_PREREG.md \u56db\u67e5\uff09", 1),
 # E. upstream chain append W213
 ("+W212=bm-c r906 \u4e94\u9762\u51bb\u7ed3\uff080f30cb725\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r907 finalize one-pass \u5df2\u843d\uff08K=464,320\u00b7\u8d26\u672c\u5934 890,189 \u673a\u8bfb\u00b7n1_w212_results.json\u00b703:3x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W212 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**",
  "+W212=bm-c r906 \u4e94\u9762\u51bb\u7ed3\uff080f30cb725\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r907 finalize one-pass \u5df2\u843d\uff08K=464,320\u00b7\u8d26\u672c\u5934 890,189 \u673a\u8bfb\u00b7n1_w212_results.json\u00b703:3x\uff09+W213=bm-c r908 \u4e94\u9762\u51bb\u7ed3\uff08a24069f4c\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r909 finalize one-pass \u5df2\u843d\uff08K=466,520\u00b7\u8d26\u672c\u5934 892,389 \u673a\u8bfb\u00b7n1_w213_results.json\u00b704:2x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W213 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**", 1),
 # F. seat MSG + downstream pointer + single-state span
 ("\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261012-0342-bmc-w213-seat \u5df2\u63a8 origin 4f3b0d6a8 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r908 \u7a97\u3011\uff1b\u4e0b\u6e38 W214+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W214 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W212 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb",
  "\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261012-0438-bmc-w214-seat \u5df2\u63a8 origin d55a6b58b \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r909 \u7a97\u3011\uff1b\u4e0b\u6e38 W215+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W215 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W213 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb", 1),
 # G. ADMIT receipt path
 ("ADMIT \u56de\u6267=results/_w213bmc_20261012_probe_receipt.json \u4e94\u817f\u5355\u7a97",
  "ADMIT \u56de\u6267=results/_w214bmc_20261012_probe_receipt.json \u4e94\u817f\u5355\u7a97", 1),
 # H. A band prose (whole compound)
 ("\u672c\u6ce2 **A-ext seed=483_404..485_403**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e09\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 483_204..485_203\uff08\u81ea\u6ce8\u518c W212 A \u5c3e 483_203 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W212 \u6ce8\u518c B \u5e26 483_204..483_403 **\u62d2**\uff08W212 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **483_404..485_403**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08483_403+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e03\u5341\u4e09\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=SEVENTY-THIRD\uff08\u7b2c\u4e03\u5341\u4e09\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\uff09",
  "\u672c\u6ce2 **A-ext seed=485_604..487_603**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u56db\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 485_404..487_403\uff08\u81ea\u6ce8\u518c W213 A \u5c3e 485_403 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W213 \u6ce8\u518c B \u5e26 485_404..485_603 **\u62d2**\uff08W213 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **485_604..487_603**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08485_603+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e03\u5341\u56db\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=SEVENTY-FOURTH\uff08\u7b2c\u4e03\u5341\u56db\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\uff09", 1),
 # I. B band prose (whole compound)
 ("**B-ext exit seed=485_404..485_603**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 483_404..483_603 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 483_404..485_403 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **485_404..485_603**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08485_403+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W212 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W213 \u987b\u5728 post-W212 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09\u3002R250\uff1aW213 \u5e26\u4ece\u672a\u6307\u6d3e",
  "**B-ext exit seed=487_604..487_803**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 485_604..485_803 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 485_604..487_603 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **487_604..487_803**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08487_603+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W213 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W214 \u987b\u5728 post-W213 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09\u3002R250\uff1aW214 \u5e26\u4ece\u672a\u6307\u6d3e", 1),
 # J. seed_admit lines (whole compound)
 ("A base=483404 span=2000 checked=2000 verdict=FREE / B base=485404 span=200 checked=200 verdict=FREE",
  "A base=485604 span=2000 checked=2000 verdict=FREE / B base=487604 span=200 checked=200 verdict=FREE", 1),
 # K. scan face
 ("\u626b\u63cf\u9762=pre-W213 \u5168\u4e8c\u767e\u4e00\u5341\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W212 \u884c\u00b7probe leg0 \u673a\u8bc1 210 \u884c live \u5355\u6001 owner rows 202\uff09",
  "\u626b\u63cf\u9762=pre-W214 \u5168\u4e8c\u767e\u4e00\u5341\u4e00\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W213 \u884c\u00b7probe leg0 \u673a\u8bc1 211 \u884c live \u5355\u6001 owner rows 203\uff09", 1),
 # L. 复用域 runner span
 ("\uff08W2..W212 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528", "\uff08W2..W213 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528", 1),
 # M. freeze bundle note + selftest face + precedent
 ("selftest W213 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**\u672c\u4ef6\u4e0e results/_w213bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w212bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W212 \u884c+W212 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W212 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r906/W212 \u5148\u4f8b freeze-prep \u540c\u5f0f",
  "selftest W214 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**\u672c\u4ef6\u4e0e results/_w214bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w213bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W213 \u884c+W213 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W213 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r908/W213 \u5148\u4f8b freeze-prep \u540c\u5f0f", 1),
 # N. §0 batch name
 ("\u6279\u540d=**PERPETUAL-N1-W213**", "\u6279\u540d=**PERPETUAL-N1-W214**", 1),
 # O. §0 upstream anchor
 ("**W1..W212 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **890,189**\u00b7K=464,320 \u5408\u5e76\u6c60\u00b7n1_w212_results.json \u673a\u8bfb\u00b7W212 finalize one-pass bm-c r907 \u7a97 03:3x\uff08W212 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7r906 freeze 0f30cb725+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011",
  "**W1..W213 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **892,389**\u00b7K=466,520 \u5408\u5e76\u6c60\u00b7n1_w213_results.json \u673a\u8bfb\u00b7W213 finalize one-pass bm-c r909 \u7a97 04:2x\uff08W213 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7r908 freeze a24069f4c+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011", 1),
 # P. §0 cumulative projection
 ("\u7d2f\u8ba1 null \u6c60=464,320+2,200\uff08\u672c\u6ce2\uff09=**466,520 \u6295\u5f71**",
  "\u7d2f\u8ba1 null \u6c60=466,520+2,200\uff08\u672c\u6ce2\uff09=**468,720 \u6295\u5f71**", 1),
 # Q. §0 认领 seat + downstream projection
 ("\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261012-0342-bmc-w213-seat \u5df2\u63a8 origin 4f3b0d6a8 r565 \u5f8b\u00b7probe W214+ \u6295\u5f71 A 485_404..487_403 / B 485_604..485_803 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W213 B \u5e26 485_404..485_603 \u6ce8\u518c\u540e\u5c06\u62d2 naive W214 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u56db\u4f8b\u2014\u2014**W214 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W213 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09",
  "\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261012-0438-bmc-w214-seat \u5df2\u63a8 origin d55a6b58b r565 \u5f8b\u00b7probe W215+ \u6295\u5f71 A 487_604..489_603 / B 487_804..488_003 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W214 B \u5e26 487_604..487_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W215 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u4e94\u4f8b\u2014\u2014**W215 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W214 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09", 1),
 # R. §0 engine-line ordinal + wave-number restatement
 ("T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 203 \u6ce2\u3010bm-c \u7b2c\u56db\u5341\u4e09\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=42 live face\uff08r908 \u7a97 live \u5355\u6001\u8ba1\u6cd5\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 42+\u5019\u9009=\u7b2c 43 \u679a EXACT\uff08\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011\u3002\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W212 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261012-0342-bmc-w213-seat \u5148\u63a8 origin 4f3b0d6a8 r565 \u5f8b",
  "T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 204 \u6ce2\u3010bm-c \u7b2c\u56db\u5341\u56db\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=43 live face\uff08r909 \u7a97 live \u5355\u6001\u8ba1\u6cd5\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 43+\u5019\u9009=\u7b2c 44 \u679a EXACT\uff08\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011\u3002\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W213 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261012-0438-bmc-w214-seat \u5148\u63a8 origin d55a6b58b r565 \u5f8b", 1),
 # S. §0 RAM face
 ("**RAM face \u5982\u5b9e\u6ce8\u8bb0\uff1a\u672c\u7a97 free RAM ~1.6GB\uff08MV XQ i2v \u5f71\u7247\u94fe=CEO \u4f18\u5148\u4ee4\u5728\u98de\u5360\u7528\u00b7O-20261011-0012 sec.2.3 \u5f71\u7247\u94fe\u4f18\u5148\u4e0d\u53d8\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211/W212 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\uff09",
  "**RAM face \u5982\u5b9e\u6ce8\u8bb0\uff1a\u672c\u7a97 free RAM ~6.8GB\uff08MV XQ i2v \u5f71\u7247\u94fe=CEO \u4f18\u5148\u4ee4\u5728\u98de\u5360\u7528\u00b7O-20261011-0012 sec.2.3 \u5f71\u7247\u94fe\u4f18\u5148\u4e0d\u53d8\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211/W212/W213 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\uff09", 1),
 # T. materializer mtime face
 ("\u81ea\u89c1 W213 \u884c\u5e76\u70b9\u706b\u81ea\u70e7", "\u81ea\u89c1 W214 \u884c\u5e76\u70b9\u706b\u81ea\u70e7", 1),
 # U. §0.5 gate command path
 ("--prereg research/PERPETUAL_N1_W213_PREREG.md", "--prereg research/PERPETUAL_N1_W214_PREREG.md", 1),
 # V. §0.5 upstream span
 ("\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W212 \u843d\u5730\uff09\u7684\u79cd\u5b50\u5e26\u6269\u5c55\u91cd\u6d4b", "\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W213 \u843d\u5730\uff09\u7684\u79cd\u5b50\u5e26\u6269\u5c55\u91cd\u6d4b", 1),
 # W. §3 A 档
 ("entry rng seed=**483_404+j**\uff08\u6cd5\u5178 \u00a74 W213 \u884c A=483_404..485_403\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u4e09\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 483_204..485_203 \u8d77\u70b9\u5373\u88ab W212 \u6ce8\u518c B \u5e26 483_204..483_403 \u62d2\u21921 hop \u843d 483_404..485_403\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09",
  "entry rng seed=**485_604+j**\uff08\u6cd5\u5178 \u00a74 W214 \u884c A=485_604..487_603\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e03\u5341\u56db\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 485_404..487_403 \u8d77\u70b9\u5373\u88ab W213 \u6ce8\u518c B \u5e26 485_404..485_603 \u62d2\u21921 hop \u843d 485_604..487_603\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09", 1),
 # X. §3 B 档 (source contains the r908 typo U+5E24 帤 in 算术续帤 -- physical bytes asserted)
 ("entry rng=**483_404+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**485_404+j**\uff08\u6cd5\u5178 \u00a74 W213 \u884c B=485_404..485_603\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e24 483_404..483_603 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 483_404..485_403 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 485_404..485_603\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W212 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09",
  "entry rng=**485_604+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**487_604+j**\uff08\u6cd5\u5178 \u00a74 W214 \u884c B=487_604..487_803\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e26 485_604..485_803 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 485_604..487_603 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 487_604..487_803\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W213 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09", 1),
 # Y. §3 disjoint A face
 ("\u79cd\u5b50\u5e26 disjoint \u5168\u4f8b\uff08selftest \u5f3a\u5236\uff09\uff1aW213 \u5e26\u4e0e v1 \u5728\u7528\u5e26", "\u79cd\u5b50\u5e26 disjoint \u5168\u4f8b\uff08selftest \u5f3a\u5236\uff09\uff1aW214 \u5e26\u4e0e v1 \u5728\u7528\u5e26", 1),
 # Y2. §3 disjoint span
 ("W2..W212 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09", "W2..W213 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09", 1),
 # Z. §3 ADMIT window
 ("\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w213bmc_20261012 \u63a2\u9488\u7a97", "\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w214bmc_20261012 \u63a2\u9488\u7a97", 1),
 # AA. §3 selftest face
 ("selftest W213 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W212 \u884c parity \u817f",
  "selftest W214 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W213 \u884c parity \u817f", 1),
 # AB. §3 estate note
 ("estate \u63d0\u53d6\u9762\u6ce8\u8bb0**\uff1a\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u7684 parity estate\uff08W138..W206 69 \u884c full-span\u00b7r858 absorb \u4ee3\uff09\u4ece**\u672c\u673a W212 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W212 \u5757\u7684 W211 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W211+W212 leg \u6784\u6210 W213 \u5757 parity 71 \u884c\uff08W138..W206+W211+W212\uff09\u00b7\u96f6\u5047\u8bbe\u96f6\u98ce\u9669",
  "estate \u63d0\u53d6\u9762\u6ce8\u8bb0**\uff1a\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u7684 parity estate\uff08W138..W206 69 \u884c full-span\u00b7r858 absorb \u4ee3\uff09\u4ece**\u672c\u673a W213 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W213 \u5757\u7684 W212 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W212+W213 leg \u6784\u6210 W214 \u5757 parity 72 \u884c\uff08W138..W206+W211+W212+W213\uff09\u00b7\u96f6\u5047\u8bbe\u96f6\u98ce\u9669", 1),
 # AC. §4 merged pool span
 ("\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W212 \u5df2\u843d\u8d26 464,320 \u5b9e\u6d4b", "\u5df2\u843d\u8d26\u51c0\u503c\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W213 \u5df2\u843d\u8d26 466,520 \u5b9e\u6d4b", 1),
 # AD. §4 ledger call
 ('append_ledger(batch_name="PERPETUAL-N1-W213", batch_trials=2200, file_name="results/perpetual_faces/n1_w213_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W214", batch_trials=2200, file_name="results/perpetual_faces/n1_w214_results.json"', 1),
 # AE. §5 anchor preface
 ("\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W212 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 890,189\u00b7**K=464,320 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W212 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w212_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b703:3x finalize one-pass\u3011",
  "\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W213 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 892,389\u00b7**K=466,520 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W213 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w213_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b704:2x finalize one-pass\u3011", 1),
 # AF. §5.1
 ("1. W213-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W212 \u5b9e\u6d4b\u952e **\u22120.09267005**\u00b7K=464,320 \u5408\u5e76\u6c60\u00b7W212-only \u5b9e\u6d4b **\u22120.08721705**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W212 \u5171\u4e8c\u767e\u4e00\u5341\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW212-only vs merged \u5b9e\u5dee 0.0055 \u5728\u5e26\u5185\uff09\u3002",
  "1. W214-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W213 \u5b9e\u6d4b\u952e **\u22120.09268619**\u00b7K=466,520 \u5408\u5e76\u6c60\u00b7W213-only \u5b9e\u6d4b **\u22120.09609245**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W213 \u5171\u4e8c\u767e\u4e00\u5341\u4e00\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW213-only vs merged \u5b9e\u5dee 0.0034 \u5728\u5e26\u5185\uff09\u3002", 1),
 # AG. §5.2
 ("\u952e **0.24512048**=W212 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002", "\u952e **0.24512063**=W213 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002", 1),
 # AH. §5.3
 ("3. A \u6863 full_sharpe_p95 \u4e0e W212 A \u6863 p95\uff08**0.3282** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W211 \u5148\u4f8b",
  "3. A \u6863 full_sharpe_p95 \u4e0e W213 A \u6863 p95\uff08**0.3056** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W212 \u5148\u4f8b", 1),
 # AI. §5.4
 ("W136..W212 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W212 \u5b9e\u6d4b K-lift **0.0001**\u00b7line_merged@K464,320 **1.1903**\u00b7line_pre_w212 1.1902\u00b7n_eff_held_equal 887,989\uff1bse_mu \u6536\u7a84\u94fe \u2026\u2192W209 0.000362\u2192W211 0.000361\u2192W212 **0.000360**\u3011\uff09\u3002",
  "W136..W213 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W213 \u5b9e\u6d4b K-lift **0.0000**\u00b7line_merged@K466,520 **1.1904**\u00b7line_pre_w213 1.1904\u00b7n_eff_held_equal 890,189\uff1bse_mu \u6536\u7a84\u94fe \u2026\u2192W209 0.000362\u2192W211 0.000361\u2192W212 0.000360\u2192W213 **0.000359**\u3011\uff09\u3002", 1),
 # AJ. §5.5 downstream projection (whole compound)
 ("5. **W214+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 485_404..487_403 CLEAN\uff08hops=0\u00b7pre-W213 \u5b87\u5b99\uff09\uff1bB naive first-clean **485_604..485_803 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W214\uff1aW214 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W213 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W213 B \u5e26 485_404..485_603 \u6ce8\u518c\u540e\u5c06\u62d2 naive W214 A \u7a97**\u2014\u2014W214 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W213 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u56db\u4f8b\uff09\uff1bverify at W214 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002",
  "5. **W215+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 487_604..489_603 CLEAN\uff08hops=0\u00b7pre-W214 \u5b87\u5b99\uff09\uff1bB naive first-clean **487_804..488_003 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W215\uff1aW215 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W214 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W214 B \u5e26 487_604..487_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W215 A \u7a97**\u2014\u2014W215 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W214 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u4e94\u4f8b\uff09\uff1bverify at W215 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002", 1),
 # AK. §6 runner wave args
 ("--shard k --of 12 --wave 213/finalize --wave 213", "--shard k --of 12 --wave 214/finalize --wave 214", 1),
 # AL. §6 ignition evidence path
 ("\u3010n1_w213/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011", "\u3010n1_w214/ \u5206\u7247\u8ba1\u6570\u589e\u957f\u00b7\u552f\u4e00\u70b9\u706b\u8bc1\u636e\u00b7r325 \u5f8b\u3011", 1),
 # AM. §6 shard deliverable path
 ("`results/p2cal_ext/n1_w213/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w214/shard-<k>-of-12.json`", 1),
 # AN. §6 finalize deliverable + deps span
 ("`results/perpetual_faces/n1_w213_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W212 \u5168\u843d\uff09**",
  "`results/perpetual_faces/n1_w214_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W213 \u5168\u843d\uff09**", 1),
 # AO. §6 engine ledger owner rows
 ("engine_owner==bm-c 42 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009", "engine_owner==bm-c 43 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009", 1),
]

for i, (old, new, expect) in enumerate(REP):
    c = t.count(old)
    assert c == expect, f"REP[{i}] count {c} != {expect}: {old[:60]}..."
    t = t.replace(old, new, 1)
print(f"applied {len(REP)} count-asserted replacements")

# ---------- §7/§8 cut + pending stubs (W214 fresh freeze face) ----------
marker = "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011"
pos = t.find(marker)
assert pos > 0, "section-7 marker not found"
t = t[:pos].rstrip("\r\n") + eol + eol
stubs = [
 "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011",
 "- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f/\u5408\u5e76\u6c60 K/merged mu\u00b7sigma\u00b7se_mu/K-lift \u5bf9\u7167/\u00a75 \u4e94\u9884\u952e\u673a\u8bc1\u4ef6/\u516d\u95e8\u63a2\u9488/canon flip \u6001/audit \u6bb5\u2014\u2014r909 W213 \u00a77 \u8303\u5f0f\uff09",
 "",
 "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u3011",
 "- \uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W215+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r909 W213 \u00a78 \u8303\u5f0f\uff09",
 "",
 "- **\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit**\uff08freeze hash \u5f52\u7a97\u62a5\u544a\u4e0e\u6cd5\u5178 \u00a74 \u884c\uff1b\u51bb\u7ed3\u540e\u8981\u6539\u5224\u636e=\u7981\uff08\u56de\u586b\u9650 \u00a77/\u00a78\uff09\u3002",
 "",
]
t += eol.join(stubs)

# ---------- DRY gates ----------
GATES = [
 ("PERPETUAL-N1-W214", 4), ("PERPETUAL-N1-W213", 0),
 ("PERPETUAL_N1_W214_PREREG", 2), ("PERPETUAL_N1_W213_PREREG", 0),
 ("485_604..487_603", 6), ("487_604..487_803", 6),
 ("485_404..487_403", 2), ("485_404..485_603", 2),
 ("485_604..485_803", 2), ("487_604..489_603", 2), ("487_804..488_003", 2),
 ("483_404", 0), ("483_204", 0), ("483_403+1", 0),
 ("485_603+1", 1), ("487_603+1", 1),
 ("\u7b2c 212 \u679a", 1), ("\u7b2c 211 \u679a", 0),
 ("\u7b2c\u4e03\u5341\u56db\u4f8b", 4), ("\u7b2c\u4e03\u5341\u4e94\u4f8b", 2),
 ("\u7b2c\u4e03\u5341\u4e09\u4f8b", 0), ("SEVENTY-FOURTH", 1), ("SEVENTY-THIRD", 0),
 ("MSG-20261012-0438-bmc-w214-seat", 3), ("MSG-20261012-0342-bmc-w213-seat", 0),
 ("d55a6b58b", 3), ("4f3b0d6a8", 0),
 ("_w214bmc_20261012_probe_receipt.json", 1), ("_w213bmc_20261012_probe_receipt.json", 0),
 ("_w214bmc_20261012 \u63a2\u9488\u7a97", 1), ("_w213bmc_20261012 \u63a2\u9488\u7a97", 0),
 ("n1_w214_results.json", 2), ("n1_w213_results.json", 3), ("n1_w212_results.json", 1),
 ("892,389", 3), ("890,189", 2), ("466,520", 7), ("464,320", 1), ("468,720", 1),
 ("\u22120.09268619", 1), ("\u22120.09609245", 1), ("0.24512063", 1), ("0.3056", 1),
 ("0.000359", 1), ("1.1904", 2),
 ("\u8868\u5c3e W213 \u884c", 2), ("\u884c 203 \u6ce8\u518c\u5728\u518c", 1),
 ("--wave 214", 2), ("--wave 213", 0),
 ("r910 freeze \u7a97", 1), ("r908 freeze \u7a97", 0), ("r908", 4),
 ("\u88ab W213 \u6ce8\u518c B \u5e26", 2), ("\u88ab W212 \u6ce8\u518c B \u5e26", 0),
 ("\u4e0e W213 \u5e2d\u4f4d leg4", 1), ("\u4e0e W212 \u5e2d\u4f4d leg4", 0),
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
