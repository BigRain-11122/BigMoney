# -*- coding: utf-8 -*-
# r964 W231 tpl generator phase B: STALE/NEW tables + in-band asserts + tail.
# Operates on the phase-A output (results/_w231bmc_prereg_derive_tpl.py).
import sys
sys.stdout.reconfigure(encoding="utf-8")
DST = r"results\_w231bmc_prereg_derive_tpl.py"
t = open(DST, encoding="utf-8").read()

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)

MINUS = "\u2212"

# ---- STALE table: full block replacement (W230 self-faces must be zero) ----
stale_old = '''STALE = ["518_604..520_603", "518_404..520_403", "518_404..518_603",
         "518604", "520604", "518_604+j", "520_604+j", "第 227 枚", "EIGHTY-NINTH", "第八十九例", "第五十九枚",
         "218 注册在册", "bmc_ordinal=59", "r960 freeze 窗", "0.3200", "\\u2212" + "0.09272118",
         "\\u2212" + "0.08495759", "0.24508298", "0855-bmc", "c9e9e83b8",
         "08:3x（W228 面完整性", "08:3x finalize one-pass】", "r959 窗 08:3x", "二百二十六",
         "共二百二十六面", "机证 226 行", "第 219 波",
         "n_eff_held_equal 923,189", "line_pre_w228 1.1918", "=**501,720 投影**", "engine_owner==bm-c 58 行",
         "prose 59th", "r959 freeze receipt 58th", "第 59 枚 EXACT", "pre-W229 宇宙",
         "W230 freezer 承接面", "r959 W228 §7 范式", "r959 W228 §8 范式", "r959/W228 先例",
         "W229 B 带 520_604..520_803 注册后将拒 naive W230",
         "（518_603+1）", "（520_603+1）", "波号 229=", "A base=518604", "B base=520604", "n1_w229/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W229"', "line_merged@K499,520",
         "实差 0.0078 在带内", "parity 87 行",
         "W136..W228 先例链披露", "W5..W228 先例", "v2..W228 落地", "W2..W228 落地 runner",
         "W2..W228 带（冻结时点", "W2..W228 全注册在冻结时点成立", "W1..W228 N1 finalize 已全部落地",
         "W1..W228 已落账", "（W1..W228 全落）", "499,520+2,200", "K=499,520 合并池",
         "净账本锚头 925,389", "净账本锚头 **925,389**", "splice 842f817ad", "W228 **0.000347**】",
         "verify at W230 prereg", "r959 窗", "2026-10-13 9:0x"]'''
stale_new = '''STALE = ["520_804..522_803", "520_604..522_603", "520_604..520_803",
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
rep(stale_old, stale_new)

# ---- NOTE comment ----
rep('''# NOTE: "520_604..522_603" / "520_804..521_003" are NOT stale in the W230
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 10:0x).
# "520_604..520_803" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w229_results.json" file refs stay (upstream
# legs) while "n1_w229/ 分片计数增长" IS stale (self shard face now n1_w230).
# "520604" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 522804; W229's 520604 appears only inside band-range strings with
# underscores (different token face).''',
    '''# NOTE: "522_804..524_803" / "523_004..523_203" are NOT stale in the W231
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 12:2x).
# "522_804..523_003" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w230_results.json" file refs stay (upstream
# legs) while "n1_w230/ 分片计数增长" IS stale (self shard face now n1_w231).
# "522804" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 525004; W230's 522804 appears only inside band-range strings with
# underscores (different token face).''')

# ---- NEW table: full block replacement ----
new_old = '''NEW = ["PERPETUAL-N1-W230", "第 228 枚", "520_804..522_803", "522_804..523_003",
       "NINETIETH", "第九十例", "第九十一例", "第六十枚",
       "927,589", "501,720", "503,920", "925,389", "499,520", "923,189",
       "MSG-20261013-1000-bmc", "6cfe285e3",
       "bmc_ordinal=60", "n1_w230_results.json", "0.3199", "\\u2212" + "0.09270128",
       "\\u2212" + "0.08818286", "0.24507549", "n_eff_held_equal 925,389", "0.000346",
       "1.1919", "第 220 波", "522_804..524_803", "523_004..523_203",
       "520_604..522_603", "520_804..521_003",
       "0.0045", "48c321706", "842f817ad", "2ae8553e6", "第 60 枚 EXACT", "W231 freezer 承接面",
       "r962 W229 §7 范式", "K-lift **+0.0000**", "实差 0.0045 在带内",
       "parity 88 行", "二百二十七行", "共二百二十七面", "机证 227 行",
       "r963 freeze 窗", "prose 60th", "59th owned 承袭",
       "10:1x（W229 面完整性", "10:1x finalize one-pass】", "verify at W231 prereg",
       "r962/W229 先例", "（520_803+1）", "（522_803+1）", "r962 窗实跑", "r962 窗 10:1x",
       "engine_owner==bm-c 59 行"]'''
new_new = '''NEW = ["PERPETUAL-N1-W231", "第 229 枚", "523_004..525_003", "525_004..525_203",
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
rep(new_old, new_new)

# ---- in-band sanity + band asserts ----
rep('''assert t.count("520_804..522_803") >= 4 and t.count("522_804..523_003") >= 4''',
    '''assert t.count("523_004..525_003") >= 4 and t.count("525_004..525_203") >= 4''')
rep('''# upstream W229 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("520_604..520_803") >= 2''',
    '''# upstream W230 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("522_804..523_003") >= 2''')

# ---- chain-history legs: add W230 leg + n1_w230 file assert ----
rep('''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''',
    '''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''')
rep('''assert t.count("n1_w229_results.json·10:1x") == 1''',
    '''assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1''')

# ---- healed RAM list + estate note + template ref + se_mu chain ----
rep('''assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229 低 RAM 实烧先例") == 1''',
    '''assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230 低 RAM 实烧先例") == 1''')
rep('''assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229）") == 1''',
    '''assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230）") == 1''')
rep('''assert t.count("按 _w229bmc_freeze_edits.py 模板派生") == 1''',
    '''assert t.count("按 _w230bmc_freeze_edits.py 模板派生") == 1''')
rep('''assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**】") == 1''',
    '''assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**】") == 1''')

# ---- out path + tail prints ----
rep('''out = r"research\\PERPETUAL_N1_W230_PREREG.md"''',
    '''out = r"research\\PERPETUAL_N1_W231_PREREG.md"''')
rep('''print("W230 prereg derived OK:", out)''',
    '''print("W231 prereg derived OK:", out)''')
rep('''print("W229(upper) refs (upstream, expected 40+):", t.count("W229"), "| W230 self:", t.count("W230"))
print("W228 heritage refs (chain legs + estate face):", t.count("W228"))''',
    '''print("W230(upper) refs (upstream, expected 40+):", t.count("W230"), "| W231 self:", t.count("W231"))
print("W229 heritage refs (chain legs + estate face):", t.count("W229"))''')

open(DST, "w", encoding="utf-8", newline="").write(t)
assert t.count("@@SUB_BLOCK@@") == 1, "SUB marker lost"
print("phase B OK: STALE/NEW/in-band/tail advanced; tpl bytes:", len(t.encode("utf-8")))
