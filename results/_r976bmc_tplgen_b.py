# -*- coding: utf-8 -*-
# r976 W234 tpl generator phase B: STALE/NEW tables + in-band asserts + tail.
# Operates on the phase-A output (results/_w234bmc_prereg_derive_tpl.py).
# Method = _r972bmc_tplgen_b.py pair-table law: source blocks extracted
# verbatim from the phase-A tpl (byte-identical to the committed W233 tpl
# blocks), each pair assert-verified count==n, inverse round-trip gate, plus
# a base-presence audit of every aged STALE token against the freeze-time
# W233 face (results/_w234bmc_base_face.txt = git blob 933e3ceea) -- aged
# STALE tokens are things the W234 SUB pairs replace, so each must sit in
# the base face count>=1 (r972 absorb-fix precedent audit).
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
DST = r"results\_w234bmc_prereg_derive_tpl.py"
BASE = open(r"results\_w234bmc_base_face.txt", encoding="utf-8").read()
t = open(DST, encoding="utf-8").read()

def block(varname):
    i = t.index(varname + " = [")
    j = t.index("]\n", i) + 2
    return t[i:j]

stale_src = block("STALE")
new_src = block("NEW")
assert t.count(stale_src) == 1 and t.count(new_src) == 1, "block not unique"

apply_pairs_source = {}

def apply_pairs(block_txt, pairs, label):
    for old, new, n in pairs:
        c = block_txt.count(old)
        assert c == n, f"{label} pair count {c} != {n}: {old[:60]!r}"
        block_txt = block_txt.replace(old, new)
    back = block_txt
    for old, new, n in reversed(pairs):
        c = back.count(new)
        assert c == n, f"{label} inverse count {c} != {n}: {new[:60]!r}"
        back = back.replace(new, old)
    assert back == apply_pairs_source[label], f"{label} round-trip drift"
    return block_txt

# ---- STALE block: W232 self-faces -> W233 self-faces ----
S = [
 ("共二百二十九面", "共二百三十面", 1),
 ('"r966 窗 13:2x", "二百二十九"', '"r968 窗 15:2x", "二百三十行"', 1),
 ("525_204..527_203", "527_404..529_403", 1),
 ('"525_004..527_003", "525_004..525_203"', '"527_204..529_203", "527_204..527_403"', 1),
 ("525204", "527404", 2),
 ("527204", "529404", 2),
 ("525_204+j", "527_404+j", 1),
 ("527_204+j", "529_404+j", 1),
 ("第 230 枚", "第 231 枚", 1),
 ("NINETY-SECOND", "NINETY-THIRD", 1),
 ("第九十二例", "第九十三例", 1),
 ("第六十二枚", "第六十三枚", 1),
 ("221 注册在册", "222 注册在册", 1),
 ("bmc_ordinal=62", "bmc_ordinal=63", 1),
 ("r967 freeze 窗", "r972 freeze 窗", 1),
 ("0.3251", "0.3063", 1),
 ("0.09268999", "0.09274288", 1),
 ("0.09203368", "0.10490950", 1),
 ("0.24507072", "0.24508296", 1),
 ("1345-bmc", "1530-bmc", 1),
 ("8d3a1b78a", "dd38a9da8", 1),
 ("13:2x（W231 面完整性", "15:2x（W232 面完整性", 1),
 ("13:2x finalize one-pass】", "15:2x finalize one-pass】", 1),
 ("机证 229 行", "机证 230 行", 1),
 ("第 222 波", "第 223 波", 1),
 ("n_eff_held_equal 929,789", "n_eff_held_equal 931,989", 1),
 ("line_pre_w231 1.1921", "line_pre_w232 1.1922", 1),
 ("=**508,320 投影**", "=**510,520 投影**", 1),
 ("engine_owner==bm-c 61 行", "engine_owner==bm-c 62 行", 1),
 ("prose 62nd", "prose 63rd", 1),
 ("r966 freeze receipt 61st", "r968 freeze receipt 62nd", 1),
 ("第 62 枚 EXACT", "第 63 枚 EXACT", 1),
 ("pre-W232 宇宙", "pre-W233 宇宙", 1),
 ("W233 freezer 承接面", "W234 freezer 承接面", 1),
 ("r966 W231 §7 范式", "r968 W232 §7 范式", 1),
 ("r966 W231 §8 范式", "r968 W232 §8 范式", 1),
 ("r966/W231 先例", "r968/W232 先例", 1),
 ("W232 B 带 527_204..527_403 注册后将拒 naive W233", "W233 B 带 529_404..529_603 注册后将拒 naive W234 A 窗", 1),
 ("（525_203+1）", "（527_403+1）", 1),
 ("（527_203+1）", "（529_403+1）", 1),
 ("波号 232=", "波号 233=", 1),
 ("n1_w232/ 分片计数增长", "n1_w233/ 分片计数增长", 1),
 ('batch_name="PERPETUAL-N1-W232"', 'batch_name="PERPETUAL-N1-W233"', 1),
 ("line_merged@K506,120", "line_merged@K508,320", 1),
 ("实差 0.0007 在带内", "实差 0.0122 在带内", 1),
 ("parity 90 行", "parity 91 行", 1),
 ("W136..W231 先例链披露", "W136..W232 先例链披露", 1),
 ("W5..W231 先例", "W5..W232 先例", 1),
 ("v2..W231 落地", "v2..W232 落地", 1),
 ("W2..W231 落地 runner", "W2..W232 落地 runner", 1),
 ("W2..W231 带（冻结时点", "W2..W232 带（冻结时点", 1),
 ("W2..W231 全注册在冻结时点成立", "W2..W232 全注册在冻结时点成立", 1),
 ("W1..W231 N1 finalize 已全部落地", "W1..W232 N1 finalize 已全部落地", 1),
 ("W1..W231 已落账", "W1..W232 已落账", 1),
 ("（W1..W231 全落）", "（W1..W232 全落）", 1),
 ("506,120+2,200", "508,320+2,200", 1),
 ("K=506,120 合并池", "K=508,320 合并池", 1),
 ("净账本锚头 931,989", "净账本锚头 934,189", 1),
 ("净账本锚头 **931,989**", "净账本锚头 **934,189**", 1),
 ("splice aee0bd9fa", "splice e58dbcda3", 1),
 ("W231 **0.000344**】", "W232 **0.000344**】", 1),
 ("verify at W233 prereg", "verify at W234 prereg", 1),
 ('"r966 窗", "2026-10-13 13:5x"', '"r972 窗", "2026-10-13 18:4x"', 1),
]
apply_pairs_source["STALE"] = stale_src
stale_new = apply_pairs(stale_src, S, "STALE")
t = t.replace(stale_src, stale_new)
print("STALE block advanced: W232->W233 64-pair, round-trip OK")

# ---- NEW block: W233 fresh faces -> W234 fresh faces ----
N = [
 ("第九十四例", "第九十五例", 1),          # before 九十三->九十四 creates a second
 ("第九十三例", "第九十四例", 1),
 ("NINETY-THIRD", "NINETY-FOURTH", 1),
 ("PERPETUAL-N1-W233", "PERPETUAL-N1-W234", 1),
 ("第 231 枚", "第 232 枚", 1),
 ("527_404..529_403", "529_604..531_603", 1),   # fresh A
 ("529_404..529_603", "531_604..531_803", 1),   # fresh B
 ("529_404..531_403", "531_604..533_603", 1),   # S5.5 projection A (before ARITH_A re-creates)
 ("529_604..529_803", "531_804..532_003", 1),   # S5.5 projection B naive (before ARITH_B)
 ("527_204..529_203", "529_404..531_403", 1),   # ARITH_A
 ("527_404..527_603", "529_604..529_803", 1),   # ARITH_B / B_naive_first_clean
 ("第六十三枚", "第六十四枚", 1),
 ("934,189", "936,389", 1),              # ledger chain high-first
 ("931,989", "934,189", 2),              # standalone + n_eff_held_equal 931,989
 ("929,789", "931,989", 1),
 ("510,520", "512,720", 1),              # K chain high-first
 ("508,320", "510,520", 1),
 ("506,120", "508,320", 1),
 ("MSG-20261013-1530-bmc", "MSG-20261013-1955-bmc", 1),
 ("dd38a9da8", "260217d39", 1),
 ("bmc_ordinal=63", "bmc_ordinal=64", 1),
 ("n1_w233_results.json", "n1_w234_results.json", 1),
 ("n1_w232_results.json", "n1_w233_results.json", 1),
 ("0.3063", "0.3027", 1),
 ("0.09274288", "0.09276956", 1),
 ("0.10490950", "0.09893318", 1),
 ("0.24508296", "0.24506207", 1),
 ("0.000344", "0.000343", 1),            # se_mu key (W232/W231 same 0.000344 -> W233 0.000343)
 ("1.1922", "1.1924", 1),
 ("第 223 波", "第 224 波", 1),
 ("实差 0.0122 在带内", "实差 0.0062 在带内", 1),
 ('"0.0122", "48c321706"', '"0.0062", "48c321706"', 1),
 ("第 63 枚 EXACT", "第 64 枚 EXACT", 1),
 ('e58dbcda3", "第 64 枚 EXACT', 'e58dbcda3", "0ca920362", "第 64 枚 EXACT', 1),
 ("W234 freezer 承接面", "W235 freezer 承接面", 1),
 ("r968 W232 §7 范式", "r974 W233 §7 范式", 1),
 ("K-lift **+0.0001**", "K-lift **−0.0002**", 1),  # U+2212 prose face (R34[37])
 ("parity 91 行", "parity 92 行", 1),
 ("二百三十行", "二百三十一行", 1),
 ("共二百三十面", "共二百三十一面", 1),
 ("机证 230 行", "机证 231 行", 1),
 ("r972 freeze 窗", "r976 freeze 窗", 1),
 ("prose 63rd", "prose 64th", 1),
 ("62nd owned 承袭", "63rd owned 承袭", 1),
 ("15:2x（W232 面完整性", "19:5x（W233 面完整性", 1),
 ("15:2x finalize one-pass】", "19:5x finalize one-pass】", 1),
 ("verify at W234 prereg", "verify at W235 prereg", 1),
 ("r968/W232 先例", "r973/W233 先例", 1),
 ("（527_403+1）", "（529_603+1）", 1),
 ("（529_403+1）", "（531_603+1）", 1),
 ("r972 窗实跑", "r976 窗实跑", 1),
 ("r968 窗 15:2x", "r974 窗 19:5x", 1),
 ("engine_owner==bm-c 62 行", "engine_owner==bm-c 63 行", 1),
]
apply_pairs_source["NEW"] = new_src
new_new = apply_pairs(new_src, N, "NEW")
t = t.replace(new_src, new_new)
print("NEW block advanced: W233->W234 (0ca920362 inserted), round-trip OK")

# ---- base-presence audit: every aged STALE token sits in the W233 face ----
MINUS = "\u2212"
audit_fail = []
for old, new, n in S:
    toks = re.findall(r'"([^"]+)"', new) if new.startswith('"') else [new]
    for tok in toks:
        probe = MINUS + tok if re.fullmatch(r"0\.09\d+|0\.104\d+", tok) else tok
        c = BASE.count(probe)
        if c < 1:
            audit_fail.append((tok, probe, c))
assert not audit_fail, f"base-presence audit FAIL: {audit_fail}"
print("base-presence audit OK: 64/64 aged STALE tokens sit count>=1 in the W233 freeze face")

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)

# ---- NOTE comment ----
rep('''# NOTE: "527_204..529_203" / "527_404..527_603" are NOT stale in the W233
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 17:5x).
# "527_204..527_403" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w232_results.json" file refs stay (upstream
# legs) while "n1_w232/ 分片计数增长" IS stale (self shard face now n1_w233).
# "527204" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 529404; W232's 527204 appears only inside band-range strings with
# underscores (different token face).''',
    '''# NOTE: "529_404..531_403" / "529_604..529_803" are NOT stale in the W234
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 20:5x).
# "529_404..529_603" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w233_results.json" file refs stay (upstream
# legs) while "n1_w233/ 分片计数增长" IS stale (self shard face now n1_w234).
# "529404" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 531604; W233's 529404 appears only inside band-range strings with
# underscores (different token face).''')

# ---- in-band sanity + band asserts ----
rep('assert t.count("527_404..529_403") >= 4 and t.count("529_404..529_603") >= 4',
    'assert t.count("529_604..531_603") >= 4 and t.count("531_604..531_803") >= 4')
rep('''# upstream W232 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("527_204..527_403") >= 2''',
    '''# upstream W233 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("529_404..529_603") >= 2''')

# ---- chain-history legs: add W233 leg + n1_w233 file assert ----
rep('''assert t.count("+W232=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''',
    '''assert t.count("+W232=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）") == 1
assert t.count("+W233=bm-c r973 死窗五面冻结（0ca920362）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''')
rep('''assert t.count("n1_w231_results.json·13:2x") == 1
assert t.count("n1_w232_results.json·15:2x") == 1''',
    '''assert t.count("n1_w231_results.json·13:2x") == 1
assert t.count("n1_w232_results.json·15:2x") == 1
assert t.count("n1_w233_results.json·19:5x") == 1''')

# ---- healed RAM list + estate note + template ref + se_mu chain ----
rep('assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232 低 RAM 实烧先例") == 1',
    'assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233 低 RAM 实烧先例") == 1')
rep('assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232）") == 1',
    'assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233）") == 1')
rep('assert t.count("按 _w232bmc_freeze_edits.py 模板派生") == 1',
    'assert t.count("按 _w233bmc_freeze_edits.py 模板派生") == 1')
rep('assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**】") == 1',
    'assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**→W233 **0.000343**】") == 1')

# ---- out path + tail prints ----
rep('out = r"research\\PERPETUAL_N1_W233_PREREG.md"',
    'out = r"research\\PERPETUAL_N1_W234_PREREG.md"')
rep('print("W233 prereg derived OK:", out)',
    'print("W234 prereg derived OK:", out)')
rep('''print("W232(upper) refs (upstream, expected 40+):", t.count("W232"), "| W233 self:", t.count("W233"))
print("W231 heritage refs (chain legs + estate face):", t.count("W231"))''',
    '''print("W233(upper) refs (upstream, expected 40+):", t.count("W233"), "| W234 self:", t.count("W234"))
print("W232 heritage refs (chain legs + estate face):", t.count("W232"))''')

open(DST, "w", encoding="utf-8", newline="").write(t)
assert t.count("@@SUB_BLOCK@@") == 1, "SUB marker lost"
import py_compile
py_compile.compile(DST, doraise=True)
print("phase B OK: STALE/NEW/in-band/tail advanced; tpl bytes:", len(t.encode("utf-8")), "| py_compile PASS")
