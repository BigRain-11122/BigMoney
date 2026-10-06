# -*- coding: utf-8 -*-
"""r794 bm-a W165 per-wave prereg builder: research/PERPETUAL_N1_W165_PREREG.md
from the W164 FROZEN-time prereg (git show f7d34e5a7 -- pre-backfill version).

r773 pit-law compliance: two-pass sentinel vmap (TOK then BACK) -- no output
can ever be re-mapped; every band/projection value machine-derived from the
r794 gate + probe receipts and the W164 finalize results JSON (r587
never-transcribe); composite strings tokenized WHOLE; bare numerals LAST.
"""
import io, json, subprocess, sys

# --- machine facts (r587) -------------------------------------------------------
gate = json.load(open("results/_r793bma_w165_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "380004_382003", "B": "382004_382203"}, gate["bands"]
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert leg1["A"] == [377804, 379803] and leg1["B"] == [379804, 380003]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [377604, 379603] and leg1["ARITH_B"] == [377804, 378003]
assert leg1["B_naive_first_clean"] == [377804, 378003]
assert leg3["W166p_A"] == "379804..381803" and leg3["W166p_B"] == "380004..380203"
w164 = json.load(open("results/perpetual_faces/n1_w164_results.json", encoding="utf-8"))
m = w164["null_pool_cumulative"]["merged"]
own = w164["null_pool_cumulative"]["w164_only"]
led = w164["science_gates"]["ledger"]
assert m["n_values"] == 358720 and led["total"] == 766212 and led["prev_total"] == 764012
assert round(m["mu"], 4) == -0.0929 and round(own["mu"], 6) == -0.096332
assert m["sigma"] == 0.2451720171066556 and own["sigma"] == 0.24661726077929613
assert w164["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3106
sk = w164["skill_line_v2_k_lift"]
assert sk["line_merged_358720"] == 1.1833 and sk["line_pre_w164"] == 1.1832
assert sk["line_delta_k_lift"] == 0.0001 and sk["n_eff_held_equal"] == 764012
assert w164["null_pool_cumulative"]["se_mu_at_k358720"] == 0.000409
raw = subprocess.run(["git", "show", "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md"],
                     capture_output=True).stdout
assert len(raw) == 19071
frozen = raw.decode("utf-8")
assert "## §7 跑后实证。【finalize 收口机械回填·待跑后】" in frozen

# --- pass 1: source -> tokens (ordered; composites first, bare numerals last) ---
TOK = [
    # §5 key 5 whole-paragraph composite (gate leg3 verbatim for W166+)
    ("5. **W165+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 377_604..379_603 **CLEAN**（hops=0）；B first-clean **377_804..378_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W165：W165 冻结方必须在 post-W164 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W164 B 带 377_604..377_803 注册后将拒 naive W165 A 窗**——W165 A 重 derive 同强制（越过 W164 B 带·阶梯 A-hops-prior-B 继承第二十四例）；verify at W165 prereg，hop 链逐跳在 probe 回执。",
     "@S5K5@"),
    # §0 claim-composite (own-seat W165+ projection -> W166+ per this seat's gate tail)
    ("投影 W165+ A 377_604..379_603 naive/B 377_804..378_003 naive",
     "@S0PROJ@"),
    ("待 W165 注册宇宙复核", "@S0REV@"),
    # §8 placeholder composite
    ("W165+ 投影承接", "@S8PROJ@"),
    # registered-row tail entry (historical W163 row keeps r789+18231a529; 表尾 moves to new W164 row)
    ("W163=bm-a r789 freeze（18231a529·表尾）；**均已注册**（表尾 W163 行）",
     "@TAIL@"),
    # §5 preamble anchor citation file
    ("n1_w163_results.json", "@ANCHORF@"),
    # stats composites
    ("K-lift **+0.0002**【line_merged@K356,520 **1.1831**·line_pre 1.1829", "@KLC@"),
    ("W162 0.000412\u2192W163 **0.000411**", "@SEC@"),
    ("0.2452**=W163 合并池实测 0.245163", "@SIGC@"),
    ("\u22120.088982", "@OWMU@"),
    ("0.3259", "@AP95@"),
    ("n_eff 761,812", "@NEFF@"),
    # ordinal / row-count composites
    ("第 162 枚", "@ORDP@"),
    ("第 154 波【bm-a 第八十枚自有波", "@ORDW@"),
    ("engine_owner 行 154+本候选=bm-a 第八十枚自有波【r792】", "@ORDT@"),
    ("engine_owner==bm-a 行 79+本候选", "@ORDA@"),
    ("engine_owner==bm-a 79 行注册 + 本候选", "@ORDB@"),
    ("同 W156/W157/W158/W159/W160/W161/W162/W163 最近自有波", "@ORDL@"),
    ("共一百六十二面实测", "@ORDC@"),
    ("全一百六十一行注册 N1 带表（表尾 W163 行·leg0 机证 161 行）", "@ORDR@"),
    ("波号 164=注册表 W163 行后首个自由号", "@WNUM@"),
    ("累计 null 池=356,520+2,200（本波）=**358,720 投影**", "@PROJC@"),
    # staircase ordinals
    ("阶梯第二十三例", "@ST22@"),
    ("阶梯几何第二十三例", "@STG22@"),
    # seat / push shas
    ("MSG-2026-10-06-194x", "@SEATX@"),
    ("469d40896", "@SEATSHA@"),
    # band geometry (own bands, naive windows, prior band, base relations)
    ("375_604..377_603", "@ABAND@"),
    ("377_604..377_803", "@BBAND@"),
    ("375_404..377_403", "@NABAND@"),
    ("375_604..375_803", "@NBBAND@"),
    ("375_404..375_603", "@PBAND@"),
    ("375_603+1", "@ABASE@"),
    ("377_603+1", "@BBASE@"),
    ("375_604+j", "@ASEED@"),
    ("377_604+j", "@BSEED@"),
    # ledger / K numbers
    ("764,012", "@LHEAD@"),
    ("356,520", "@KOLD@"),
    # session blankets
    ("r789", "@R787@"),
    ("r790", "@R788@"),
    ("r792", "@R789@"),
    # lowercase artifact names (own-wave)
    ("w164", "@LW@"),
    # wave-number blankets (prior-wave + own-wave)
    ("W163", "@PW@"),
    ("W164", "@OW@"),
    # bare numerals LAST
    ("--wave 164", "@RUNW@"),
    ("164", "@BARE@"),
]

BACK = [
    ("@S5K5@", "5. **W166+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 379_804..381_803 **CLEAN**（hops=0）；B first-clean **380_004..380_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W166：W166 冻结方必须在 post-W165 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W165 B 带 379_804..380_003 注册后将拒 naive W166 A 窗**——W166 A 重 derive 同强制（越过 W165 B 带·阶梯 A-hops-prior-B 继承第二十五例）；verify at W166 prereg，hop 链逐跳在 probe 回执。"),
    ("@S0PROJ@", "投影 W166+ A 379_804..381_803 naive/B 380_004..380_203 naive"),
    ("@S0REV@", "待 W166 注册宇宙复核"),
    ("@S8PROJ@", "W166+ 投影承接"),
    ("@TAIL@", "W163=bm-a r789 freeze（18231a529）；W164=bm-a r792 freeze（f7d34e5a7·表尾）；**均已注册**（表尾 W164 行）"),
    ("@ANCHORF@", "n1_w164_results.json"),
    ("@KLC@", "K-lift **+0.0001**【line_merged@K358,720 **1.1833**·line_pre 1.1832"),
    ("@SEC@", "W162 0.000412\u2192W163 0.000411\u2192W164 **0.000409**"),
    ("@SIGC@", "0.2452**=W164 合并池实测 0.245172"),
    ("@OWMU@", "\u22120.096332"),
    ("@AP95@", "0.3106"),
    ("@NEFF@", "n_eff 764,012"),
    ("@ORDP@", "第 163 枚"),
    ("@ORDW@", "第 155 波【bm-a 第八十一枚自有波"),
    ("@ORDT@", "engine_owner 行 154+本候选=bm-a 第八十一枚自有波【r794】"),
    ("@ORDA@", "engine_owner==bm-a 行 80+本候选"),
    ("@ORDB@", "engine_owner==bm-a 80 行注册 + 本候选"),
    ("@ORDL@", "同 W157/W158/W159/W160/W161/W162/W163/W164 最近自有波"),
    ("@ORDC@", "共一百六十三面实测"),
    ("@ORDR@", "全一百六十二行注册 N1 带表（表尾 W164 行·leg0 机证 162 行）"),
    ("@WNUM@", "波号 165=注册表 W164 行后首个自由号"),
    ("@PROJC@", "累计 null 池=358,720+2,200（本波）=**360,920 投影**"),
    ("@ST22@", "阶梯第二十四例"),
    ("@STG22@", "阶梯几何第二十四例"),
    ("@SEATX@", "MSG-2026-10-06-205x"),
    ("@SEATSHA@", "4bdf63090"),
    ("@ABAND@", "377_804..379_803"),
    ("@BBAND@", "379_804..380_003"),
    ("@NABAND@", "377_604..379_603"),
    ("@NBBAND@", "377_804..378_003"),
    ("@PBAND@", "377_604..377_803"),
    ("@ABASE@", "377_803+1"),
    ("@BBASE@", "379_803+1"),
    ("@ASEED@", "377_804+j"),
    ("@BSEED@", "379_804+j"),
    ("@LHEAD@", "766,212"),
    ("@KOLD@", "358,720"),
    ("@R787@", "r792"),
    ("@R788@", "r793"),
    ("@R789@", "r794"),
    ("@LW@", "w165"),
    ("@PW@", "W164"),
    ("@OW@", "W165"),
    ("@RUNW@", "--wave 165"),
    ("@BARE@", "165"),
]


def vmap(s):
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


src = frozen
EXPECT = {  # exact per-token source counts (empirically rebuilt)
    "r789": 5,
    "r790": 2,
    "r792": 10,
    "W163": 38,
    "W164": 24,
    "w164": 9,
    "164": 36,
    "MSG-2026-10-06-194x": 3,
    "469d40896": 3,
    "375_604..377_603": 4,
    "377_604..377_803": 5,
    "375_404..377_403": 2,
    "375_604..375_803": 2,
    "375_404..375_603": 1,
    "375_603+1": 1,
    "377_603+1": 1,
    "375_604+j": 2,
    "377_604+j": 1,
    "764,012": 2,
    "356,520": 6,
    "--wave 164": 2,
    "阶梯第二十三例": 2,
}
W156L = "同 W156/W157/W158/W159/W160/W161/W162/W163 最近自有波"
for i, (old, tok) in enumerate(TOK):
    n = src.count(old)
    want = EXPECT.get(old, 1)
    if old == W156L:
        want = 2
    assert n == want, f"TOK {i} count={n} != {want}: {old[:60]!r}"
out = vmap(src)

# --- output assertions -----------------------------------------------------------
checks = [
    ("377_804..379_803", 4), ("379_804..380_003", 5), ("377_604..379_603", 2),
    ("377_804..378_003", 2), ("377_604..377_803", 1),
    ("375_404..377_403", 0), ("375_604..375_803", 0), ("375_404..375_603", 0),
    ("375_604..377_603", 0), ("375_603+1", 0), ("377_603+1", 0),
    ("377_803+1", 1), ("379_803+1", 1), ("377_804+j", 2), ("379_804+j", 1),
    ("766,212", 2), ("764,012", 1), ("761,812", 0),
    ("358,720", 6), ("360,920", 1), ("356,520", 0),
    ("\u22120.096332", 1), ("\u22120.088982", 0), ("0.3106", 1), ("0.3259", 0),
    ("0.245172", 1), ("0.245163", 0), ("1.1833", 1), ("1.1831", 0),
    ("MSG-2026-10-06-205x", 3), ("469d40896", 0), ("4bdf63090", 3),
    ("r794", 10), ("r793", 2), ("r789", 1), ("r792", 5), ("r790", 0),
    ("阶梯第二十四例", 2), ("阶梯几何第二十四例", 1), ("阶梯第二十三例", 0),
    ("第 163 枚", 1), ("第 155 波", 1), ("第 162 枚", 0), ("第 154 波", 0),
    ("W166+ 投影", 2), ("W164 席位 W165+ 投影", 3), ("W163 席位", 0), ("继承第二十五例", 1),
    ("f7d34e5a7", 1), ("18231a529", 1), ("bm-a r789 freeze（18231a529）", 1),
    ("PERPETUAL_N1_W165_PREREG.md", 1), ("PERPETUAL-N1-W165", 3),
    ("n1_w165_results.json", 2), ("n1_w164_results.json", 1), ("n1_w163", 0),
    ("--wave 165", 2), ("波号 165=注册表 W164 行后首个自由号", 1),
    ("全一百六十二行注册 N1 带表（表尾 W164 行·leg0 机证 162 行）", 1),
    ("共一百六十三面实测", 1), ("第 163 枚", 1),
    ("（表尾 W164 行）", 1), ("（表尾 W163 行）", 0),
    ("SEED_REGISTRY 全键 188 值", 1),
]
for s, want in checks:
    got = out.count(s)
    assert got == want, f"output check {s!r}: {got} != {want}"
assert "## §7 跑后实证。【finalize 收口机械回填·待跑后】" in out
assert "## §8 批后复盘。【finalize 同窗回填·待跑后】" in out
assert "（待 finalize 收口窗回填：合并池/账本/K-lift/se_mu/A p95/§5 四键机证/canon flip 态/审计段。）" in out
assert "（待 finalize 收口窗回填：设计复用面/宝藏捕获问/W166+ 投影承接。）" in out
# no leftover tokens
for _, tok in TOK:
    assert tok not in out, f"token residue {tok}"
# SEED_REGISTRY live int-value count == prose 188 (machine check)
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates
n_int = len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)])
assert n_int == 188, f"SEED_REGISTRY int values drifted: {n_int}"
# start>end malformed-window scan (r773 leg 3)
import re
bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out)
       if int(m.group(3)) < int(m.group(1))]
assert not bad, f"malformed windows: {bad}"

io.open("research/PERPETUAL_N1_W165_PREREG.md", "w", encoding="utf-8", newline="").write(out)
print(f"W165 PREREG built: {len(out)} bytes, all {len(checks)} output checks PASS, "
      f"malformed-window scan CLEAN, SEED_REGISTRY 188 live-verified")
