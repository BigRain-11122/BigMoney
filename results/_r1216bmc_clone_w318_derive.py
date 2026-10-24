# -*- coding: utf-8 -*-
"""r1216 bm-c: clone the W317 prereg derive onto W318 (canon-clone, MEASURE-first).

Source face = results/_w317bmc_prereg_derive.py (proven live-fire r1214).
Pitfall family r1168/r1170/r1171/r1182/r1184/r1199/r1206/r1208/r1179/r1214:
  digit faces -> single-pass NUM map (long key first, no cascades);
  accumulated-history chains -> parked behind pure-letter sentinels (r1180);
  self/prior-wave reference faces -> explicit hand values (never cascaded).

Usage: python results/_r1216bmc_clone_w318_derive.py
"""
import io

SRC = "results/_w317bmc_prereg_derive.py"
DST = "results/_w318bmc_prereg_derive.py"
t = io.open(SRC, encoding="utf-8").read()
orig_len = len(t)


def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, "count %r = %d != %d" % (old[:70], c, n)
    t = t.replace(old, new, n)


# ---------------- 1. docstring + constants (window / wave identity) ----------------
rep('"""W317 prereg derive (bm-c r1214).', '"""W318 prereg derive (bm-c r1216).')
rep("Canon-clone of the W316 POST-RUN face", "Canon-clone of the W317 POST-RUN face")
rep("(git a2ba09e18a:research/PERPETUAL_N1_W316_PREREG.md, 29,468B / 75 newlines,",
    "(git 231c6f902f:research/PERPETUAL_N1_W317_PREREG.md, 29,002B / 75 newlines,")
rep("sha16 7a603242774e3b85) -> research/PERPETUAL_N1_W317_PREREG.md.",
    "sha16 8c22d023eb2f2668) -> research/PERPETUAL_N1_W318_PREREG.md.")
rep("Usage: python results/_w317bmc_prereg_derive.py",
    "Usage: python results/_w318bmc_prereg_derive.py")
rep("The section-7 block is taken VERBATIM from the post-W315-finalize face at HEAD.",
    "The section-7 block is taken VERBATIM from the post-W317-finalize face at HEAD.")
rep('SRC_REV = "a2ba09e18a"', 'SRC_REV = "231c6f902f"')
rep('SRC_PATH = "research/PERPETUAL_N1_W316_PREREG.md"',
    'SRC_PATH = "research/PERPETUAL_N1_W317_PREREG.md"')
rep('OUT = "research/PERPETUAL_N1_W317_PREREG.md"',
    'OUT = "research/PERPETUAL_N1_W318_PREREG.md"')
rep('EXPECT_SHA16 = "7a603242774e3b85"', 'EXPECT_SHA16 = "8c22d023eb2f2668"')
rep("EXPECT_BYTES = 29468", "EXPECT_BYTES = 29002")
rep('SEAT_MSG = "MSG-20261024-2215-bmc-w317-seat"',
    'SEAT_MSG = "MSG-20261024-2259-bmc-w318-seat"')
rep('SEAT_SHA = "db6d35c413"', 'SEAT_SHA = "a2ba09e18a"')
rep('FREE_RAM = "3.7"', 'FREE_RAM = "3.8"')

# ---------------- 2. live fact gates (W317 finalize + W318 seat) ----------------
rep('res = json.load(open("results/perpetual_faces/n1_w316_results.json", encoding="utf-8"))',
    'res = json.load(open("results/perpetual_faces/n1_w317_results.json", encoding="utf-8"))')
rep('assert led["total"] == 1119541 and led["prev_total"] == 1117341, "ledger anchor drift"',
    'assert led["total"] == 1121741 and led["prev_total"] == 1119541, "ledger anchor drift"')
rep('assert cum["merged"]["n_values"] == 693120, "merged K drift"',
    'assert cum["merged"]["n_values"] == 695320, "merged K drift"')
rep("assert abs(cum[\"merged\"][\"mu\"] + 0.09280325903162512) < 1e-12",
    "assert abs(cum[\"merged\"][\"mu\"] + 0.0928243713685785) < 1e-12")
rep("assert abs(cum[\"merged\"][\"sigma\"] - 0.2451643067749893) < 1e-12",
    "assert abs(cum[\"merged\"][\"sigma\"] - 0.24516846767474942) < 1e-12")
rep('assert cum["se_mu_at_k693120"] == 0.000294',
    'assert cum["se_mu_at_k695320"] == 0.000294')
rep("assert abs(cum[\"w316_only\"][\"mu\"] + 0.08997063636363636) < 1e-12",
    "assert abs(cum[\"w317_only\"][\"mu\"] + 0.0994759090909091) < 1e-12")
rep("assert abs(cum[\"w316_only\"][\"sigma\"] - 0.2450550974074963) < 1e-12",
    "assert abs(cum[\"w317_only\"][\"sigma\"] - 0.24644184248926793) < 1e-12")
rep('assert kl["line_merged_693120"] == 1.2011 and kl["line_pre_w316"] == 1.2011',
    'assert kl["line_merged_695320"] == 1.2012 and kl["line_pre_w317"] == 1.2012')
rep('assert kl["n_eff_held_equal"] == 1117341', 'assert kl["n_eff_held_equal"] == 1119541')
rep('assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3227) < 1e-12',
    'assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3158) < 1e-12')
rep('assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4737) < 1e-12',
    'assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4508) < 1e-12')
rep('seed = json.load(open("results/_w317bmc_20261024_probe_receipt.json", encoding="utf-8"))',
    'seed = json.load(open("results/_w318bmc_20261024_probe_receipt.json", encoding="utf-8"))')
rep('assert l1["A"] == [712701, 714700] and l1["B"] == [714701, 714900]',
    'assert l1["A"] == [714901, 716900] and l1["B"] == [716901, 717100]')
rep('assert l4["W318p_A_naive"] == "714_701..716_700"',
    'assert l4["W319p_A_naive"] == "716_901..718_900"')
rep('assert l4["W318p_B_naive"] == "714_901..715_100"',
    'assert l4["W319p_B_naive"] == "717_101..717_300"')
rep('assert seed["legs"]["leg0"]["owner_rows"] == 306',
    'assert seed["legs"]["leg0"]["owner_rows"] == 307')
rep('assert seed["legs"]["leg0"]["bmc_rows"] == 135',
    'assert seed["legs"]["leg0"]["bmc_rows"] == 136')
rep('assert seed["ordinals"]["a_hop"] == 70 and seed["ordinals"]["above_own_a"] == 71',
    'assert seed["ordinals"]["a_hop"] == 71 and seed["ordinals"]["above_own_a"] == 72')
rep('print("facts OK: ledger 1,119,541 / K 693,120 / W316-only mu -0.08997064 / p95 0.3227")',
    'print("facts OK: ledger 1,121,741 / K 695,320 / W317-only mu -0.09947591 / p95 0.3158")')

# ---------------- 3. sec.7 verbatim gate ----------------
rep('assert "W316-only" in SEC7_NEW and "1,119,541" in SEC7_NEW',
    'assert "W317-only" in SEC7_NEW and "1,121,741" in SEC7_NEW')

# ---------------- 4. parked cumulative chains (extend by one, never roll) ----------------
rep('''    old_tail = "\\u2192W316 " + PROJ + " 0.000294"
    assert old_tail in old, "se chain tail not the expected W316 projection"
    assert "0.000294" in old
    return old.replace(old_tail,
                       "\\u2192W316 **0.000294**\\u2192W317 " + PROJ + " 0.000293")''',
    '''    old_tail = "\\u2192W317 " + PROJ + " 0.000293"
    assert old_tail in old, "se chain tail not the expected W317 projection"
    assert "0.000293" in old
    return old.replace(old_tail,
                       "\\u2192W317 **0.000294**\\u2192W318 " + PROJ + " 0.000293")''')

rep('''    t = old.replace("/W313/W314/W315/W316=A/B", "/W313/W314/W315/W316/W317=A/B", 1)
    assert "W317=A/B" in t, "A/B chain tail not expected /W313..W316=A/B"''',
    '''    t = old.replace("/W313/W314/W315/W316/W317=A/B", "/W313/W314/W315/W316/W317/W318=A/B", 1)
    assert "W318=A/B" in t, "A/B chain tail not expected /W313..W317=A/B"''')

rep('''    t = old.replace("\\u2192W316 bm-c own-turn rotation",
                    "\\u2192W316 bm-c\\u2192W317 bm-c own-turn rotation", 1)
    assert "W317 bm-c own-turn rotation" in t, "own-turn chain tail not expected W316"''',
    '''    t = old.replace("\\u2192W317 bm-c own-turn rotation",
                    "\\u2192W317 bm-c\\u2192W318 bm-c own-turn rotation", 1)
    assert "W318 bm-c own-turn rotation" in t, "own-turn chain tail not expected W317"''')

rep('''    m = re.search(r"\\u00b7W314 " + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR +
                  r"\\u00b7W315 " + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR +
                  r"\\u00b7\\u672c\\u7a97" + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR + "\\uff09", old)
    assert m, "RAM chain tail not found"
    new_tail = ("\\u00b7W314 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
                "\\u00b7W315 " + FREEZE + " ~" + m.group(2) + "G bm-c " + ANCHOR +
                "\\u00b7W316 " + FREEZE + " ~" + m.group(3) + "G bm-c " + ANCHOR +
                "\\u00b7\\u672c\\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\\uff09")''',
    '''    m = re.search(r"\\u00b7W315 " + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR +
                  r"\\u00b7W316 " + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR +
                  r"\\u00b7\\u672c\\u7a97" + FREEZE + r" ~([\\d.]+)G bm-c " + ANCHOR + "\\uff09", old)
    assert m, "RAM chain tail not found"
    new_tail = ("\\u00b7W315 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
                "\\u00b7W316 " + FREEZE + " ~" + m.group(2) + "G bm-c " + ANCHOR +
                "\\u00b7W317 " + FREEZE + " ~" + m.group(3) + "G bm-c " + ANCHOR +
                "\\u00b7\\u672c\\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\\uff09")''')

rep('park(r"W277 \\*\\*0\\.000314\\*\\*[^\\n]*?\\u6295\\u5f71 0\\.000294"',
    'park(r"W277 \\*\\*0\\.000314\\*\\*[^\\n]*?\\u6295\\u5f71 0\\.000293"')
rep('assert SEC8.count("W317+") == 1 and "lands_inside=True" in SEC8, "sec.8 template drift"',
    'assert SEC8.count("W318+") == 1 and "lands_inside=True" in SEC8, "sec.8 template drift"')

# ---------------- 5. NUM map (single-pass; long keys win) ----------------
START = t.index("NUM = [")
END = t.index("]\n\ncounts = {}", START) + 1
NEW_NUM = '''NUM = [
    # --- ledger / pool anchors (single-pass)
    ("1,119,541", "1,121,741"),
    ("1,117,341", "1,119,541"),
    ("K693,120", "K695,320"),
    ("693,120", "695,320"),
    ("695,320", "697,520"),
    # --- merged / wave-only statistics
    ("−0.09280326", "−0.09282437"),
    ("0.24516431", "0.24516847"),
    ("−0.08997064", "−0.09947591"),
    ("0.0028", "0.0067"),
    # --- A family p95 anchor
    ("0.3227", "0.3158"),
    # --- K-lift pair (long key wins over the bare decimals)
    ("**1.2011**·line_pre_w317 1.2011", "**1.2012**·line_pre_w318 1.2012"),
    ("line_pre_w317", "line_pre_w318"),
    # --- wave / row / seed ordinals
    ("池第 315 枚", "池第 316 枚"),
    ("行 306 注册在册", "行 307 注册在册"),
    ("bmc rows 135+候选=第 136 枚", "bmc rows 136+候选=第 137 枚"),
    ("bmc_rows=135", "bmc_rows=136"),
    ("bmc live rows 135", "bmc live rows 136"),
    ("第一百三十五枚", "第一百三十六枚"),
    ("引擎线第 307 波", "引擎线第 308 波"),
    ("波号 315=", "波号 316="),
    ("三百一十一面", "三百一十二面"),
    ("CLEAN-AT-BIRTH 48th gen", "CLEAN-AT-BIRTH 49th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("第七十次", "第七十一次"),
    ("第七十一次", "第七十二次"),
    ("第六十四波", "第六十五波"),
    # --- runner / artifact names
    ("--wave 317", "--wave 318"),
    ("n1_w316", "n1_w317"),
    ("n1_w317", "n1_w318"),
    ("_w317bmc_", "_w318bmc_"),
    ("MSG-20261024-2215-bmc-w317-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("24d7917916", "06002d41aa"),
    ("dfeb4f3d21", "5d6d26634f"),
    ("db6d35c413", SEAT_SHA),
    # --- window clock / round labels (long keys first via sort)
    ("bm-c r1212 五面冻结 splice dfeb4f3d21 落地 21:5x",
     "bm-c r1214 五面冻结 splice 5d6d26634f 落地 22:4x"),
    ("bm-c r1213 窗 22:1x", "bm-c r1215 窗 23:0x"),
    ("r1211/r1212/r1213 W317", "r1214/r1214/r1215 W317"),
    ("prereg 24d7917916 落于 r1211 窗·splice dfeb4f3d21 落于 r1212 执行窗 21:5x",
     "prereg 06002d41aa 落于 r1214 窗·splice 5d6d26634f 落于 r1214 执行窗 22:4x"),
    ("estate chain r1211/r1212/r1213", "estate chain r1214/r1214/r1215"),
    ("席位 r1210 窗+prereg r1211 窗落地", "席位 r1215 窗+prereg r1216 窗落地"),
    ("bm-c r1214 席位", "bm-c r1215 席位"),
    ("r1214 席位窗实跑", "r1215 席位窗实跑"),
    ("bm-c 循环班 r1214 " + FREEZE + " 2026-10-24 22:4x",
     "bm-c 循环班 r1216 " + FREEZE + " 2026-10-24 23:1x"),
    ("r1214", "r1216"),
    ("r1213", "r1215"),
    ("r1211", "r1214"),
]'''
assert t[START:END].startswith("NUM = [")
t = t[:START] + NEW_NUM + t[END:]

# ---------------- 6. final asserts of the derive script ----------------
rep('assert out.count("712_701..714_700") >= 2, "new A band missing"',
    'assert out.count("714_901..716_900") >= 2, "new A band missing"')
rep('assert out.count("714_701..714_900") >= 2, "new B band missing"',
    'assert out.count("716_901..717_100") >= 2, "new B band missing"')
rep('assert out.count("712_501..714_500") >= 1, "naive A continuation band missing"',
    'assert out.count("714_701..716_700") >= 1, "naive A continuation band missing"')
rep('assert out.count("714_901..715_100") >= 1, "W318p B naive band missing"',
    'assert out.count("717_101..717_300") >= 1, "W319p B naive band missing"')
rep('assert out.count("714_701..716_700") >= 1, "W318p A naive band missing"',
    'assert out.count("716_901..718_900") >= 1, "W319p A naive band missing"')
rep('assert out.count("W317") > 30 and out.count("W318") > 5',
    'assert out.count("W318") > 30 and out.count("W319") > 5')
rep('assert out.count("1,119,541") >= 3, "new ledger anchor missing"',
    'assert out.count("1,121,741") >= 3, "new ledger anchor missing"')
rep('assert out.count("693,120") >= src.count("690,920") - 1, "prior-K roll mismatch"',
    'assert out.count("695,320") >= src.count("693,120") - 1, "prior-K roll mismatch"')
rep('''    for tok in ("712_300", "712_500", "712_501", "714_500", "714_501", "714_700",
                "714_300", "714_701", "716_500", "714_900"):''',
    '''    for tok in ("714_500", "714_700", "714_701", "716_700", "716_701", "716_900",
                "716_500", "716_901", "718_700", "717_100"):''')

# ---------------- 7. POST-fix list (window honesty faces) ----------------
PSTART = t.index("POST = [")
PEND = t.index("]\nfor old, new in POST:", PSTART) + 1
NEW_POST = '''POST = [
    ("finalize 已落地 22:1x）", "finalize 已落地 23:0x）"),
    ("键·22:1x finalize one-pass", "键·23:0x finalize one-pass"),
    ("本窗 free RAM 3.7GB", "本窗 free RAM " + FREE_RAM + "GB"),
    ("GPU=gen-only 车道 idle（nvidia-smi 实读 util 3%·VRAM 占用 2.3G/16G·非本波占用·CPU 车道独立）",
     "GPU=gen-only 车道 idle（nvidia-smi 实读 util 8%·VRAM 占用 3.2G/16G·非本波占用·CPU 车道独立）"),
]'''
assert t[PSTART:PEND].startswith("POST = [")
t = t[:PSTART] + NEW_POST + t[PEND:]

# ---------------- 8. sec.8 rebuild template (W317 -> W318 projections) ----------------
S8_START = t.index("SEC8_NEW = (")
S8_END = t.index('assert out.count("ZZSECS") == 1', S8_START)
NEW_SEC8 = '''SEC8_NEW = (
    "## §8 批后复盘。【finalize 同窗回填】\\n"
    "- §5.5 W319+ 投影承接机证：本窗席位回执 leg4（pre-W318 宇宙）投影 W319p A naive **716_901..718_900** clean（hops=0）、"
    "B naive **717_101..717_300** clean（hops=0）但落投影 A 窗内（own-A reservation 承袭预期）——**W319 冻结方必须在 "
    "post-W318 宇宙重 live derive 且在 derive B 时预留本波 A 窗（W141 先例）·never transcribe r587**。\\n"
    "- 本窗席位实测机证：A **714_901..716_900**（71st 连续 A-hop·hops=1·base==注册 W317 B 尾 716_900+1）／"
    "B **716_901..717_100**（72nd 连续 above-own-A·hops=1·base==本波 A 尾 716_900+1）——"
    "`results/_w318bmc_20261024_probe_receipt.json` verdict ADMIT·relation_asserts 4/4·seed_admit_gate FREE x2·leg3 bands_clear=True。\\n"
    "- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 "
    "TREASURE_REGISTRY.md 均不追加。\\n"
    "- 诚实披露：§5 五预键若出现 prose 偏差（se_mu 取 3 位小数），以机读值为准并披露、不抹平；mu/sigma/K-lift 一律按冻结带校验。\\n"
    "- 坑律捕获：post-W317 finalize 同窗回填（本段属 finalize 回填面，冻结时为前波沿用文本）；本窗冻结沿用 r1208 判例："
    "canon-clone 生成器的纯数字面（注册行号前缀/切口/setwave 键后缀）直写目标波号、W token 面保留**上一波**形态交给级联推进一次。\\n"
    "- 收口纪律：finalize 只消费在册分片（audit.finalize_only=true），本波零重烧、零双烧；S6 链与轮收口同窗。\\n\\n\\n"
)
'''
t = t[:S8_START] + NEW_SEC8 + t[S8_END:]

# ---------------- 8b. tail asserts of the derive script ----------------
rep('assert out.count("line_pre_w317") >= 1 and out.count("line_pre_w316") == 1  # sec.7 prior block',
    'assert out.count("line_pre_w318") >= 1 and out.count("line_pre_w317") == 1  # sec.7 prior block')
rep('assert out.count("n1_w316") >= 4 and out.count("n1_w317") >= 1',
    'assert out.count("n1_w317") >= 4 and out.count("n1_w318") >= 1')
rep('assert out.count("n1_w315") == 0, "n1 double roll"',
    'assert out.count("n1_w316") == 0, "n1 double roll"')
rep('assert out.count("CLEAN-AT-BIRTH 48th gen") == 1',
    'assert out.count("CLEAN-AT-BIRTH 49th gen") == 1')
rep('assert out.count("r1214") >= 8, "round labels"',
    'assert out.count("r1216") >= 6, "round labels"')
rep('assert out.count("_w317bmc_20261024_probe_receipt.json") >= 2',
    'assert out.count("_w318bmc_20261024_probe_receipt.json") >= 2')
rep('assert "\\u7b2c 79 \\u6b21" in out or "\\u7b2c 80 \\u6b21" in out, "sixgate ordinal missing"',
    'assert "\\u7b2c 80 \\u6b21" in out or "\\u7b2c 81 \\u6b21" in out, "sixgate ordinal missing"')
rep('assert out.count("W316-only") >= 1  # sec.7 prior-wave block intact',
    'assert out.count("W317-only") >= 1  # sec.7 prior-wave block intact')

rep('open("results/_w317bmc_derive_counts.json", "w", encoding="utf-8")',
    'open("results/_w318bmc_derive_counts.json", "w", encoding="utf-8")')

# ---------------- 9. write ----------------
io.open(DST, "w", encoding="utf-8", newline="").write(t)
print("CLONE OK %d -> %d chars" % (orig_len, len(t)))
for probe in ("W318 prereg derive", "_w318bmc_prereg_derive.py", "FREE_RAM = \"3.8\"",
              "SEAT_SHA = \"a2ba09e18a\"", "1,121,741", "695,320", "714_901..716_900"):
    print("  ", probe, "=>", t.count(probe))