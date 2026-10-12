
# ---------- build + apply W228 pairs ----------
PAIRS = []
for i, old in enumerate(OLD27):
    new = old
    for find, repl in SUB[i]:
        c = new.count(find)
        assert c == 1, f"submap[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    PAIRS.append((old, new))

for old, new in PAIRS:
    c = t.count(old)
    assert c == 1, f"pair count {c} != 1: {old[:70]}..."
    t = t.replace(old, new, 1)

# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W227 self face (each count==1 asserted). Remaining
# "W227" tokens = pair-written legit refs (chain W227 leg, refusing band,
# W227 finalize keys, W1..W227 scope) which must STAY W227 -- mask, then age
# one-wave-older W226 refs to W227, then restore. @L26@/@T26@ hold heritage
# tokens immune.
t = t.replace("n1_w227_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W227", "PERPETUAL-N1-W228")
t = t.replace("PERPETUAL_N1_W227", "PERPETUAL_N1_W228")
t = t.replace("n1_w227", "n1_w228")
t = t.replace("_w227bmc", "_w228bmc")
t = t.replace("W227", "@U_W@")
t = t.replace("W226", "W227")
t = t.replace("n1_w226", "n1_w227")
t = t.replace("PERPETUAL_N1_W226", "PERPETUAL_N1_W227")
t = t.replace("_w226bmc", "_w227bmc")
t = t.replace("@u_w@", "w227")
t = t.replace("@U_W@", "W227")
t = t.replace("@L26@", "226")
t = t.replace("@T26@", "27")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["514_204..516_203", "514_004..516_003", "514_004..514_203", "514_204..514_403",
         "514204", "516204", "514_204+j", "516_204+j", "第 225 枚", "EIGHTY-SEVENTH", "第八十七例", "第五十七枚",
         "216 注册在册", "bmc_ordinal=57", "r956 freeze 窗", "0.3199", "\u2212" + "0.09279386",
         "\u2212" + "0.09264214", "0.24510059", "0645-bmc", "10781c2f8",
         "22:4x（W226 面完整性", "22:4x finalize one-pass】", "r943 窗 22:4x", "二百二十四行",
         "共二百二十四面", "机证 224 行", "第 217 波",
         "n_eff_held_equal 918,789", "line_pre_w226 1.1916", "=**497,320 投影**", "engine_owner==bm-c 56 行",
         "prose 57th", "r943 freeze receipt 56th", "第 57 枚 EXACT", "pre-W227 宇宙",
         "W228 freezer 承接面", "r944 W226 §7 范式", "r944 W226 §8 范式", "r943/W226 先例",
         "W227 B 带 516_204..516_403 注册后将拒 naive W228",
         "（514_203+1）", "（516_203+1）", "波号 227=", "A base=514204", "B base=516204", "n1_w227/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W227"', "line_merged@K495,120",
         "实差 0.0002 在带内", "parity 85 行",
         "W136..W226 先例链披露", "W5..W226 先例", "v2..W226 落地", "W2..W226 落地 runner",
         "W2..W226 带（冻结时点", "W2..W226 全注册在冻结时点成立", "W1..W226 N1 finalize 已全部落地",
         "W1..W226 已落账", "（W1..W226 全落）", "495,120+2,200", "K=495,120 合并池",
         "净账本锚头 920,989", "净账本锚头 **920,989**", "splice 9b44d37d1", "W226 **0.000348**】",
         "verify at W228 prereg", "r955 窗", "2026-10-13 6:3x"]
# NOTE: "516_204..518_203" / "516_404..516_603" are NOT stale in the W228
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 07:2x).
# "516_204..516_403" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w227_results.json" file refs stay (upstream
# legs) while "n1_w227/ 分片计数增长" IS stale (self shard face now n1_w228).
# "516204" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 518404; W227's 516204 appears only inside band-range strings with
# underscores (different token face).
for s in STALE:
    c = t.count(s)
    if c:
        import re as _re2
        for m in _re2.finditer(_re2.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-160):m.end()+80].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W228", "第 226 枚", "516_404..518_403", "518_404..518_603",
       "EIGHTY-EIGHTH", "第八十八例", "第八十九例", "第五十八枚",
       "923,189", "497,320", "499,520", "920,989",
       "MSG-20261013-0720-bmc", "4e30ddf69",
       "bmc_ordinal=58", "n1_w228_results.json", "0.3206", "\u2212" + "0.09275553",
       "\u2212" + "0.08412782", "0.24507723", "n_eff_held_equal 920,989", "0.000348",
       "1.1917", "第 218 波", "518_404..520_403", "518_604..518_803",
       "516_204..518_203", "516_404..516_603",
       "0.0086", "bd50be730", "48c321706", "第 58 枚 EXACT", "W229 freezer 承接面",
       "r956 W227 §7 范式", "K-lift **+0.0000**", "实差 0.0086 在带内",
       "parity 86 行", "二百二十五行", "共二百二十五面", "机证 225 行",
       "r958 freeze 窗", "prose 58th", "57th owned 承袭",
       "06:5x（W227 面完整性", "06:5x finalize one-pass】", "verify at W229 prereg",
       "r956/W227 先例", "（516_403+1）", "（518_403+1）", "r957 窗实跑", "r956 窗 06:5x",
       "engine_owner==bm-c 57 行"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("516_404..518_403") >= 4 and t.count("518_404..518_603") >= 4
# upstream W227 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("516_204..516_403") >= 2
# chain-history legs present exactly once each (heritage restored verbatim)
assert t.count("+W213=bm-c r908 五面冻结（a24069f4c）") == 1
assert t.count("+W214=bm-c r910 五面冻结（4664900c8）") == 1
assert t.count("+W215=bm-c r912 五面冻结（1e71c3b93）") == 1
assert t.count("+W216=bm-c r914 五面冻结（0b3c489f0）") == 1
assert t.count("+W217=bm-c r916 五面冻结（ad011fee2）") == 1
assert t.count("+W218=bm-c r918 五面冻结（9afb0b1d7）") == 1
assert t.count("+W219=bm-c r920 五面冻结（0dae35332）") == 1
assert t.count("+W220=bm-c r923 五面冻结（a9aee1d05）") == 1
assert t.count("+W221=bm-c r928 五面冻结（98da27a40）") == 1
assert t.count("+W222=bm-c r931 死窗五面冻结") == 1
assert t.count("+W223=bm-c r934 五面冻结（448c4d8c2）") == 1
assert t.count("+W224=bm-c r937 死窗五面冻结") == 1
assert t.count("+W225=bm-c r939 五面冻结（84ecb3a3a）") == 1
assert t.count("+W226=bm-c r943 死窗五面冻结") == 1
assert t.count("+W227=bm-c r956 五面冻结（48c321706）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1
assert t.count("n1_w214_results.json·05:2x") == 1
assert t.count("n1_w215_results.json·06:1x") == 1
assert t.count("n1_w216_results.json·06:5x") == 1
assert t.count("n1_w217_results.json·08:1x") == 1
assert t.count("n1_w218_results.json·09:1x") == 1
assert t.count("n1_w219_results.json·10:1x") == 1
assert t.count("n1_w220_results.json·12:0x") == 1
assert t.count("n1_w221_results.json·14:1x") == 1
assert t.count("n1_w222_results.json·15:5x") == 1
assert t.count("n1_w223_results.json·17:2x") == 1
assert t.count("n1_w224_results.json·19:1x") == 1
assert t.count("n1_w225_results.json·20:2x") == 1
assert t.count("n1_w226_results.json·22:4x") == 1
assert t.count("n1_w227_results.json·06:5x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227）") == 1
assert t.count("按 _w227bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**】") == 1

out = r"research\PERPETUAL_N1_W228_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W228 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W227(upper) refs (upstream, expected 40+):", t.count("W227"), "| W228 self:", t.count("W228"))
print("W226 heritage refs (chain legs + estate face):", t.count("W226"))
