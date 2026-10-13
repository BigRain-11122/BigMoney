# -*- coding: utf-8 -*-
# r967 W232 tpl generator phase B: STALE/NEW tables + in-band asserts + tail.
# Operates on the phase-A output (results/_w232bmc_prereg_derive_tpl.py).
import sys
sys.stdout.reconfigure(encoding="utf-8")
DST = r"results\_w232bmc_prereg_derive_tpl.py"
t = open(DST, encoding="utf-8").read()

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)

MINUS = "\u2212"

# ---- STALE table: full block replacement (W231 self-faces must be zero) ----
stale_old = '''STALE = ["520_804..522_803", "520_604..522_603", "520_604..520_803",
         "520804", "522804", "520_804+j", "522_804+j", "第 228 枚", "NINETIETH", "第九十例", "第六十枚",
         "219 注册在册", "bmc_ordinal=60", "r963 freeze 窗", "0.3199", "\\u2212" + "0.09270128",
         "\\u2212" + "0.08818286", "0.24507549", "1000-bmc", "6cfe285e3",
         "10:1x（W229 面完整性", "10:1x finalize one-pass】", "r962 窗 10:1x", "二百二十七",
         "共二百二十七面", "机证 227 行", "第 220 波",
         "n_eff_held_equal 925,389", "line_pre_w229 1.1919", "=**503,920 投影**", "engine_owner==bm-c 59 行",
         "prose 60th", "r962 freeze receipt 59th", "第 60 枚 EXACT", "pre-W230 宇宙",
         "W231 freezer 承接面", "r962 W229 §7 范式", "r962 W229 §8 范式", "r962/W229 先例",
         "W230 B 带 522_804..523_003 注册后将拒 naive W231",
         "（520_803+1）", "（522_803+1）", "波号 230=", "A base=520804", "B base=522804", "n1_w230/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W230"', "line_merged@K501,720",
         "实差 0.0045 在带内", "parity 88 行",
         "W136..W229 先例链披露", "W5..W229 先例", "v2..W229 落地", "W2..W229 落地 runner",
         "W2..W229 带（冻结时点", "W2..W229 全注册在冻结时点成立", "W1..W229 N1 finalize 已全部落地",
         "W1..W229 已落账", "（W1..W229 全落）", "501,720+2,200", "K=501,720 合并池",
         "净账本锚头 927,589", "净账本锚头 **927,589**", "splice 2ae8553e6", "W229 **0.000346**】",
         "verify at W231 prereg", "r962 窗", "2026-10-13 10:3x"]'''
stale_new = '''STALE = ["523_004..525_003", "522_804..524_803", "522_804..523_003",
         "523004", "525004", "523_004+j", "525_004+j", "第 229 枚", "NINETY-FIRST", "第九十一例", "第六十一枚",
         "220 注册在册", "bmc_ordinal=61", "r964 freeze 窗", "0.3069", "\\u2212" + "0.09269286",
         "\\u2212" + "0.090772", "0.24504776", "1155-bmc", "6638ddf9f",
         "11:5x（W230 面完整性", "11:5x finalize one-pass】", "r963 窗 11:5x", "二百二十八",
         "共二百二十八面", "机证 228 行", "第 221 波",
         "n_eff_held_equal 927,589", "line_pre_w230 1.192", "=**506,120 投影**", "engine_owner==bm-c 60 行",
         "prose 61st", "r963 freeze receipt 60th", "第 61 枚 EXACT", "pre-W231 宇宙",
         "W232 freezer 承接面", "r963 W230 §7 范式", "r963 W230 §8 范式", "r963/W230 先例",
         "W231 B 带 525_004..525_203 注册后将拒 naive W232",
         "（523_003+1）", "（525_003+1）", "波号 231=", "A base=523004", "B base=525004", "n1_w231/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W231"', "line_merged@K503,920",
         "实差 0.0019 在带内", "parity 89 行",
         "W136..W230 先例链披露", "W5..W230 先例", "v2..W230 落地", "W2..W230 落地 runner",
         "W2..W230 带（冻结时点", "W2..W230 全注册在冻结时点成立", "W1..W230 N1 finalize 已全部落地",
         "W1..W230 已落账", "（W1..W230 全落）", "503,920+2,200", "K=503,920 合并池",
         "净账本锚头 929,789", "净账本锚头 **929,789**", "splice 24e12fa5e", "W230 **0.000345**】",
         "verify at W232 prereg", "r963 窗", "2026-10-13 12:1x"]'''
rep(stale_old, stale_new)

# ---- NOTE comment ----
rep('''# NOTE: "522_804..524_803" / "523_004..523_203" are NOT stale in the W231
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 12:2x).
# "522_804..523_003" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w230_results.json" file refs stay (upstream
# legs) while "n1_w230/ 分片计数增长" IS stale (self shard face now n1_w231).
# "522804" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 525004; W230's 522804 appears only inside band-range strings with
# underscores (different token face).''',
    '''# NOTE: "525_004..527_003" / "525_204..525_403" are NOT stale in the W232
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 13:4x).
# "525_004..525_203" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w231_results.json" file refs stay (upstream
# legs) while "n1_w231/ 分片计数增长" IS stale (self shard face now n1_w232).
# "525004" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 527204; W231's 525004 appears only inside band-range strings with
# underscores (different token face).''')

# ---- NEW table: full block replacement ----
new_old = '''NEW = ["PERPETUAL-N1-W231", "第 229 枚", "523_004..525_003", "525_004..525_203",
       "NINETY-FIRST", "第九十一例", "第九十二例", "第六十一枚",
       "929,789", "503,920", "506,120", "927,589", "501,720", "925,389",
       "MSG-20261013-1155-bmc", "6638ddf9f",
       "bmc_ordinal=61", "n1_w231_results.json", "n1_w230_results.json", "0.3069", "\\u2212" + "0.09269286",
       "\\u2212" + "0.090772", "0.24504776", "n_eff_held_equal 927,589", "0.000345",
       "1.1919", "第 221 波", "525_004..527_003", "525_204..525_403",
       "522_804..524_803", "523_004..523_203",
       "0.0019", "48c321706", "842f817ad", "2ae8553e6", "24e12fa5e", "第 61 枚 EXACT", "W232 freezer 承接面",
       "r963 W230 §7 范式", "K-lift **''' + MINUS + '''0.0001**", "实差 0.0019 在带内",
       "parity 89 行", "二百二十八行", "共二百二十八面", "机证 228 行",
       "r964 freeze 窗", "prose 61st", "60th owned 承袭",
       "11:5x（W230 面完整性", "11:5x finalize one-pass】", "verify at W232 prereg",
       "r963/W230 先例", "（523_003+1）", "（525_003+1）", "r963 窗实跑", "r963 窗 11:5x",
       "engine_owner==bm-c 60 行"]'''
new_new = '''NEW = ["PERPETUAL-N1-W232", "第 230 枚", "525_204..527_203", "527_204..527_403",
       "NINETY-SECOND", "第九十二例", "第九十三例", "第六十二枚",
       "931,989", "506,120", "508,320", "929,789", "503,920", "927,589",
       "MSG-20261013-1345-bmc", "8d3a1b78a",
       "bmc_ordinal=62", "n1_w232_results.json", "n1_w231_results.json", "0.3251", "\\u2212" + "0.09268999",
       "\\u2212" + "0.09203368", "0.24507072", "n_eff_held_equal 929,789", "0.000344",
       "1.1921", "第 222 波", "527_204..529_203", "527_404..527_603",
       "525_004..527_003", "525_204..525_403",
       "0.0007", "48c321706", "842f817ad", "2ae8553e6", "24e12fa5e", "aee0bd9fa", "第 62 枚 EXACT", "W233 freezer 承接面",
       "r966 W231 §7 范式", "K-lift **+0.0001**", "实差 0.0007 在带内",
       "parity 90 行", "二百二十九行", "共二百二十九面", "机证 229 行",
       "r967 freeze 窗", "prose 62nd", "61st owned 承袭",
       "13:2x（W231 面完整性", "13:2x finalize one-pass】", "verify at W233 prereg",
       "r966/W231 先例", "（525_203+1）", "（527_203+1）", "r966 窗实跑", "r966 窗 13:2x",
       "engine_owner==bm-c 61 行"]'''
rep(new_old, new_new)

# ---- in-band sanity + band asserts ----
rep('''assert t.count("523_004..525_003") >= 4 and t.count("525_004..525_203") >= 4''',
    '''assert t.count("525_204..527_203") >= 4 and t.count("527_204..527_403") >= 4''')
rep('''# upstream W230 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("522_804..523_003") >= 2''',
    '''# upstream W231 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("525_004..525_203") >= 2''')

# ---- chain-history legs: add W231 leg + n1_w231 file assert ----
rep('''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''',
    '''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("+W231=bm-c r966 五面冻结（aee0bd9fa）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''')
rep('''assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1''',
    '''assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1
assert t.count("n1_w231_results.json·13:2x") == 1''')

# ---- healed RAM list + estate note + template ref + se_mu chain ----
rep('''assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230 低 RAM 实烧先例") == 1''',
    '''assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231 低 RAM 实烧先例") == 1''')
rep('''assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230）") == 1''',
    '''assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231）") == 1''')
rep('''assert t.count("按 _w230bmc_freeze_edits.py 模板派生") == 1''',
    '''assert t.count("按 _w231bmc_freeze_edits.py 模板派生") == 1''')
rep('''assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**】") == 1''',
    '''assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**】") == 1''')

# ---- out path + tail prints ----
rep('''out = r"research\\PERPETUAL_N1_W231_PREREG.md"''',
    '''out = r"research\\PERPETUAL_N1_W232_PREREG.md"''')
rep('''print("W231 prereg derived OK:", out)''',
    '''print("W232 prereg derived OK:", out)''')
rep('''print("W230(upper) refs (upstream, expected 40+):", t.count("W230"), "| W231 self:", t.count("W231"))
print("W229 heritage refs (chain legs + estate face):", t.count("W229"))''',
    '''print("W231(upper) refs (upstream, expected 40+):", t.count("W231"), "| W232 self:", t.count("W232"))
print("W230 heritage refs (chain legs + estate face):", t.count("W230"))''')

open(DST, "w", encoding="utf-8", newline="").write(t)
assert t.count("@@SUB_BLOCK@@") == 1, "SUB marker lost"
print("phase B OK: STALE/NEW/in-band/tail advanced; tpl bytes:", len(t.encode("utf-8")))
