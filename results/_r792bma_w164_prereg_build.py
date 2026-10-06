# -*- coding: utf-8 -*-
"""r792 bm-a W164 per-wave prereg builder: research/PERPETUAL_N1_W164_PREREG.md
from the W163 FROZEN-time prereg (git show 18231a529 -- pre-backfill version).

r773 pit-law compliance: two-pass sentinel vmap (TOK then BACK) -- no output
can ever be re-mapped; every band/projection value machine-derived from the
r792 gate + probe receipts and the W163 finalize results JSON (r587
never-transcribe); composite strings tokenized WHOLE; bare numerals LAST.
"""
import io, json, subprocess, sys

# --- machine facts (r587) -------------------------------------------------------
gate = json.load(open("results/_r792bma_w164_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "375604_377603", "B": "377604_377803"}, gate["bands"]
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert leg1["A"] == [375604, 377603] and leg1["B"] == [377604, 377803]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [375404, 377403] and leg1["ARITH_B"] == [375604, 375803]
assert leg1["B_naive_first_clean"] == [375604, 375803]
assert leg3["W165p_A"] == "377604..379603" and leg3["W165p_B"] == "377804..378003"
w163 = json.load(open("results/perpetual_faces/n1_w163_results.json", encoding="utf-8"))
m = w163["null_pool_cumulative"]["merged"]
own = w163["null_pool_cumulative"]["w163_only"]
led = w163["science_gates"]["ledger"]
assert m["n_values"] == 356520 and led["total"] == 764012 and led["prev_total"] == 761812
assert round(m["mu"], 4) == -0.0929 and round(own["mu"], 6) == -0.088982
assert m["sigma"] == 0.2451632693353447 and own["sigma"] == 0.250561227901671
assert w163["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3259
sk = w163["skill_line_v2_k_lift"]
assert sk["line_merged_356520"] == 1.1831 and sk["line_pre_w163"] == 1.1829
assert sk["line_delta_k_lift"] == 0.0002 and sk["n_eff_held_equal"] == 761812
assert w163["null_pool_cumulative"]["se_mu_at_k356520"] == 0.000411
raw = subprocess.run(["git", "show", "18231a529:research/PERPETUAL_N1_W163_PREREG.md"],
                     capture_output=True).stdout
assert len(raw) == 19021
frozen = raw.decode("utf-8")
assert "## §7 跑后实证。【finalize 收口机械回填·待跑后】" in frozen

# --- pass 1: source -> tokens (ordered; composites first, bare numerals last) ---
TOK = [
    # §5 key 5 whole-paragraph composite (gate leg3 verbatim for W165+)
    ("5. **W164+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 375_404..377_403 **CLEAN**（hops=0）；B first-clean **375_604..375_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W164：W164 冻结方必须在 post-W163 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W163 B 带 375_404..375_603 注册后将拒 naive W164 A 窗**——W164 A 重 derive 同强制（越过 W163 B 带·阶梯 A-hops-prior-B 继承第二十三例）；verify at W164 prereg，hop 链逐跳在 probe 回执。",
     "@S5K5@"),
    # §0 claim-composite (own-seat W164+ projection -> W165+ per this seat's gate tail)
    ("投影 W164+ A 375_404..377_403 naive/B 375_604..375_803 naive",
     "@S0PROJ@"),
    ("待 W164 注册宇宙复核", "@S0REV@"),
    # §8 placeholder composite
    ("W164+ 投影承接", "@S8PROJ@"),
    # registered-row tail entry (historical W162 row keeps r787+764cd882a; 表尾 moves to new W163 row)
    ("W162=bm-a r787 freeze（764cd882a·表尾）；**均已注册**（表尾 W162 行）",
     "@TAIL@"),
    # §5 preamble anchor citation file
    ("n1_w162_results.json", "@ANCHORF@"),
    # stats composites
    ("K-lift **\u22120.0001**【line_merged@K354,320 **1.1828**", "@KLC@"),
    ("W161 0.000413\u2192W162 **0.000412**", "@SEC@"),
    ("0.2451**=W162 合并池实测 0.245130", "@SIGC@"),
    ("\u22120.095597", "@OWMU@"),
    ("0.3093", "@AP95@"),
    ("n_eff 759,612", "@NEFF@"),
    # ordinal / row-count composites
    ("第 161 枚", "@ORDP@"),
    ("第 153 波【bm-a 第七十九枚自有波", "@ORDW@"),
    ("engine_owner 行 152+本候选=bm-a 第七十九枚自有波【r789】", "@ORDT@"),
    ("engine_owner==bm-a 行 78+本候选", "@ORDA@"),
    ("engine_owner==bm-a 78 行注册 + 本候选", "@ORDB@"),
    ("同 W155/W156/W157/W158/W159/W160/W161/W162 最近自有波", "@ORDL@"),
    ("共一百六十一面实测", "@ORDC@"),
    ("全一百六十行注册 N1 带表（表尾 W162 行·leg0 机证 160 行）", "@ORDR@"),
    ("波号 163=注册表 W162 行后首个自由号", "@WNUM@"),
    ("累计 null 池=354,320+2,200（本波）=**356,520 投影**", "@PROJC@"),
    # staircase ordinals
    ("阶梯第二十二例", "@ST22@"),
    ("阶梯几何第二十二例", "@STG22@"),
    # seat / push shas
    ("MSG-2026-10-06-183x", "@SEATX@"),
    ("189157de8", "@SEATSHA@"),
    # band geometry (own bands, naive windows, prior band, base relations)
    ("373_404..375_403", "@ABAND@"),
    ("375_404..375_603", "@BBAND@"),
    ("373_204..375_203", "@NABAND@"),
    ("373_404..373_603", "@NBBAND@"),
    ("373_204..373_403", "@PBAND@"),
    ("373_403+1", "@ABASE@"),
    ("375_403+1", "@BBASE@"),
    ("373_404+j", "@ASEED@"),
    ("375_404+j", "@BSEED@"),
    # ledger / K numbers
    ("761,812", "@LHEAD@"),
    ("354,320", "@KOLD@"),
    # session blankets
    ("r787", "@R787@"),
    ("r788", "@R788@"),
    ("r789", "@R789@"),
    # lowercase artifact names (own-wave)
    ("w163", "@LW@"),
    # wave-number blankets (prior-wave + own-wave)
    ("W162", "@PW@"),
    ("W163", "@OW@"),
    # bare numerals LAST
    ("--wave 163", "@RUNW@"),
    ("163", "@BARE@"),
]

BACK = [
    ("@S5K5@", "5. **W165+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 377_604..379_603 **CLEAN**（hops=0）；B first-clean **377_804..378_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W165：W165 冻结方必须在 post-W164 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W164 B 带 377_604..377_803 注册后将拒 naive W165 A 窗**——W165 A 重 derive 同强制（越过 W164 B 带·阶梯 A-hops-prior-B 继承第二十四例）；verify at W165 prereg，hop 链逐跳在 probe 回执。"),
    ("@S0PROJ@", "投影 W165+ A 377_604..379_603 naive/B 377_804..378_003 naive"),
    ("@S0REV@", "待 W165 注册宇宙复核"),
    ("@S8PROJ@", "W165+ 投影承接"),
    ("@TAIL@", "W162=bm-a r787 freeze（764cd882a）；W163=bm-a r789 freeze（18231a529·表尾）；**均已注册**（表尾 W163 行）"),
    ("@ANCHORF@", "n1_w163_results.json"),
    ("@KLC@", "K-lift **+0.0002**【line_merged@K356,520 **1.1831**"),
    ("@SEC@", "W161 0.000413\u2192W162 0.000412\u2192W163 **0.000411**"),
    ("@SIGC@", "0.2452**=W163 合并池实测 0.245163"),
    ("@OWMU@", "\u22120.088982"),
    ("@AP95@", "0.3259"),
    ("@NEFF@", "n_eff 761,812"),
    ("@ORDP@", "第 162 枚"),
    ("@ORDW@", "第 154 波【bm-a 第八十枚自有波"),
    ("@ORDT@", "engine_owner 行 153+本候选=bm-a 第八十枚自有波【r792】"),
    ("@ORDA@", "engine_owner==bm-a 行 79+本候选"),
    ("@ORDB@", "engine_owner==bm-a 79 行注册 + 本候选"),
    ("@ORDL@", "同 W156/W157/W158/W159/W160/W161/W162/W163 最近自有波"),
    ("@ORDC@", "共一百六十二面实测"),
    ("@ORDR@", "全一百六十一行注册 N1 带表（表尾 W163 行·leg0 机证 161 行）"),
    ("@WNUM@", "波号 164=注册表 W163 行后首个自由号"),
    ("@PROJC@", "累计 null 池=356,520+2,200（本波）=**358,720 投影**"),
    ("@ST22@", "阶梯第二十三例"),
    ("@STG22@", "阶梯几何第二十三例"),
    ("@SEATX@", "MSG-2026-10-06-194x"),
    ("@SEATSHA@", "469d40896"),
    ("@ABAND@", "375_604..377_603"),
    ("@BBAND@", "377_604..377_803"),
    ("@NABAND@", "375_404..377_403"),
    ("@NBBAND@", "375_604..375_803"),
    ("@PBAND@", "375_404..375_603"),
    ("@ABASE@", "375_603+1"),
    ("@BBASE@", "377_603+1"),
    ("@ASEED@", "375_604+j"),
    ("@BSEED@", "377_604+j"),
    ("@LHEAD@", "764,012"),
    ("@KOLD@", "356,520"),
    ("@R787@", "r789"),
    ("@R788@", "r790"),
    ("@R789@", "r792"),
    ("@LW@", "w164"),
    ("@PW@", "W163"),
    ("@OW@", "W164"),
    ("@RUNW@", "--wave 164"),
    ("@BARE@", "164"),
]


def vmap(s):
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


src = frozen
EXPECT = {  # exact per-token source counts (probe-verified)
    "r787": 5, "r788": 2, "r789": 10, "W162": 38, "W163": 24, "w163": 9, "163": 36,
    "MSG-2026-10-06-183x": 3, "189157de8": 3,
    "373_404..375_403": 4, "375_404..375_603": 5, "373_204..375_203": 2,
    "373_404..373_603": 2, "373_204..373_403": 1, "373_403+1": 1, "375_403+1": 1,
    "373_404+j": 2, "375_404+j": 1, "761,812": 2, "354,320": 6, "--wave 163": 2,
    "阶梯第二十二例": 2,
}
W155L = "同 W155/W156/W157/W158/W159/W160/W161/W162 最近自有波"
for i, (old, tok) in enumerate(TOK):
    n = src.count(old)
    want = EXPECT.get(old, 1)
    if old == W155L:
        want = 2
    assert n == want, f"TOK {i} count={n} != {want}: {old[:60]!r}"
out = vmap(src)

# --- output assertions -----------------------------------------------------------
checks = [
    ("375_604..377_603", 4), ("377_604..377_803", 5), ("375_404..377_403", 2),
    ("375_604..375_803", 2), ("375_404..375_603", 1),
    ("373_204..375_203", 0), ("373_404..373_603", 0), ("373_204..373_403", 0),
    ("373_404..375_403", 0), ("373_403+1", 0), ("375_403+1", 0),
    ("375_603+1", 1), ("377_603+1", 1), ("375_604+j", 2), ("377_604+j", 1),
    ("764,012", 2), ("761,812", 1), ("759,612", 0),
    ("356,520", 6), ("358,720", 1), ("354,320", 0),
    ("\u22120.088982", 1), ("\u22120.095597", 0), ("0.3259", 1), ("0.3093", 0),
    ("0.245163", 1), ("0.245130", 0), ("1.1831", 1), ("1.1828", 0),
    ("MSG-2026-10-06-194x", 3), ("189157de8", 0), ("469d40896", 3),
    ("r792", 10), ("r790", 2), ("r787", 1), ("r789", 5), ("r788", 0),
    ("阶梯第二十三例", 2), ("阶梯几何第二十三例", 1), ("阶梯第二十二例", 0),
    ("第 162 枚", 1), ("第 154 波", 1), ("第 161 枚", 0), ("第 153 波", 0),
    ("W165+ 投影", 2), ("W163 席位 W164+ 投影", 3), ("W162 席位", 0), ("继承第二十四例", 1),
    ("18231a529", 1), ("764cd882a", 1), ("bm-a r787 freeze（764cd882a）", 1),
    ("PERPETUAL_N1_W164_PREREG.md", 1), ("PERPETUAL-N1-W164", 3),
    ("n1_w164_results.json", 2), ("n1_w163_results.json", 1), ("n1_w162", 0),
    ("--wave 164", 2), ("波号 164=注册表 W163 行后首个自由号", 1),
    ("全一百六十一行注册 N1 带表（表尾 W163 行·leg0 机证 161 行）", 1),
    ("共一百六十二面实测", 1), ("第 162 枚", 1),
    ("（表尾 W163 行）", 1), ("（表尾 W162 行）", 0),
    ("SEED_REGISTRY 全键 188 值", 1),
]
for s, want in checks:
    got = out.count(s)
    assert got == want, f"output check {s!r}: {got} != {want}"
assert "## §7 跑后实证。【finalize 收口机械回填·待跑后】" in out
assert "## §8 批后复盘。【finalize 同窗回填·待跑后】" in out
assert "（待 finalize 收口窗回填：合并池/账本/K-lift/se_mu/A p95/§5 四键机证/canon flip 态/审计段。）" in out
assert "（待 finalize 收口窗回填：设计复用面/宝藏捕获问/W165+ 投影承接。）" in out
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

io.open("research/PERPETUAL_N1_W164_PREREG.md", "w", encoding="utf-8", newline="").write(out)
print(f"W164 PREREG built: {len(out)} bytes, all {len(checks)} output checks PASS, "
      f"malformed-window scan CLEAN, SEED_REGISTRY 188 live-verified")
