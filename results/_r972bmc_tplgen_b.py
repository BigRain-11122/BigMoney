# -*- coding: utf-8 -*-
# r972 W233 tpl generator phase B: STALE/NEW tables + in-band asserts + tail.
# Operates on the phase-A output (results/_w233bmc_prereg_derive_tpl.py).
# Old blocks are AST-extracted verbatim from the committed _r967bmc_tplgen_b.py
# (stale_new/new_new = exactly what that script wrote into the committed W232
# tpl -- zero hand transcription); new blocks are built by an explicit ordered
# pair table, each pair assert-verified, with an inverse round-trip gate.
import ast, sys
sys.stdout.reconfigure(encoding="utf-8")
DST = r"results\_w233bmc_prereg_derive_tpl.py"
t = open(DST, encoding="utf-8").read()

def resolve_node(node, vars):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return resolve_node(node.left, vars) + resolve_node(node.right, vars)
    if isinstance(node, ast.Name) and node.id in vars:
        return vars[node.id]
    raise AssertionError(f"unresolvable AST node: {ast.dump(node)[:100]}")

def extract_lit(path, varname, vars):
    src = open(path, encoding="utf-8").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            return resolve_node(node.value, vars)
    raise AssertionError(f"{varname} not found")

VARS = {"MINUS": "\u2212"}
stale_w231 = extract_lit(r"results\_r967bmc_tplgen_b.py", "stale_new", VARS)
new_w232 = extract_lit(r"results\_r967bmc_tplgen_b.py", "new_new", VARS)
assert t.count(stale_w231) == 1, "W231-face STALE block not count==1 in phase-A tpl"
assert t.count(new_w232) == 1, "W232-face NEW block not count==1 in phase-A tpl"

apply_pairs_source = {}

def apply_pairs(block, pairs, label):
    for old, new, n in pairs:
        c = block.count(old)
        assert c == n, f"{label} pair count {c} != {n}: {old[:60]!r}"
        block = block.replace(old, new)
    # inverse round-trip gate: reverse application restores the original
    back = block
    for old, new, n in reversed(pairs):
        c = back.count(new)
        assert c == n, f"{label} inverse count {c} != {n}: {new[:60]!r}"
        back = back.replace(new, old)
    assert back == apply_pairs_source[label], f"{label} round-trip drift"
    return block

# ---- STALE block: W231 self-faces -> W232 self-faces ----
S = [
 ("共二百二十八面", "共二百二十九面", 1),
 ('"r963 窗 11:5x", "二百二十八"', '"r966 窗 13:2x", "二百二十九"', 1),
 ("523_004..525_003", "525_204..527_203", 1),
 ('"522_804..524_803", "522_804..523_003"', '"525_004..527_003", "525_004..525_203"', 1),
 ("523004", "525204", 2),
 ("525004", "527204", 2),
 ("523_004+j", "525_204+j", 1),
 ("525_004+j", "527_204+j", 1),
 ("第 229 枚", "第 230 枚", 1),
 ("NINETY-FIRST", "NINETY-SECOND", 1),
 ("第九十一例", "第九十二例", 1),
 ("第六十一枚", "第六十二枚", 1),
 ("220 注册在册", "221 注册在册", 1),
 ("bmc_ordinal=61", "bmc_ordinal=62", 1),
 ("r964 freeze 窗", "r967 freeze 窗", 1),
 ("0.3069", "0.3251", 1),
 ("0.09269286", "0.09268999", 1),
 ("0.090772", "0.09203368", 1),
 ("0.24504776", "0.24507072", 1),
 ("1155-bmc", "1345-bmc", 1),
 ("6638ddf9f", "8d3a1b78a", 1),
 ("11:5x（W230 面完整性", "13:2x（W231 面完整性", 1),
 ("11:5x finalize one-pass】", "13:2x finalize one-pass】", 1),
 ("机证 228 行", "机证 229 行", 1),
 ("第 221 波", "第 222 波", 1),
 ("n_eff_held_equal 927,589", "n_eff_held_equal 929,789", 1),
 ("line_pre_w230 1.192", "line_pre_w231 1.1921", 1),
 ("=**506,120 投影**", "=**508,320 投影**", 1),
 ("engine_owner==bm-c 60 行", "engine_owner==bm-c 61 行", 1),
 ("prose 61st", "prose 62nd", 1),
 ("r963 freeze receipt 60th", "r966 freeze receipt 61st", 1),
 ("第 61 枚 EXACT", "第 62 枚 EXACT", 1),
 ("pre-W231 宇宙", "pre-W232 宇宙", 1),
 ("W232 freezer 承接面", "W233 freezer 承接面", 1),
 ("r963 W230 §7 范式", "r966 W231 §7 范式", 1),
 ("r963 W230 §8 范式", "r966 W231 §8 范式", 1),
 ("r963/W230 先例", "r966/W231 先例", 1),
 ("W231 B 带 525_004..525_203 注册后将拒 naive W232", "W232 B 带 527_204..527_403 注册后将拒 naive W233", 1),
 ("（523_003+1）", "（525_203+1）", 1),
 ("（525_003+1）", "（527_203+1）", 1),
 ("波号 231=", "波号 232=", 1),
 ("n1_w231/ 分片计数增长", "n1_w232/ 分片计数增长", 1),
 ("PERPETUAL-N1-W231", "PERPETUAL-N1-W232", 1),
 # r972 absorb fix: three pairs were mis-aged one wave too far (dead session
 # aged W230->W232 measurement faces; STALE faces must be the W232 prereg
 # BASE's stale slots = W231 measurements -- base-presence audited count==1
 # each in results/_r972bmc_s_audit.py before this fix):
 ("line_merged@K503,920", "line_merged@K506,120", 1),
 ("实差 0.0019 在带内", "实差 0.0007 在带内", 1),
 ("parity 89 行", "parity 90 行", 1),
 ("W136..W230 先例链披露", "W136..W231 先例链披露", 1),
 ("W5..W230 先例", "W5..W231 先例", 1),
 ("v2..W230 落地", "v2..W231 落地", 1),
 ("W2..W230 落地 runner", "W2..W231 落地 runner", 1),
 ("W2..W230 带（冻结时点", "W2..W231 带（冻结时点", 1),
 ("W2..W230 全注册在冻结时点成立", "W2..W231 全注册在冻结时点成立", 1),
 ("W1..W230 N1 finalize 已全部落地", "W1..W231 N1 finalize 已全部落地", 1),
 ("W1..W230 已落账", "W1..W231 已落账", 1),
 ("（W1..W230 全落）", "（W1..W231 全落）", 1),
 ("503,920+2,200", "506,120+2,200", 1),
 ("K=503,920 合并池", "K=506,120 合并池", 1),
 ("净账本锚头 929,789", "净账本锚头 931,989", 1),
 ("净账本锚头 **929,789**", "净账本锚头 **931,989**", 1),
 ("splice 24e12fa5e", "splice aee0bd9fa", 1),  # r972 absorb fix #3 (was e58dbcda3 = W232's own splice = NEW face)
 ("W230 **0.000345**】", "W231 **0.000344**】", 1),
 ("verify at W232 prereg", "verify at W233 prereg", 1),
 ('"r963 窗", "2026-10-13 12:1x"', '"r966 窗", "2026-10-13 13:5x"', 1),
]
apply_pairs_source["STALE"] = stale_w231
stale_w232 = apply_pairs(stale_w231, S, "STALE")
t = t.replace(stale_w231, stale_w232)
print("STALE block advanced: W231->W232 68-entry, round-trip OK")

# ---- NEW block: W232 fresh faces -> W233 fresh faces ----
N = [
 ("第九十三例", "第九十四例", 1),          # before 九十二->九十三 creates a second
 ("第九十二例", "第九十三例", 1),
 ("NINETY-SECOND", "NINETY-THIRD", 1),
 ("PERPETUAL-N1-W232", "PERPETUAL-N1-W233", 1),
 ("第 230 枚", "第 231 枚", 1),
 ("525_204..527_203", "527_404..529_403", 1),
 ("527_204..527_403", "529_404..529_603", 1),
 ("527_204..529_203", "529_404..531_403", 1),   # S5.5 projection A (before ARITH_A re-creates this string)
 ("527_404..527_603", "529_604..529_803", 1),   # S5.5 projection B naive (before ARITH_B)
 ("525_004..527_003", "527_204..529_203", 1),   # ARITH_A
 ("525_204..525_403", "527_404..527_603", 1),   # ARITH_B / B_naive_first_clean
 ("第六十二枚", "第六十三枚", 1),
 ("931,989", "934,189", 1),              # ledger chain high-first
 ("929,789", "931,989", 2),              # standalone + n_eff_held_equal 929,789
 ("927,589", "929,789", 1),
 ("508,320", "510,520", 1),              # K chain high-first
 ("506,120", "508,320", 1),
 ("503,920", "506,120", 1),
 ("MSG-20261013-1345-bmc", "MSG-20261013-1530-bmc", 1),
 ("8d3a1b78a", "dd38a9da8", 1),
 ("bmc_ordinal=62", "bmc_ordinal=63", 1),
 ("n1_w232_results.json", "n1_w233_results.json", 1),
 ("n1_w231_results.json", "n1_w232_results.json", 1),
 ("0.3251", "0.3063", 1),
 ("0.09268999", "0.09274288", 1),
 ("0.09203368", "0.10490950", 1),
 ("0.24507072", "0.24508296", 1),
 ("1.1921", "1.1922", 1),
 ("第 222 波", "第 223 波", 1),
 ("实差 0.0007 在带内", "实差 0.0122 在带内", 1),
 ('"0.0007", "48c321706"', '"0.0122", "48c321706"', 1),
 ("第 62 枚 EXACT", "第 63 枚 EXACT", 1),
 ('aee0bd9fa", "第 63 枚 EXACT', 'aee0bd9fa", "e58dbcda3", "第 63 枚 EXACT', 1),
 ("W233 freezer 承接面", "W234 freezer 承接面", 1),
 ("r966 W231 §7 范式", "r968 W232 §7 范式", 1),
 ("parity 90 行", "parity 91 行", 1),
 ("二百二十九行", "二百三十行", 1),
 ("共二百二十九面", "共二百三十面", 1),
 ("机证 229 行", "机证 230 行", 1),
 ("r967 freeze 窗", "r972 freeze 窗", 1),
 ("prose 62nd", "prose 63rd", 1),
 ("61st owned 承袭", "62nd owned 承袭", 1),
 ("13:2x（W231 面完整性", "15:2x（W232 面完整性", 1),
 ("13:2x finalize one-pass】", "15:2x finalize one-pass】", 1),
 ("verify at W233 prereg", "verify at W234 prereg", 1),
 ("r966/W231 先例", "r968/W232 先例", 1),
 ("（525_203+1）", "（527_403+1）", 1),
 ("（527_203+1）", "（529_403+1）", 1),
 ("r966 窗实跑", "r972 窗实跑", 1),
 ("r966 窗 13:2x", "r968 窗 15:2x", 1),
 ("engine_owner==bm-c 61 行", "engine_owner==bm-c 62 行", 1),
]
apply_pairs_source["NEW"] = new_w232
new_w233 = apply_pairs(new_w232, N, "NEW")
t = t.replace(new_w232, new_w233)
print("NEW block advanced: W232->W233 (e58dbcda3 inserted), round-trip OK")

def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:70]!r}"
    t = t.replace(old, new)

# ---- NOTE comment ----
rep('''# NOTE: "525_004..527_003" / "525_204..525_403" are NOT stale in the W232
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 13:4x).
# "525_004..525_203" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w231_results.json" file refs stay (upstream
# legs) while "n1_w231/ 分片计数增长" IS stale (self shard face now n1_w232).
# "525004" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 527204; W231's 525004 appears only inside band-range strings with
# underscores (different token face).''',
    '''# NOTE: "527_204..529_203" / "527_404..527_603" are NOT stale in the W233
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 17:5x).
# "527_204..527_403" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w232_results.json" file refs stay (upstream
# legs) while "n1_w232/ 分片计数增长" IS stale (self shard face now n1_w233).
# "527204" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 529404; W232's 527204 appears only inside band-range strings with
# underscores (different token face).''')

# ---- in-band sanity + band asserts ----
rep('assert t.count("525_204..527_203") >= 4 and t.count("527_204..527_403") >= 4',
    'assert t.count("527_404..529_403") >= 4 and t.count("529_404..529_603") >= 4')
rep('''# upstream W231 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("525_004..525_203") >= 2''',
    '''# upstream W232 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("527_204..527_403") >= 2''')

# ---- chain-history legs: add W232 leg + n1_w232 file assert ----
rep('''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("+W231=bm-c r966 五面冻结（aee0bd9fa）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''',
    '''assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("+W231=bm-c r966 五面冻结（aee0bd9fa）") == 1
assert t.count("+W232=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1''')
rep('''assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1
assert t.count("n1_w231_results.json·13:2x") == 1''',
    '''assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1
assert t.count("n1_w231_results.json·13:2x") == 1
assert t.count("n1_w232_results.json·15:2x") == 1''')

# ---- healed RAM list + estate note + template ref + se_mu chain ----
rep('assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231 低 RAM 实烧先例") == 1',
    'assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232 低 RAM 实烧先例") == 1')
rep('assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231）") == 1',
    'assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232）") == 1')
rep('assert t.count("按 _w231bmc_freeze_edits.py 模板派生") == 1',
    'assert t.count("按 _w232bmc_freeze_edits.py 模板派生") == 1')
rep('assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**】") == 1',
    'assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**】") == 1')

# ---- out path + tail prints ----
rep('out = r"research\\PERPETUAL_N1_W232_PREREG.md"',
    'out = r"research\\PERPETUAL_N1_W233_PREREG.md"')
rep('print("W232 prereg derived OK:", out)',
    'print("W233 prereg derived OK:", out)')
rep('''print("W231(upper) refs (upstream, expected 40+):", t.count("W231"), "| W232 self:", t.count("W232"))
print("W230 heritage refs (chain legs + estate face):", t.count("W230"))''',
    '''print("W232(upper) refs (upstream, expected 40+):", t.count("W232"), "| W233 self:", t.count("W233"))
print("W231 heritage refs (chain legs + estate face):", t.count("W231"))''')

open(DST, "w", encoding="utf-8", newline="").write(t)
assert t.count("@@SUB_BLOCK@@") == 1, "SUB marker lost"
print("phase B OK: STALE/NEW/in-band/tail advanced; tpl bytes:", len(t.encode("utf-8")))
