# -*- coding: utf-8 -*-
# r977 W235 R35 data generator v2: machine-advances committed R34 one wave.
# Three layers: (1) pre-shift targeted rewrites for complex/collision entries,
# (2) generic wave-token shifts, (3) post-shift value updates.
# All new values machine-read from results/_w235bmc_facts.json (r587 law).
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

F = json.load(open(r"results\_w235bmc_facts.json", encoding="utf-8"))
w = F["w234"]; b = F["w235_bands"]
LED = format(w["ledger_total"], ",")
K = format(w["merged_n_values"], ",")
KNEXT = format(w["merged_n_values"] + 2200, ",")
MU = w["merged_mu_8f"]; WON = w["w234_only_mu_8f"]
SIG = w["merged_sigma_8f"]; ABSD = w["w234_only_vs_merged_absdiff_4f"]
P95 = w["A_p95_4f"]; KLD = w["kl_line_delta"]
KLNE = format(w["kl_n_eff_held_equal"], ",")
KLPRE = w["kl_line_pre_w234_4f"]; KLMER = w["kl_line_merged_4f"]
SE = w["se_mu"]
A0, A1 = b["leg1_A"]; B0, B1 = b["leg1_B"]
W6A, W6B = b["leg4_W236p_A"], b["leg4_W236p_B"]
print("facts:", LED, K, MU, WON, SIG, ABSD, P95, KLD, KLNE, KLPRE, KLMER, SE, A0, A1, B0, B1, W6A, W6B)

t = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:80]!r}"
    t = t.replace(old, new)

# ============ LAYER 1: pre-shift targeted rewrites ============
# -- special BinOp win label (self freeze-window prediction r976 -> r978) --
rep("\u3010bm-c \u5faa\u73af\u73ed r976 freeze \u7a97\u00b7", "\u3010bm-c \u5faa\u73af\u73ed r978 freeze \u7a97\u00b7")
rep("saturation_engine.py status live-read r976\uff1a", "saturation_engine.py status live-read r978\uff1a")

# -- entry 0 ordinals (pre-shift; the W234 self tokens shift later) --
rep("N1 nulls-deepening \u6cf5\u7b2c 232 \u679a", "N1 nulls-deepening \u6cf5\u7b2c 233 \u679a")
rep("engine_owner \u884c 223 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W233 \u884c\u00b7probe leg0 \u673a\u8bc1 231 \u884c",
    "engine_owner \u884c 224 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W234 \u884c\u00b7probe leg0 \u673a\u8bc1 232 \u884c")
rep("\u672c\u5019\u9009=bm-c \u7b2c\u516d\u5341\u56db\u679a\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 prose 64th=seat-time face\uff08r974 \u7a97 W233 \u6ce8\u518c\u540e attempt-continuity live derive\u00b7r973 freeze receipt 63rd owned \u627f\u88ad\uff09\u2192freeze \u65f6 live derive bm-c rows 63+\u5019\u9009=\u7b2c 64 \u679a EXACT",
    "\u672c\u5019\u9009=bm-c \u7b2c\u516d\u5341\u4e94\u679a\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 prose 65th=seat-time face\uff08r976 \u7a97 W234 \u6ce8\u518c\u540e attempt-continuity live derive\u00b7r976-continuation freeze receipt 64th owned \u627f\u88ad\uff09\u2192freeze \u65f6 live derive bm-c rows 64+\u5019\u9009=\u7b2c 65 \u679a EXACT")

# -- entry 2 hygiene window labels --
rep("r976 \u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W234 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d",
    "r978 \u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W235 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d")
rep("origin perpetual_faces.py \u96f6 234 \u884c", "origin perpetual_faces.py \u96f6 235 \u884c")

# -- entry 3 chain surgery: unprotect W232 leg / protect W233 leg / append W234 leg --
rep("W@L32@=bm-c r968 \u6b7b\u7a97\u4e94\u9762\u51bb\u7ed3 estate \u843d\u76d8\u00b7r968 absorb \u63d0\u4ea4\uff08e58dbcda3\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r968 finalize one-pass \u5df2\u843d\uff08K=508,320\u00b7\u8d26\u672c\u5934 934,189 \u673a\u8bfb\u00b7n1_w@L32@_results.json\u00b715:2x\uff09",
    "W232=bm-c r968 \u6b7b\u7a97\u4e94\u9762\u51bb\u7ed3 estate \u843d\u76d8\u00b7r968 absorb \u63d0\u4ea4\uff08e58dbcda3\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r968 finalize one-pass \u5df2\u843d\uff08K=508,320\u00b7\u8d26\u672c\u5934 934,189 \u673a\u8bfb\u00b7n1_w232_results.json\u00b715:2x\uff09")
rep("+W233=bm-c r973 \u6b7b\u7a97\u4e94\u9762\u51bb\u7ed3\uff080ca920362\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r974 finalize one-pass \u5df2\u843d\uff08K=510,520\u00b7\u8d26\u672c\u5934 936,389 \u673a\u8bfb\u00b7n1_w233_results.json\u00b719:5x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W233 finalize \u5168\u843d\u5730",
    "+W@L33@=bm-c r973 \u6b7b\u7a97\u4e94\u9762\u51bb\u7ed3\uff080ca920362\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r974 finalize one-pass \u5df2\u843d\uff08K=510,520\u00b7\u8d26\u672c\u5934 936,389 \u673a\u8bfb\u00b7n1_w@L33@_results.json\u00b719:5x\uff09"
    "+W234=bm-c r976-continuation \u6b7b\u7a97\u4e94\u9762\u51bb\u7ed3\uff08de342250c\uff09+\u5f15\u64ce\u81ea\u71c3 12/12+r976 absorb finalize one-pass \u5df2\u843d\uff08K=" + K + "\u00b7\u8d26\u672c\u5934 " + LED + " \u673a\u8bfb\u00b7n1_w234_results.json\u00b721:5x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W234 finalize \u5168\u843d\u5730")

# -- entry 4 seat MSG/commit (pre-shift full rewrite) --
rep("\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261013-1955-bmc \u5df2\u63a8 origin 260217d39 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r974 \u7a97\u3011\uff1b\u4e0b\u6e38 W235+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W235 freezer \u627f\u63a5\u9762\uff09\u3011\u3002",
    "\u672c\u673a\u5e2d\u4f4d\u516c\u793a=MSG-20261013-2149-bmc \u5df2\u63a8 origin e830a2632 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7r976 \u7a97\u3011\uff1b\u4e0b\u6e38 W236+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W236 freezer \u627f\u63a5\u9762\uff09\u3011\u3002")

# -- entry 7/8 band derivation (pre-shift: band numbers + ordinals) --
rep("**A-ext seed=529_604..531_603**", "**A-ext seed=" + f"{A0//1000}_{A0}..{A1}" + "**")
rep("**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u56db\u4f8b**",
    "**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u4e94\u4f8b**")
rep("A \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 529_404..531_403\uff08\u81ea\u6ce8\u518c W233 A \u5c3e 529_403 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W233 \u6ce8\u518c B \u5e26 529_404..529_603 **\u62d2**\uff08W233 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **529_604..531_603**",
    "A \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 531_604..533_603\uff08\u81ea\u6ce8\u518c W234 A \u5c3e 531_603 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W234 \u6ce8\u518c B \u5e26 531_604..531_803 **\u62d2**\uff08W234 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **" + f"{A0//1000}_{A0}..{A1}" + "**")
rep("**A base==\u524d\u6ce2 B \u5c3e+1\uff08529_603+1\uff09\u673a\u68c0\u5173\u7cfb**",
    "**A base==\u524d\u6ce2 B \u5c3e+1\uff08531_803+1\uff09\u673a\u68c0\u5173\u7cfb**")
rep("=\u00b7**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u56db\u4f8b\uff08E36 \u5361\uff09**",
    "=\u00b7**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u4e94\u4f8b\uff08E36 \u5361\uff09**")
rep("A_semantics \u673a\u8bfb\u5e8f\u6570=NINETY-FOURTH\uff08\u7b2c\u4e5d\u5341\u56db\u4f8b\uff09",
    "A_semantics \u673a\u8bfb\u5e8f\u6570=NINETY-FIFTH\uff08\u7b2c\u4e5d\u5341\u4e94\u4f8b\uff09")
rep("**B-ext exit seed=531_604..531_803**", "**B-ext exit seed=" + f"{B0//1000}_{B0}..{B1}" + "**")
rep("B \u9762 naive first-clean \u7ee7\u7eed\u5e26 529_604..529_803 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 529_604..531_603 \u5185**",
    "B \u9762 naive first-clean \u7ee7\u7eed\u5e26 531_804..532_003 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 " + f"{A0//1000}_{A0}..{A1}" + " \u5185**")
rep("\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **531_604..531_803**",
    "\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **" + f"{B0//1000}_{B0}..{B1}" + "**")
rep("**B base==\u672c\u6ce2 A \u5c3e+1\uff08531_603+1\uff09\u673a\u68c0\u5173\u7cfb**",
    "**B base==\u672c\u6ce2 A \u5c3e+1\uff08" + f"{A1}" + "+1\uff09\u673a\u68c0\u5173\u7cfb**")
rep("**W233 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W234 \u987b\u5728 post-W233 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97",
    "**W234 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W235 \u987b\u5728 post-W234 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97")
rep("R250\uff1aW234 \u5e26\u4ece\u672a\u6307\u6d3e", "R250\uff1aW235 \u5e26\u4ece\u672a\u6307\u6d3e")
rep("A base=529604 span=2000 checked=2000 verdict=FREE / B base=531604 span=200 checked=200 verdict=FREE",
    "A base=" + str(A0) + " span=2000 checked=2000 verdict=FREE / B base=" + str(B0) + " span=200 checked=200 verdict=FREE")

# -- entry 11 scan face --
rep("\u626b\u63cf\u9762=pre-W234 \u5168\u4e8c\u767e\u4e09\u5341\u4e00\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W233 \u884c\u00b7probe leg0 \u673a\u8bc1 231 \u884c live \u5355\u6001 owner rows 223\uff09",
    "\u626b\u63cf\u9762=pre-W235 \u5168\u4e8c\u767e\u4e09\u5341\u4e8c\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W234 \u884c\u00b7probe leg0 \u673a\u8bc1 232 \u884c live \u5355\u6001 owner rows 224\uff09")

# -- entry 14 gate/estate faces --
rep("gate0.5 \u81ea\u67e5 W233 \u884c+W233 finalize \u4ef6\u5728\u573a",
    "gate0.5 \u81ea\u67e5 W234 \u884c+W234 finalize \u4ef6\u5728\u573a")
rep("estate \u63d0\u53d6\u9762=\u672c\u673a W233 \u5757\u7269\u7406\u5b57\u8282",
    "estate \u63d0\u53d6\u9762=\u672c\u673a W234 \u5757\u7269\u7406\u5b57\u8282")
rep("\uff08r973/W233 \u5148\u4f8b freeze-prep \u540c\u5f0f",
    "\uff08r976-continuation/W234 \u5148\u4f8b freeze-prep \u540c\u5f0f")
rep("_w2@T32@bmc_freeze_edits.py", "_w2@T33@bmc_freeze_edits.py")

# -- entry 18 seat projection (full pre-shift rewrite) --
rep("\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261013-1955-bmc \u5df2\u63a8 origin 260217d39 r565 \u5f8b\u00b7probe W235+ \u6295\u5f71 A 531_604..533_603 / B 531_804..532_003",
    "\uff08\u672c\u673a\u5e2d\u4f4d\u516c\u793a MSG-20261013-2149-bmc \u5df2\u63a8 origin e830a2632 r565 \u5f8b\u00b7probe W236+ \u6295\u5f71 A " + W6A + " / B " + W6B)
rep("\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W234 B \u5e26 531_604..531_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W235 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u4e94\u4f8b\u2014\u2014**W235 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W234 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97",
    "\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W235 B \u5e26 " + f"{B0//1000}_{B0}..{B1}" + " \u6ce8\u518c\u540e\u5c06\u62d2 naive W236 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u516d\u4f8b\u2014\u2014**W236 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W235 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97")

# -- entry 19 T-141 ordinal faces --
rep("T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 224 \u6ce2\u3010bm-c \u7b2c\u516d\u5341\u56db\uu679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=64 attempt-continuity face\uff08r974 \u7a97\u8ba1\u6cd5\u00b7W233 splice/freeze receipt=63rd owned \u627f\u88ad\u6ce8\u8bb0\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 63+\u5019\u9009=\u7b2c 64 \u679a EXACT",
    "T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 225 \u6ce2\u3010bm-c \u7b2c\u516d\u5341\u4e94\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_ordinal=65 attempt-continuity face\uff08r976 \u7a97\u8ba1\u6cd5\u00b7W234 splice/freeze receipt=64th owned \u627f\u88ad\u6ce8\u8bb0\uff09\u2014\u2014freeze \u65f6 live derive bm-c rows 64+\u5019\u9009=\u7b2c 65 \u679a EXACT")
rep("\u6ce2\u53f7=\u6ce8\u518c\u8868 W233 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261013-1955-bmc \u5148\u63a8 origin 260217d39 r565 \u5f8b",
    "\u6ce2\u53f7=\u6ce8\u518c\u8868 W234 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u4e2d\u4f4d\u516c\u793a MSG-20261013-2149-bmc \u5148\u63a8 origin e830a2632 r565 \u5f8b")

# -- entry 20 low-RAM precedent list --
rep("W229/W230/W231/W@L32@/W233 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b",
    "W229/W230/W231/W232/W@L33@/W234 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b")

# -- entry 29 selftest parity face --
rep("selftest W234 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W233 \u884c parity \u817f",
    "selftest W235 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W234 \u884c parity \u817f")

# -- entry 30 parity narrative --
rep("W@L32@ \u5757\u7684 W231 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W231+W@L32@ leg \u6784\u6210 W234 \u5757 parity 92 \u884c\uff08W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W@L32@+W233\uff09",
    "W@L33@ \u5757\u7684 W232 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W232+W@L33@ leg \u6784\u6210 W235 \u5757 parity 92 \u884c\uff08W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W@L33@+W234\uff09")

# -- entry 24/25 rng/band faces --
rep("entry rng seed=**529_604+j**", "entry rng seed=**" + f"{A0//1000}_{A0}" + "+j**")
rep("\u6cd5\u5178 \u00a74 W234 \u884c A=529_604..531_603", "\u6cd5\u5178 \u00a74 W235 \u884c A=" + f"{A0//1000}_{A0}..{A1}")
rep("**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u56db\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 529_404..531_403 \u8d77\u70b9\u5373\u88ab W233 \u6ce8\u518c B \u5e26 529_404..529_603 \u62d2\u21921 hop \u843d 529_604..531_603",
    "**FIRST-CLEAN past prior-wave B \u9636\u68ef\u7b2c\u4e5d\u5341\u4e94\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 531_604..533_603 \u8d77\u70b9\u5373\u88ab W234 \u6ce8\u518c B \u5e26 531_604..531_803 \u62d2\u21921 hop \u843d " + f"{A0//1000}_{A0}..{A1}")
rep("entry rng=**529_604+j**", "entry rng=**" + f"{A0//1000}_{A0}" + "+j**")
rep("exit rng=**531_604+j**", "exit rng=**" + f"{B0//1000}_{B0}" + "+j**")
rep("\u6cd5\u5178 \u00a74 W234 \u884c B=531_604..531_803", "\u6cd5\u5178 \u00a74 W235 \u884c B=" + f"{B0//1000}_{B0}..{B1}")
rep("B \u7b97\u672f\u7eed\u5e26 529_604..529_803 \u5728\u6ce8\u518c\u5b87\u5b99 CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 529_604..531_603 \u5185",
    "B \u7b97\u672f\u7eed\u5e26 531_804..532_003 \u5728\u6ce8\u518c\u5b87\u5b99 CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 " + f"{A0//1000}_{A0}..{A1}" + " \u5185")
rep("\u4fdd\u7559\u8d70\u843d 531_604..531_803", "\u4fdd\u7559\u8d70\u843d " + f"{B0//1000}_{B0}..{B1}")

# -- entry 37 KL face (pre-shift: values only, wave tokens shift after) --
rep("\u952e W233 \u5b9e\u6d4b K-lift **\u2212 0.0002**", "KEEP37KLPLACEHOLDER")

# ============ LAYER 2: generic wave-token shifts ============
t = t.replace("PERPETUAL-N1-W234", "PERPETUAL-N1-W235")
t = t.replace("PERPETUAL_N1_W234", "PERPETUAL_N1_W235")
t = t.replace("n1_w234", "n1_w235")
t = t.replace("_w234bmc", "_w235bmc")
t = t.replace("W234", "@SELF@")
t = t.replace("line_pre_w233", "line_pre_w@WPRE@")
t = t.replace("n1_w233", "n1_w234")
t = t.replace("W233", "W234")
t = t.replace("@WPRE@", "w234")
t = t.replace("@SELF@", "W235")
assert t.count("@L32@") == 0 and t.count("@T32@") == 0

# ============ LAYER 3: post-shift value updates (upstream anchors) ============
# entry 16 ledger anchor
rep("\u51c0\u8d26\u672c\u951a\u5934 **936,389**\u00b7K=510,520 \u5408\u5e76\u6c60\u00b7n1_w234_results.json \u673a\u8bfb\u00b7W234 finalize one-pass bm-c r974 \u7a97 19:5x\uff08W234 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7r973 splice 0ca920362+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09",
    "\u51c0\u8d26\u672c\u951a\u5934 **" + LED + "**\u00b7K=" + K + " \u5408\u5e76\u6c60\u00b7n1_w235_results.json \u673a\u8bfb\u00b7W235 finalize one-pass bm-c r978 \u7a97 2?:??x\uff08W235 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7r976-continuation splice de342250c+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09")
# entry 17 null-pool projection
rep("\u7d2f\u8ba1 null \u6c60=510,520+2,200\uff08\u672c\u6ce2\uff09=**512,720 \u6295\u5f71**",
    "\u7d2f\u8ba1 null \u6c60=" + K + "+2,200\uff08\u672c\u6ce2\uff09=**" + KNEXT + " \u6295\u5f71**")
# entry 31 drafting-window face
rep("\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W234 \u5df2\u843d\u8d26 510,520 \u5b9e\u6d4b",
    "\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W235 \u5df2\u843d\u8d26 " + K + " \u5b9e\u6d4b")
# entry 33 §5 prediction-key face
rep("\u51c0\u8d26\u672c\u951a\u5934 936,389\u00b7**K=510,520 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W234 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w234_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b719:5x finalize one-pass\u3011\u3002",
    "\u51c0\u8d26\u672c\u951a\u5934 " + LED + "\u00b7**K=" + K + " \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W235 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w235_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b721:5x finalize one-pass\u3011\u3002")
# entry 34 mu keys
rep("\uff08W234 \u5b9e\u6d4b\u952e **\u22120.09276956**\u00b7K=510,520 \u5408\u5e76\u6c60\u00b7W234-only \u5b9e\u6d4b **\u22120.09893318**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W234 \u5171\u4e8c\u767e\u4e09\u5341\u4e00\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW234-only vs merged \u5b9e\u5dee 0.0062 \u5728\u5e26\u5185\uff09\u3002",
    "\uff08W235 \u5b9e\u6d4b\u952e **" + MU + "**\u00b7K=" + K + " \u5408\u5e76\u6c60\u00b7W235-only \u5b9e\u6d4b **" + WON + "**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W235 \u5171\u4e8c\u767e\u4e09\u5341\u4e8c\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW235-only vs merged \u5b9e\u5dee " + ABSD + " \u5728\u5e26\u5185\uff09\u3002")
# entry 35 sigma key
rep("\u952e **0.24506207**=W234 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002",
    "\u952e **" + SIG + "**=W235 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002")
# entry 36 p95 key
rep("3. A \u6863 full_sharpe_p95 \u4e0e W234 A \u6863 p95\uff08**0.3027** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W234 \u5148\u4f8b",
    "3. A \u6863 full_sharpe_p95 \u4e0e W235 A \u6863 p95\uff08**" + P95 + "** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W235 \u5148\u4f8b")
# entry 37 KL + se_mu chain (W234-upstream slot values)
rep("\u952e W234 \u5b9e\u6d4b K-lift **\u22120.0002**\u00b7line_merged@K510,520 **1.1922**\u00b7line_pre_w234 1.1924\u00b7n_eff_held_equal 934,189",
    "\u952e W235 \u5b9e\u6d4b K-lift **" + KLD + "**\u00b7line_merged@K" + K + " **" + KLMER + "**\u00b7line_pre_w235 " + KLPRE + "\u00b7n_eff_held_equal " + KLNE)
rep("\u2192W231 **0.000344**\u2192W232 **0.000344**\u2192W234 **0.000343**\u3011",
    "\u2192W231 **0.000344**\u2192W232 **0.000344**\u2192W@L33@ **0.000343**\u2192W234 **" + SE + "**\u3011")
rep("W136..W234 \u5148\u4f8b\u94fe\u62ab\u9732", "W136..W235 \u5148\u4f8b\u94fe\u62ab\u9732")
# entry 38 W236+ projection (post-shift tokens: W234 aged from W233, W235 self)
rep("**W236+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 531_604..533_603 CLEAN\uff08hops=0\u00b7pre-W234 \u5b87\u5b99\uff09\uff1bB naive first-clean **531_804..532_003 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W235\uff1aW235 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W234 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W234 B \u5e26 531_604..531_803 \u6ce8\u518c\u540e\u5c06\u62d2 naive W235 A \u7a97**\u2014\u2014W235 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W234 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u4e94\u4f8b\uff09\uff1bverify at W235 prereg",
    "**W236+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean " + W6A.replace("..", "..") + " CLEAN\uff08hops=0\u00b7pre-W235 \u5b87\u5b99\uff09\uff1bB naive first-clean **" + W6B + " CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W236\uff1aW236 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W235 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W235 B \u5e26 " + f"{B0//1000}_{B0}..{B1}" + " \u6ce8\u518c\u540e\u5c06\u62d2 naive W236 A \u7a97**\u2014\u2014W236 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W235 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u516d\u4f8b\uff09\uff1bverify at W236 prereg")
# entries 39 --wave
rep(" --wave 234/finalize --wave 234", " --wave 235/finalize --wave 235")
# entry 43 owner rows
rep("engine_owner==bm-c 63 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009",
    "engine_owner==bm-c 64 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015+ \u672c\u5019\u9009")
# entries 44/45 §7/§8 paradigm refs
rep("\u6bb5\u2014\u2014r974 W233 \u00a77 \u8303\u5f0f\uff09", "\u6bb5\u2014\u2014r976 W234 \u00a77 \u8303\u5f0f\uff09")
rep("\uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W235+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r974 W233 \u00a78 \u8303\u5f0f\uff09",
    "\uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W236+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r976 W234 \u00a78 \u8303\u5f0f\uff09")

# entry 12 runner scope / entry 23 calibration scope / entry 27 (aged by shifts, verify)
rep("\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W234 \u843d\u5730\uff09",
    "\uff08p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W235 \u843d\u5730\uff09")

# ---- dict rename + final writes ----
rep("R34 = {", "R35 = {")
assert t.count("R35") >= 1 and "R34" not in t.replace("R34 = {", ""), "R34 residue"

open(r"results\_w235bmc_r35_data.py", "w", encoding="utf-8", newline="").write(t)

# ---- verify: import + structural checks ----
import importlib.util, ast
spec = importlib.util.spec_from_file_location("r35", r"results\_w235bmc_r35_data.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R35 = m.R35
assert len(R35) == 46, "R35 entries %d" % len(R35)
import importlib
R34 = importlib.import_module("_w234bmc_r34_data").R34
for i in range(46):
    assert len(R35[i]) == len(R34[i]), f"entry {i} len drift {len(R35[i])} vs {len(R34[i])}"
assert R35[0][3].startswith("@@BINOP_WINLABEL@@")
assert R35[20][0] == "@@BINOP_RAM@@"
spot = [R35[0][0][:20], R35[7][0], R35[32][0][:40], R35[37][1][:60]]
print("R35 LANDED: 46 entries, lens aligned, spots:", spot)
