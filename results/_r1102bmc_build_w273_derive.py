# -*- coding: utf-8 -*-
# r1102 bm-c: W273 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w272bmc_prereg_derive.py -> results/_w273bmc_prereg_derive.py.
# Zero hand-transcription of chain values: W273 bands/anchors read from the seat receipt +
# fivekeys/results/facts jsons; floors MEASURED on the frozen W272 template (r1077 law) and
# rewritten in-place; complex value spans placeholder-protected before the general rolls.
# Needle evidence receipt -> results/_w273bmc_needle_probe.json (probe folded into builder).
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w273bmc_w272_frozen_face.txt"), encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23409
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "b023511eba80a9bf"
fk = json.load(open(os.path.join(REPO, "results", "_r1100bmc_w272_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w273bmc_20261018_probe_receipt.json"), encoding="utf-8"))
facts = json.load(open(os.path.join(REPO, "results", "_w273bmc_facts.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [615901, 617900] and rcp["bands"]["B"] == [617901, 618100]
assert round(fk["merged"]["mu"], 8) == -0.09277998 and round(fk["merged"]["sigma"], 8) == 0.24509581
assert round(fk["w272_only"]["mu"], 8) == -0.09706318 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3138
assert round(fk["merged"]["se_mu_k596320"], 6) == 0.000317 and fk["ledger_identity"]["total"] == 1022735
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w272_vs_merged_mu_gap"][0]
DIFF4 = "%.4f" % round(_k1["value"], 4)  # 0.0043
RAM = round(subprocess.run(["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"],
           capture_output=True, text=True).stdout.strip() and float(subprocess.run(
           ["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"],
           capture_output=True, text=True).stdout) or 0, 1)
ram_face = "~%.1fGB" % RAM
ram_anchor = "~%.1fG" % RAM
TWIN_SIZE = subprocess.run([GIT, "cat-file", "-s", "HEAD:research/PERPETUAL_N1_W272_PREREG.md"],
                            capture_output=True, text=True, cwd=REPO).stdout.strip()
SRC = io.open(os.path.join(REPO, "results", "_w272bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected complex spans (old exact -> new final) ----------------
OLD_RAM_T = "本窗 free RAM ~1.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.2G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"
LED_T = "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚）"
LED_S1 = "W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚）"
LED_T1 = LED_T[:-1] + "·W272 冻结窗 " + ram_anchor + " bm-c 实锚）"
SPANS = [
 ("S1", '("17:2x", "18:4x", 5),', '("18:4x", "20:4x", 4),'),
 ("S2", '("（W271 实测键 **−0.09272692**·K=591,920 合并池·W271-only 实测 **−0.09170727**）",\n     "（W271 实测键 **−0.09276412**·K=594,120 合并池·W271-only 实测 **−0.10277223**）", 1),',
  '("（W272 实测键 **−0.09276412**·K=594,120 合并池·W272-only 实测 **−0.10277223**）",\n     "（W272 实测键 **−0.09277998**·K=596,320 合并池·W272-only 实测 **−0.09706318**）", 1),'),
 ("S3", '("W271-only vs merged 实差 0.0010 在带内", "W271-only vs merged 实差 0.0100 在带内", 1),',
  '("W272-only vs merged 实差 0.0100 在带内", "W272-only vs merged 实差 ' + DIFF4 + ' 在带内", 1),'),
 ("S4", '("键 W271 实测 K-lift **+0.0000**·line_merged@K591,920 **1.1962**·line_pre_w270 1.1962·n_eff_held_equal 1,016,135",\n     "键 W271 实测 K-lift **+0.0001**·line_merged@K594,120 **1.1964**·line_pre_w271 1.1963·n_eff_held_equal 1,018,335", 1),',
  '("键 W272 实测 K-lift **+0.0001**·line_merged@K594,120 **1.1964**·line_pre_w271 1.1963·n_eff_held_equal 1,018,335",\n     "键 W272 实测 K-lift **+0.0000**·line_merged@K596,320 **1.1965**·line_pre_w272 1.1965·n_eff_held_equal 1,020,535", 1),'),
 ("S5", '("→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 投影 0.000319】",\n     "→W266 **0.000321**→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 投影 0.000318】", 1),',
  '("→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 投影 0.000318】",\n     "→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 投影 0.000317】", 1),'),
 ("S6", '("bm-c r1095 W271 §7 范式", "bm-c r1097 W271 §7 范式", 1),',
  '("bm-c r1097 W272 §7 范式", "bm-c r1100 W272 §7 范式", 1),'),
 ("S7", '("bm-c r1095 W271 §8 范式", "bm-c r1097 W271 §8 范式", 1),',
  '("bm-c r1097 W272 §8 范式", "bm-c r1100 W272 §8 范式", 1),'),
 ("S8", '("本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 95%·7.9G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",\n     "' + OLD_RAM_T + '", 1),',
  '("' + OLD_RAM_T + '",\n     "本窗 free RAM ' + ram_face + '（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.2G VRAM 占用·MV PACK-A i2v wave-3 收官烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),'),
 ("S9", '("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚）",\n     "' + LED_T + '", 1),',
  '("' + LED_S1 + '",\n     "' + LED_T1 + '", 1),'),
 ("S10", '"W206/W211..W271 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",\n    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",\n    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",\n    "W271 冻结窗 ~1.4G bm-c 实锚",',
  '"W206/W211..W272 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",\n    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",\n    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",\n    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ' + ram_anchor + ' bm-c 实锚",'),
 ("S11", '"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",\n    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G",',
  '"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",\n    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G",'),
 ("S12", '"MSG-20261018-175x", "87d2697cdc", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb",',
  '"MSG-20261018-191x", "f608ff1cee", "87d2697cdc", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",'),
 ("S13", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x",',
  '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x",'),
 ("S14", '# r1099 bm-c: W272 prereg derive (count-asserted ordered transform + marker-extracted block replaces).',
  '# r1102 bm-c: W273 prereg derive (count-asserted ordered transform + marker-extracted block replaces).'),
]
txt = SRC
for sid, old, new in SPANS:
    c = txt.count(old)
    assert c == 1, "SPAN %s count=%d (expect 1)" % (sid, c)
    txt = txt.replace(old, "\x02%s\x02" % sid)

NEEDLES = [
 # -- G+1 consumes (fire before everything that creates their outputs) --
 ("W274 冻结方", "W275 冻结方"), ("W273p_", "W274p_"), ("verify at W273 prereg", "verify at W274 prereg"),
 ("W273/W274", "W274/W275"), ("W272/W273", "W273/W274"), ("R273", "R274"), ("W273+ ", "W274+ "),
 ("第二十二次连续 A-hop", "第二十三次连续 A-hop"), ("第二十二次连续 above-own-A", "第二十三次连续 above-own-A"),
 ("第二十一次连续 A-hop", "第二十二次连续 A-hop"), ("第二十次连续 A-hop", "第二十一次连续 A-hop"),
 ("第二十一次连续 above-own-A", "第二十二次连续 above-own-A"), ("第二十次连续 above-own-A", "第二十一次连续 above-own-A"),
 ("连续二十一波", "连续二十二波"), ("连续二十波", "连续二十一波"),
 ("共二百七十面", "共二百七十一面"), ("共二百六十九面", "共二百七十面"),
 ("TWENTY-SECOND consecutive above-own-A", "TWENTY-THIRD consecutive above-own-A"),
 ("TWENTY-FIRST consecutive A-hop", "TWENTY-SECOND consecutive A-hop"),
 # -- numbers/shas/values (descending consume) --
 ("1,020,535", "1,022,735"), ("1,018,335", "1,020,535"), ("1,016,135", "1,018,335"),
 ("1020535", "1022735"), ("1018335", "1020535"), ("1016135", "1018335"),
 ("596,320 投影", "598,520 投影"), ('"596,320": 0', '"598,520": 0'), ("594,120", "596,320"), ("591,920", "594,120"),
 ("594120", "596320"), ("591920", "594120"),
 ("**+0.0001**", "**+0.0000**"), ("K-lift +0.0001", "K-lift +0.0000"), ("== 0.0001", "== 0.0"),
 ("0.000318", "0.000317"), ("0.000319", "0.000318"),
 ("0.01000810891279999", "0.0042832029477766626"), ("(4dp 0.0100)", "(4dp %s)" % DIFF4),
 ("-0.09276411835992728", "-0.09277997887040515"), ("0.24509039950538597", "0.24509581465156932"),
 ("-0.10277222727272727", "-0.09706318181818181"),
 ("-0.09276412", "-0.09277998"), ("−0.09276412", "−0.09277998"), ("−0.09272692", "−0.09276412"),
 ("0.24509040", "0.24509581"), ("0.24507005", "0.24509040"),
 ("-0.10277223", "-0.09706318"), ("−0.10277223", "−0.09706318"), ("−0.09170727", "−0.10277223"),
 ("0.3042", "0.3138"), ("**0.3268**", "**0.3042**"),
 ("1.1964", "1.1965"), ("1.1963", "1.1965"),
 ("line_pre_w271", "line_pre_w272"), ("line_pre_w270", "line_pre_w271"),
 ("== 0.01 and _k1", "== %s and _k1" % DIFF4), ("实差 0.0100 在带内", "实差 %s 在带内" % DIFF4),
 ("= 0.0100 @4dp", "= %s @4dp" % DIFF4),
 # -- underscore bands (G+1/G0 consume, then G-1 roll) --
 ("615_901..616_100", "618_101..618_300"), ("615_701..617_700", "617_901..619_900"),
 ("615_701..615_900", "617_901..618_100"), ("613_701..615_700", "615_901..617_900"),
 ("613_501..615_500", "615_701..617_700"), ("613_701..613_900", "615_901..616_100"),
 ("613_501..613_700", "615_701..615_900"),
 ("611_501..613_500", "613_701..615_700"), ("611_301..613_300", "613_501..615_500"),
 ("611_301..611_500", "613_501..613_700"), ("611_101..611_300", "613_301..613_500"),
 ("611_101..613_100", "613_301..615_300"), ("611_501..611_500", "613_701..613_700"),
 ("609_301..611_300", "611_501..613_500"), ("609_101..609_300", "611_301..611_500"),
 ("609_101..611_100", "611_301..613_300"), ("609_301..609_500", "611_501..611_700"),
 ("607_101..609_100", "609_301..611_300"), ("607_101..607_300", "609_301..609_500"),
 ("606_901..608_900", "609_101..611_100"), ("606_901..607_100", "609_101..609_300"),
 ("604_901..606_900", "607_101..609_100"),
 ("615_700+1", "617_900+1"), ("613_700+1", "615_900+1"), ("613_500+1", "615_700+1"),
 ("615_701+j", "617_901+j"), ("613_701+j", "615_901+j"), ("613_501+j", "615_701+j"), ("611_501+j", "613_701+j"),
 ("A 尾 613_500 续", "A 尾 615_700 续"),
 ("611_500+1", "613_700+1"), ("611_300+1", "613_500+1"), ("609_300+1", "611_500+1"), ("609_100+1", "611_300+1"),
 # -- bare numbers (consume G0/G+1 then create) --
 ("615901", "618101"), ("615701", "617901"), ("615700", "617900"), ("615900", "618100"),
 ("616100", "618300"), ("617700", "619900"), ("615500", "617700"),
 ("613501", "615701"), ("613700", "615900"), ("613701", "615901"), ("613900", "616100"),
 # -- seat/provenance/sha/r-numbers/stamps/paths --
 ("_r1097bmc_w271_fivekeys.json", "_r1100bmc_w272_fivekeys.json"),
 ("MSG-20261018-191x", "MSG-20261018-211x"), ("MSG-20261018-175x", "MSG-20261018-191x"),
 ("MSG-191x owner", "MSG-211x owner"), ("bmc-w272-seat", "bmc-w273-seat"), ("bmc-w271-seat", "bmc-w272-seat"),
 ("f608ff1cee", "39e1bb32f1"), ("87d2697cdc", "f608ff1cee"), ("e0a21b817d", "d914e1a3db"),
 ("7dd091eef1", "c99ee20a4"), ("a035552321", "434983cb65"), ("037445477b", "42549d6df1"),
 ("f75b18c862", "c049a57623"),
 ("a5aad2251d04d082c031b61d67dc3d5b0f39b06f", "c1c8a39c3debff40bcd4b6227f39a4209119405b"),
 ("e204ebdd512eb4a27a2e76ff5040399357b9d154", "f11abb7e39078aaa4e8671db1692cfd73d0e2934"),
 ("f8b4a755d81bfbe5", "b023511eba80a9bf"), ("== 23336", "== 23409"), ("23,336 bytes", "23,409 bytes"), ("(27,175 bytes)", "(%s bytes)" % TWIN_SIZE),
 ("r1099", "r1102"), ("r1098", "r1101"), ("r1097", "r1100"), ("r1096", "r1099"), ("r1095", "r1098"),
 ("the r1101 prep window", "the r1102 prep window"),
 ("2026-10-18 19:10:53", "2026-10-18 21:15:53"), ("2026-10-18 19:1x", "2026-10-18 21:1x"),
 ("2026-10-18 19:1", "2026-10-18 21:1"), ("@ 19:1x", "@ 21:1x"), ('"19:1x": 0', '"21:1x": 0'),
 ("18:46:31", "20:42:48"), ("2026-10-18 18:4", "2026-10-18 20:4"), ("@ 18:4x", "@ 20:4x"),
 ('"18:4x": 0', '"20:4x": 0'), ("窗 18:4x", "窗 20:4x"),
 ("18:33:39", "20:28:33"), ('"2026-10-18 18:(', '"2026-10-18 20:('), ('"18:%sx"', '"20:%sx"'), ('"18:3x": 0', '"20:2x": 0'),
 ('"17:2x": 5', '"18:4x": 5'), ('"17:0x": 2', '"18:3x": 2'), ("17:2x=5 / 17:0x=2", "18:4x=5 / 18:3x=2"),
 ('"18:4x",', '"20:4x",'), ("i2v wave-1 烧批在飞", "i2v wave-3 收官烧批在飞"),
 ("landed 18:4x", "landed 20:4x"), ("17:2x stamps", "18:4x stamps"),
 ("本窗 free RAM ~1.4GB", "本窗 free RAM " + ram_face),
 ("freeze-window ~1.4G bm-c anchor appended", "freeze-window %s bm-c anchor appended" % ram_anchor),
 ("_w271_frozen_face", "_w272_frozen_face"),
 ("w271_only", "w272_only"), ('"key1_w271_vs', '"key1_w272_vs'), ("w271_finalize", "w272_finalize"),
 ("W272p_", "W273p_"), ("W271p_", "W272p_"),
 ("行 261 注册在册", "行 262 注册在册"), ("行 260 注册在册", "行 261 注册在册"),
 ("90 行注册", "91 行注册"), ("89 行注册", "90 行注册"),
 ("bmc_rows=90", "bmc_rows=91"), ("bmc_rows=89", "bmc_rows=90"),
 ("bmc rows 90+候选", "bmc rows 91+候选"), ("bmc rows 89+候选", "bmc rows 90+候选"),
 ("live rows 90 实读", "live rows 91 实读"), ("live rows 89 实读", "live rows 90 实读"),
 ("波号 272", "波号 273"), ("波号 271", "波号 272"), ("零 272 行", "零 273 行"), ("零 271 行", "零 272 行"),
 ("--wave 272/finalize --wave 272", "--wave 273/finalize --wave 273"),
 ("--wave 271/finalize --wave 271", "--wave 272/finalize --wave 272"),
 ("池第 270 枚", "池第 271 枚"), ("池第 269 枚", "池第 270 枚"),
 ("第 262 波", "第 263 波"), ("第 261 波", "第 262 波"),
 ("第九十一枚", "第九十二枚"), ("第九十枚", "第九十一枚"), ("第 91 枚", "第 92 枚"), ("第 90 枚", "第 91 枚"),
 ("rows=269", "rows=270"), ("owner_rows=261", "owner_rows=262"), ("ordinal=262", "ordinal=263"),
 ('_l0["rows"] == 269', '_l0["rows"] == 270'), ('_l0["owner_rows"] == 261', '_l0["owner_rows"] == 262'),
 ('_l0["bmc_rows"] == 90', '_l0["bmc_rows"] == 91'), ('_l0["ordinal"] == 262', '_l0["ordinal"] == 263'),
 ("34th consecutive", "35th consecutive"), ("CLEAN-AT-BIRTH 4th gen", "CLEAN-AT-BIRTH 5th gen"),
 ("~1.4GB written", "%s written" % ram_face),
]
for old, new in NEEDLES:
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the new VMAP roll floor) --
P1 = "\x01W\x01"
for w in range(272, 257, -1):  # W272..W258 consume descending
    txt = txt.replace("W%d" % w, "\x01W%d\x01" % w if w == 272 else None) if False else txt
txt2 = txt
for w in range(272, 257, -1):
    if w == 272:
        txt2 = txt2.replace("W272", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W273")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w272", P2).replace("n1_w271", "n1_w272").replace("n1_w270", "n1_w271").replace(P2, "n1_w273")
txt = txt.replace("_w272bmc", P3).replace("_w271bmc", "_w272bmc").replace("_w270bmc", "_w271bmc").replace(P3, "_w273bmc")

# ---------------- substitute placeholders ----------------
for sid, old, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- MEASURED floors rewrite (r1077 law) + zero-floor audit ----------------
measured = {}
for k in ["W272", "W271", "W270", "W269", "W268", "W267", "W266", "W265", "W264", "W263", "W262",
          "W261", "W260", "W259", "n1_w272", "n1_w271", "_w272bmc", "_w271bmc", "18:4x", "18:3x"]:
    measured[k] = T0.count(k)
pattern = {"W272": 34, "W271": 61, "W270": 4, "W269": 4, "W268": 3, "W267": 3, "W266": 2, "W265": 2,
           "W264": 2, "W263": 1, "W262": 1, "W261": 1, "W260": 1, "W259": 1,
           "n1_w272": 4, "n1_w271": 6, "_w272bmc": 4, "_w271bmc": 1, "18:4x": 5, "18:3x": 2}
heals = []
for k, pv in pattern.items():
    mv = measured[k]
    if mv != pv:
        old_line = '"%s": %d,' % (k, pv)
        new_line = '"%s": %d,' % (k, mv)
        assert txt.count(old_line) == 1, "floor rewrite anchor missing: %s" % old_line
        txt = txt.replace(old_line, new_line)
        heals.append({"key": k, "pattern": pv, "measured": mv})
zero_expected = ["_w273bmc", "n1_w273", "W274p_", "第 92 枚", "第 263 波", "第九十二枚", "池第 271 枚",
                 "波号 273", "零 273 行", "第二十三次连续 A-hop", "第二十三次连续 above-own-A",
                 "连续二十二波", "共二百七十一面", "1,022,735", "615_901..617_900",
                 "617_901..618_100", "617_901..619_900", "618_101..618_300", "20:2x", "20:4x", "21:1x",
                 "c049a57623", "c99ee20a4", "434983cb65", "42549d6df1", "d914e1a3db", "39e1bb32f1"]
zero_bad = [k for k in zero_expected if T0.count(k) != 0]

# ---------------- audit ----------------
MUST_NEW = ["r1102 bm-c: W273 prereg derive", "PERPETUAL_N1_W273_PREREG.md", "615_901..617_900",
            "617_901..618_100", "598,520 投影", "MSG-20261018-211x-bmc-w273-seat", "39e1bb32f1",
            "c049a57623", "第二十二次连续 A-hop", "第二十三次连续 above-own-A", "c1c8a39c3debff40bcd4b6227f39a4209119405b",
            "f11abb7e39078aaa4e8671db1692cfd73d0e2934", "20:28:33", "20:42:48", "bm-c r1100 W272 §7 范式",
            "_r1100bmc_w272_fivekeys.json", "−0.09277998", "0.24509581", "−0.09706318", "（**0.3138** 实测锚）",
            "1,022,735", "596,320", "0.000317", "第 92 枚", "第 263 波", "池第 271 枚", "W272 冻结窗"]
BAN = ["f75b18c862", "第 261 波", "波号 271", "第 90 枚", "bmc_rows=89",
       "TWENTY-FIRST consecutive", "18:33:39", "18:46:31", "−0.09272692", "0.24507005",
       "r1095", "17:2x=5", "bmc-w271-seat", "PERPETUAL_N1_W271_PREREG.md"]
# r1095/r1096 ban is contextual: they must not survive as live faces; whitelist comment archaeology is none in canon.
for s in MUST_NEW:
    assert s in txt, "AUDIT MUST missing: %r" % s
for s in BAN:
    assert s not in txt, "AUDIT MUST_NOT present: %r (count=%d)" % (s, txt.count(s))

OUT = os.path.join(REPO, "results", "_w273bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"measured_t0": measured, "floor_heals": heals, "zero_floor_violations": zero_bad,
           "ram_face": ram_face, "ram_anchor_gb": RAM, "twin_size": TWIN_SIZE, "diff4": DIFF4,
           "spans": len(SPANS), "needles": len(NEEDLES) + 15}
io.open(os.path.join(REPO, "results", "_w273bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("measured floors: %r" % measured)
print("floor heals: %r | zero-floor violations: %r" % (heals, zero_bad))
print("ram face %s | twin size %s B | diff4 %s" % (ram_face, TWIN_SIZE, DIFF4))
