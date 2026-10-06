# -*- coding: utf-8 -*-
"""r799 bm-a W166 per-wave prereg builder: xform research/PERPETUAL_N1_W165_PREREG.md
-> research/PERPETUAL_N1_W166_PREREG.md (bloodline: r766 xform law, r773 whole-
string tokens, r781 fragment needles; r587 machine values from on-disk
receipts; sec7/8 span-replaced to placeholder per r763/r764 lineage).

Facts (machine-derived, r587 never-transcribe):
  - gate results/_r797bma_w166_band_gate.json ADMIT: A 380_004..382_003
    staircase 25th instance E36 hops=1 (naive 379_804..381_803 refused by
    the W165 B band 379_804..380_003); B 382_004..382_203 own-A hops=1
    (naive 380_004..380_203); W167+ projection A 382_004..384_003 /
    B 382_204..382_403 (naive-B-inside-naive-A).
  - W165 finalize r796 (n1_w165_results.json): merged K=360,920,
    mu -0.092878, sigma 0.245144; W165-only mu -0.092588 (sec7 backfill);
    ledger 766,212+2,200=768,412; skill_line 1.1834->1.1833 (-0.0001);
    A p95 0.3018; se_mu 0.000408.
  - W165 freeze sha aebb94d2d (registered row citation).
  - Seat MSG-2026-10-06-223x-bma-w166-seat on origin d1dc12117 (r797
    pre-seat push, r565 law)."""
import io
import json
import re

SRC = r"research/PERPETUAL_N1_W165_PREREG.md"
DST = r"research/PERPETUAL_N1_W166_PREREG.md"
s = io.open(SRC, encoding="utf-8", newline="").read()

# PHASE 0 -- current-wave bulk roll FIRST (single-pass law: the W165->W166
# roll must consume the SOURCE wave numbers before any needle generates
# new W165 prior-wave citations; needles' OLD strings below are written
# in the post-phase-0 shape)
s = s.replace("W165", "W166")

gate = json.load(open(r"results\_r797bma_w166_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT"
assert leg1["A"] == [380004, 382003] and leg1["B"] == [382004, 382203]
w165 = json.load(open(r"results\perpetual_faces\n1_w165_results.json", encoding="utf-8"))
m = w165["null_pool_cumulative"]["merged"]
assert m["n_values"] == 360920

def rep(old, new, expect=None):
    n = s_count(old) if False else None  # placeholder
    return old, new

# ordered replacement list: (old, new, min_count)
REPL = [
    # --- identity / file names / batch
    # (PERPETUAL_N1_W165_PREREG.md / PERPETUAL-N1-W165 already rolled to
    # the W166 shape by PHASE 0 -- no needles needed)
    ("n1_w165_results.json", "n1_w166_results.json", 2),
    ("n1_w164_results.json", "@N1KEYR@", 1),  # sec5 key roll (token: the
    # n1_w165 residual consumer below would otherwise re-map this output)
    ("n1_w165/", "n1_w166/", 1),
    ("n1_w165", "n1_w166", 0),  # residual
    # --- seat / push session
    ("MSG-2026-10-06-205x-bma-w165-seat", "MSG-2026-10-06-223x-bma-w166-seat", 2),
    ("4bdf63090", "d1dc12117", 2),
    ("（r793 pre-seat push", "（r797 pre-seat push", 1),
    ("r793 pre-seat push", "r797 pre-seat push", 0),
    ("r793 席位 MSG-2026-10-06-205x 投影", "r797 席位 MSG-2026-10-06-223x 投影", 1),
    # --- header ordinal / series
    ("泵第 163 枚", "泵第 164 枚", 1),
    ("engine_owner 行 154+本候选=bm-a 第八十一枚自有波【r795】",
     "engine_owner 行 155+本候选=bm-a 第八十二枚自有波【r799】", 1),
    ("波号 165=注册表 W164 行后首个自由号", "波号 166=注册表 W165 行后首个自由号", 1),
    ("（波号=注册表 W164 行后首个自由号", "（波号=注册表 W165 行后首个自由号", 1),
    # --- single-state roster tail extension
    ("W164=bm-a r792 freeze（f7d34e5a7·表尾）",
     "W164=bm-a r792 freeze（f7d34e5a7）；W165=bm-a r795 freeze（aebb94d2d·表尾）", 1),
    ("**均已注册**（表尾 W164 行）", "**均已注册**（表尾 W165 行）", 1),
    # --- receipts / gate / probe
    ("_r793bma_w165_band_gate.json", "_r797bma_w166_band_gate.json", 2),
    ("_r793bma_w165_probe.py", "_r797bma_w166_probe.py", 1),
    ("_r793bma_w165_probe", "_r797bma_w166_probe", 0),
    ("_r793bma_w165", "_r797bma_w166", 0),
    # --- band geometry (whole strings; W167 projection BEFORE current-wave
    #     bands per r773 whole-string law)
    ("r792 gate leg3", "r793 gate leg3", 2),
    ("r793 sec8 succession", "r796 sec8 succession", 0),
    ("r793 sec8", "r796 sec8", 0),
    ("继承第二十五例", "继承第二十六例", 2),
    ("阶梯第二十四例", "阶梯第二十五例", 2),
    ("阶梯几何第二十四例", "阶梯几何第二十五例", 1),
    ("（r792 冻结件）", "（r795 冻结件）", 1),
    ("A-ext seed=377_804..379_803", "A-ext seed=380_004..382_003", 1),
    ("B-ext exit seed=379_804..380_003", "B-ext exit seed=382_004..382_203", 1),
    ("379_804..381_803", "382_004..384_003", 2),
    ("380_004..380_203", "382_204..382_403", 2),
    ("377_604..379_603", "379_804..381_803", 2),
    # r773 law via mini-token: the W165-B-band citation is collected into
    # @W165BB@ BEFORE the bare-band consumers run, and re-expanded AFTER
    # the whole REPL loop (generator output never re-mapped)
    ("W164 B 带 377_604..377_803", "@XBBTOKEN@", 1),
    ("377_604..377_803", "379_804..380_003", 0),
    ("377_804..378_003", "380_004..380_203", 2),
    ("377_804..379_803", "380_004..382_003", 2),
    ("379_804..380_003", "382_004..382_203", 3),
    ("377_803+1", "380_003+1", 1),
    ("379_803+1", "382_003+1", 1),
    # --- prior-citation roll (W164 session -> W165 session)
    ("W164 finalize one-pass bm-a r793·§7/§8 已回填", "W165 finalize one-pass bm-a r796·§7/§8 已回填", 1),
    ("W164 finalize 落账【one-pass·K=358,720 合并池", "W165 finalize 落账【one-pass·K=360,920 合并池", 1),
    ("落账【one-pass·bm-a r793·§7/§8 已回填】", "落账【one-pass·bm-a r796·§7/§8 已回填】", 1),
    ("W164 席位 W166+ 投影", "W165 席位 W166+ 投影", 2),
    ("W164 行投影散文", "W165 行投影散文", 2),
    # --- ledger / K anchors
    ("净账本锚头 766,212", "净账本锚头 768,412", 1),
    ("358,720+2,200（本波）=**360,920 投影**", "360,920+2,200（本波）=**363,120 投影**", 1),
    ("766,212", "768,412", 0),
    ("358,720", "360,920", 0),
    # --- scan face / rows / ordinals
    ("pre-W166 全一百六十二行", "pre-W166 全一百六十三行", 1),
    ("表尾 W164 行·leg0 机证 162 行", "表尾 W165 行·leg0 机证 163 行", 1),
    ("第 155 波", "第 156 波", 1),
    ("engine_owner==bm-a 行 80+本候选", "engine_owner==bm-a 行 81+本候选", 1),
    ("engine_owner==bm-a 80 行注册", "engine_owner==bm-a 81 行注册", 1),
    ("同 W157/W158/W159/W160/W161/W162/W163/W164 最近自有波",
     "同 W157/W158/W159/W160/W161/W162/W163/W164/W165 最近自有波", 2),
    # --- selftest / freeze-window session
    ("r795 bm-a 冻结窗（pre-seat probe r793 先跑", "r799 bm-a 冻结窗（pre-seat probe r797 先跑", 1),
    # --- §3 seed formulas
    ("entry rng seed=**377_804+j**", "entry rng seed=**380_004+j**", 1),
    ("entry rng=**377_804+j**", "entry rng=**380_004+j**", 1),
    ("exit rng=**379_804+j**", "exit rng=**382_004+j**", 1),
    # --- §5 numeric keys (W165 finalize measured values, r587)
    ("W164-only 实测 **−0.096332**", "W165-only 实测 **−0.092588**", 1),
    ("**0.2452**=W164 合并池实测 0.245172", "**0.2451**=W165 合并池实测 0.245144", 1),
    ("W164 A 档 p95（**0.3106** 实测锚）", "W165 A 档 p95（**0.3018** 实测锚）", 1),
    ("W2..W164 共一百六十三面实测", "W2..W165 共一百六十四面实测", 1),
    ("W161 **+0.0002** 如实披露；", "W161 **+0.0002**/W165 **−0.0001** 如实披露；", 1),
    ("键 W164 实测 K-lift **+0.0001**", "键 W165 实测 K-lift **−0.0001**", 1),
    ("line_pre 1.1832·n_eff 764,012", "line_pre 1.1834·n_eff 766,212", 1),
    ("→W164 **0.000409**】", "→W164 0.000409→W165 **0.000408**】", 1),
    ("适用于 W166：W166 冻结方必须在 post-W166", "适用于 W167：W167 冻结方必须在 post-W166", 1),
    ("naive W166 A 窗", "naive W167 A 窗", 1),
    ("W166 A 重 derive", "W167 A 重 derive", 1),
    ("verify at W166 prereg", "verify at W167 prereg", 1),
    ("待 W166 注册宇宙复核", "待 W167 注册宇宙复核", 1),
    # --- §6 runner faces
    ("--wave 165", "--wave 166", 2),
    # --- wave-number roll (post-phase-0 shapes: projection phrases use
    # exact-context needles so the 'W164 席位 W166+ 投影' generator output
    # is never re-mapped; prior-wave bulk roll runs LAST -- its W165
    # outputs are immune because every W165-targeting needle has run)
    ("投影 W166+ A", "投影 W167+ A", 1),
    ("W166+ 投影（gate 机证", "W167+ 投影（gate 机证", 1),
    ("W1..W164", "W1..W165", 2),
    ("W2..W164", "W2..W165", 3),
    ("W164", "W165", 1),   # prior-wave bulk roll (>=1)
    # --- bare numerals: NOT needed (all bare-165 faces carry dedicated
    # needles above: --wave 165 -> --wave 166; a generic bare pass would
    # tear the W165/W164 bulk-roll outputs -- r789 two-phase law note)
]

counts_ok = []
for old, new, mn in REPL:
    c = s.count(old)
    assert c >= mn, f"needle undercount {c}<{mn}: {old[:60]!r}"
    s = s.replace(old, new)
    counts_ok.append((old[:40], c))

# mini-BACK: re-expand the collected tokens (after all consumer needles
# have run -- r773 two-phase law)
assert s.count("@XBBTOKEN@") == 1, "XBB token count drift"
s = s.replace("@XBBTOKEN@", "W165 B 带 379_804..380_003")
assert s.count("@N1KEYR@") == 1, "N1KEYR token count drift"
s = s.replace("@N1KEYR@", "n1_w165_results.json")

# --- sec7/8 span-replace to placeholder (r763/r764 lineage) -----------------
i7 = s.find("## §7 跑后实证。")
i_tail = s.find("- **跑前冻结=本件 commit**")
assert 0 < i7 < i_tail, "sec7/tail anchors missing"
PLACEHOLDER = """## §7 跑后实证。【finalize 收口机械回填·待 W166 finalize 窗】
- 占位：本节由 W166 finalize 收口窗按 results/perpetual_faces/n1_w166_results.json 机读键回填（r381 范式·r763/r764 血统；回填限本两节·判据零改·禁看结果调线）。

## §8 批后复盘。【finalize 同窗回填·待 W166 finalize 窗】
- 占位：§5.5 W167+ 投影承接复核（阶梯 A-hops-prior-B 继承第二十六例待 W167 注册宇宙复核）+ 宝藏/方法论捕获问 + 诚实披露面（W165 例：K-lift −0.0001 如实）。

"""
s = s[:i7] + PLACEHOLDER + s[i_tail:]

# --- post-xform assertions ------------------------------------------------------
assert "PERPETUAL-N1-W166" in s and "PERPETUAL_N1_W166_PREREG.md" in s
for stale in ("377_604", "377_804", "378_003", "377_803", "锚头 766,212", "358,720",
              "379_603", "379_803", "f7d34e5a7·表尾", "4bdf63090", "0.245172",
              "0.3106", "−0.096332", "n1_w165/", "bma-w165-seat"):
    assert stale not in s, f"stale residue {stale!r} in W166 prereg"
# the §5 drafting-window key citation legitimately references the W165
# finalize results file (latest landed keys at drafting time)
assert "perpetual_faces/n1_w165_results.json" in s, \
    "sec5 W165 key citation missing"
assert "380_004..382_003" in s and "382_004..382_203" in s
assert "379_804..380_003" in s  # W165 B band citation (prior-wave refuse face)
assert "382_004..384_003" in s and "382_204..382_403" in s  # W167 projection
assert "768,412" in s and "360,920" in s and "363,120" in s
assert s.count("W166") >= 25 and s.count("W165") >= 30
# malformed-window scan (r773 leg 3)
bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", s)
       if int(m.group(3)) < int(m.group(1))]
assert not bad, f"malformed windows in W166 prereg: {bad[:4]}"
io.open(DST, "w", encoding="utf-8", newline="").write(s)
print(f"W166 prereg built: {len(s)} bytes, {len(REPL)} ordered needles, "
      f"sec7/8 span-replaced placeholder, malformed-scan CLEAN")
