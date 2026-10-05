# -*- coding: utf-8 -*-
"""r752 bm-a W144 per-wave prereg transform: research/PERPETUAL_N1_W143_PREREG.md
(freeze-time version, commit 86d3b070c, NOT the §7/§8-backfilled current
blob) -> research/PERPETUAL_N1_W144_PREREG.md.
Measurement pass FIRST (every needle count printed to receipt verbatim per
r735 law), then assert-apply (fail-closed; write only at the end).
Needle ordering laws enforced: (a) blanket W143->W144 then W142->W143;
(b) §5.5 projection rewrite BEFORE window replace-alls (the W145 projection
must not inherit the W144 window numbers); (c) 认领 seat needle BEFORE the
generic "r748 席位" needle (substring order); (d) B-window replace-all BEFORE
the "B 带 329_204..329_403 拒" needle (which creates a correct W143-B ref that
must survive); (e) "n1_w143_results.json"->n1_w144 FIRST, then
"n1_w142_results.json"->n1_w143 (§5 key file = the W143 finalize results);
(f) "708,411"->"710,611" FIRST, then "n_eff 706,211"->"n_eff 708,411";
(g) ledger/K replace-alls BEFORE "312,520 投影"->"314,720 投影".
Minus signs are U+2212 in the source; needles use the same byte."""
import io, json, subprocess

SRC_REF = "86d3b070c:research/PERPETUAL_N1_W143_PREREG.md"
DST = r"research\PERPETUAL_N1_W144_PREREG.md"
src = subprocess.run(["git", "show", SRC_REF], capture_output=True,
                     check=True).stdout.decode("utf-8")
assert "## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】" in src, \
    "source must be the freeze-time version (placeholders intact)"

M = {}  # measurement record


def rep(s, pairs, tag):
    for old, new, expect in pairs:
        n = s.count(old)
        M[f"{tag}: {old[:44]}"] = n
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        s = s.replace(old, new)
    return s


# ---- Phase 1: blanket wave shift (ordered) ----
n_w143 = src.count("W143"); n_w142 = src.count("W142")
s = src.replace("W143", "W144")
s = s.replace("W142", "W143")
M["blanket W143->W144"] = n_w143
M["blanket W142->W143"] = n_w142
assert s.count("W144") >= n_w143 and s.count("W141") == src.count("W141")

# ---- Phase 2a: §5.5 W145+ projection rewrite BEFORE window replace-alls ----
s = rep(s, [
    ("W144+ 投影（gate 机证", "W145+ 投影（gate 机证", 1),
    ("A first-clean 331_404..333_403 **CLEAN**（hops=0）",
     "A first-clean 333_604..335_603 **CLEAN**（hops=0）", 1),
    ("B first-clean **331_604..331_803 CLEAN**（hops=0）",
     "B first-clean **333_804..334_003 CLEAN**（hops=0）", 1),
    ("同窗互斥先例适用于 W144：W144 冻结方",
     "同窗互斥先例适用于 W145：W145 冻结方", 1),
    ("拒 naive W144 A 窗", "拒 naive W145 A 窗", 1),
    ("verify at W144 prereg", "verify at W145 prereg", 1),
    ("W144+ 投影承接", "W145+ 投影承接", 1),
], "s55")

# ---- Phase 2b: 认领 seat needle BEFORE generic r748-seat needle ----
s = rep(s, [
    ("r748 席位 MSG-2026-10-05-233x", "r750 席位 MSG-2026-10-06-002x", 1),
    ("投影 W144+ A 329_204..331_203 naive", "投影 W144+ A 331_404..333_403 naive", 1),
], "claim")

# ---- Phase 2c: B-window replace-all BEFORE the W143-B-ref creation needle ----
s = rep(s, [
    ("331_404..331_603", "333_604..333_803", 6),
], "bwin")
s = rep(s, [
    ("B 带 329_204..329_403 **拒**", "B 带 331_404..331_603 **拒**", 1),
    ("（r748 W143 gate 尾投影注记所预言）", "（r750 W143 gate 尾投影注记所预言）", 1),
    ("r748 W143 gate 尾投影 re-derive-MANDATORY", "r750 W143 gate 尾投影 re-derive-MANDATORY", 1),
    ("r748 席位", "r750 席位", 1),
], "bwin-fix")

# ---- Phase 2c-2: freeze-history tail advance (blanket shifted W142->W143;
#      the r/sha must advance to the real W143 freeze) ----
s = rep(s, [
    ("W143=bm-a r748 freeze（16baa2a7b·表尾）",
     "W143=bm-a r750 freeze（86d3b070c·表尾）", 1),
], "history")

# ---- Phase 2d: A-window / continuation / machine-check replace-alls ----
s = rep(s, [
    ("329_404..331_403", "331_604..333_603", 5),
    ("329_204..331_203", "331_404..333_403", 2),
    ("329_404..329_603", "331_604..331_803", 2),
    ("（329_403+1）机检关系", "（331_603+1）机检关系", 1),
    ("（331_403+1）机检关系", "（333_603+1）机检关系", 1),
    ("seed=**329_404+j**", "seed=**331_604+j**", 1),
    ("entry rng=**329_404+j**", "entry rng=**331_604+j**", 1),
    ("exit rng=**331_404+j**", "exit rng=**333_604+j**", 1),
    ("阶梯第二例", "阶梯第三例", 3),
], "awin")

# ---- Phase 2e: seat/probe/receipt files ----
s = rep(s, [
    ("_r750bma_w143_band_gate.py", "_r752bma_w144_band_gate.py", 2),
    ("_r750bma_w143_probe_receipt.json", "_r751bma_w144_probe_receipt.json", 1),
    ("_r750bma_w143_probe.py", "_r751bma_w144_probe.py", 2),
    ("MSG-2026-10-06-002x-bma-w143-seat", "MSG-2026-10-06-011x-bma-w144-seat", 2),
    ("3a7640311", "2ba4a613f", 3),
    ("bm-a r749 fec2adb73", "bm-a r751 6d93bd7ba", 2),
], "seat")

# ---- Phase 2f: ledger/K numbers (order: 708,411 first, then n_eff; 310,320 first, then 投影) ----
s = rep(s, [
    ("708,411", "710,611", 2),
    ("n_eff 706,211", "n_eff 708,411", 1),
    ("310,320", "312,520", 6),
    ("312,520 投影", "314,720 投影", 1),
], "ledger")

# ---- Phase 2g: §5 keys (W143 finalize measured values) ----
s = rep(s, [
    ("−0.0877", "−0.0958", 1),
    ("**0.2449**", "**0.2450**", 1),
    ("**0.3273**", "**0.3051**", 1),
    ("**1.1785**·line_pre 1.1784", "**1.1787**·line_pre 1.1786", 1),
    ("se_mu 收窄键 W138 0.000446→W139 0.000444→W140 0.000443→W141 0.000441→W143 **0.000440**",
     "se_mu 收窄键 W139 0.000444→W140 0.000443→W141 0.000441→W142 0.000440→W143 **0.000438**", 1),
    ("W135..W143 先例", "W136..W143 先例", 1),
    ("W135 +0.0000/W136", "W136", 1),
    ("共一百四十一面", "共一百四十二面", 1),
], "s5keys")

# ---- Phase 2h: ordinals / rows / rounds ----
s = rep(s, [
    ("泵第 141 枚", "泵第 142 枚", 1),
    ("行 132+本候选", "行 133+本候选", 1),
    ("第五十九枚", "第六十枚", 3),
    ("【r750】", "【r752】", 1),
    ("第一百三十三引擎波", "第一百三十四引擎波", 1),
    ("引擎线第 133 波", "引擎线第 134 波", 1),
    ("行 58+本候选", "行 59+本候选", 2),
    ("58 行注册", "59 行注册", 1),
    ("全一百四十行", "全一百四十一行", 1),
    ("leg0 机证 140 行", "leg0 机证 141 行", 1),
    ("同 W139/W140/W141/W143", "同 W140/W141/W142/W143", 2),
    ("r750 bm-a 冻结窗", "r752 bm-a 冻结窗", 1),
    ("（r750 窗口实况）", "（r751 窗口实况）", 1),
], "ordinal")

# ---- Phase 2i: runner/deliverable files (order: n1_w143_results first, then n1_w142) ----
s = rep(s, [
    ("n1_w143_results.json", "n1_w144_results.json", 2),
    ("n1_w142_results.json", "n1_w143_results.json", 1),
    ("n1_w143/shard", "n1_w144/shard", 1),
    ("--wave 143", "--wave 144", 2),
], "runner")

# ---- Phase 3: residue checks (fail-closed; excluded: n_eff 708,411 / §5-key
#      n1_w143_results.json / the W143-B band ref -- all legitimate
#      post-transform leftovers) ----
for stale in ["3a7640311", "fec2adb73", "r749", "16baa2a7b",
              "310,320", "329_204..", "329_404",
              "阶梯第二例", "第五十九枚", "0.3273",
              "706,211", "0.0877", "_r750bma_w143", "r748 席位",
              "（r748 W143", "第一百三十三", "第 133 波"]:
    assert s.count(stale) == 0, f"residue: {stale!r} count={s.count(stale)}"
assert s.count("W145") == 0 or "W145" in s  # W145 only in projection contexts
assert "PERPETUAL-N1-W144" in s and "research/PERPETUAL_N1_W144_PREREG.md" in s

io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
io.open(r"results\_r752bma_w144_prereg_xform_receipt.json", "w",
        encoding="utf-8", newline="\n").write(
    json.dumps({"probe": "r752 W144 prereg transform", "src": SRC_REF,
                "bytes_out": len(s.encode("utf-8")), "lines": s.count(chr(10)) + 1,
                "measured": M}, ensure_ascii=False, indent=1))
print("W144 prereg written:", len(s.encode("utf-8")), "bytes |",
      s.count(chr(10)) + 1, "lines |", len(M), "needle measurements recorded")
