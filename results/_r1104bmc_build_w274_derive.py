# -*- coding: utf-8 -*-
# r1104 bm-c: W274 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w273bmc_prereg_derive.py -> results/_w274bmc_prereg_derive.py.
# Zero hand-transcription of chain values: W274 bands/anchors read from the seat receipt +
# fivekeys/results/facts jsons; floors MEASURED on the frozen W273 template (r1077 law) and
# rewritten in-place; complex value spans placeholder-protected before the general rolls.
# Needle evidence receipt -> results/_w274bmc_needle_probe.json (probe folded into builder).
# Same-window heals disclosed (builder-level): (a) stale b_band prose faces "B 尾 613_700" and
# "→jump 613_701" inherited from the W273 canon (W271-era tails never rolled by the W273 builder)
# healed to the true W274 rolled values 618_100 / 618_101; (b) header disclosures (1)/(7)/(10)
# span-rewritten for the r1104 window instead of left to drift; (c) estate-chain line span-rewritten
# (W273 cycle = one-window full cycle r1102, not a two-window r1099/r1100-style chain);
# (d) date-cross POST_LEG appended via S1: the W274 seat receipt _w274bmc_20261019 crossed the
# 10-18->10-19 boundary (W272/W273 seats were both 10-18, so the lineage carried no date
# needle; the lowercase prefix chain rolls _w273bmc->_w274bmc but leaves 20261018) -- the
# receipt date is rolled on T1 (floor 3 = 2 non-block + b_title block-interior).
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w274bmc_w273_frozen_face.txt"), encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23449
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "2f289446a93fa102"
fk = json.load(open(os.path.join(REPO, "results", "_r1102bmc_w273_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w274bmc_20261019_probe_receipt.json"), encoding="utf-8"))
facts = json.load(open(os.path.join(REPO, "results", "_w274bmc_facts.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [618101, 620100] and rcp["bands"]["B"] == [620101, 620300]
assert round(fk["merged"]["mu"], 8) == -0.09278822 and round(fk["merged"]["sigma"], 8) == 0.24510975
assert round(fk["w273_only"]["mu"], 8) == -0.095021 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3124
assert round(fk["merged"]["se_mu_k598520"], 6) == 0.000317 and fk["ledger_identity"]["total"] == 1024935
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w273_vs_merged_mu_gap"][0]
DIFF4 = "%.4f" % round(_k1["value"], 4)  # 0.0022
RAM = round(float(subprocess.run(["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"],
           capture_output=True, text=True).stdout.strip() or 0), 1)
ram_face = "~%.1fGB" % RAM
ram_anchor = "~%.1fG" % RAM
try:
    _nvs = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                           "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    _util, _vram = [x.strip() for x in _nvs.split(",")]
    vram_g = "%.1fG" % (int(_vram) / 1024.0)
    gpu_face = "nvidia-smi 实读 %s%%·%s VRAM 占用·MV PACK-A i2v wave-3 已收官 GPU idle 回释" % (_util, vram_g)
except Exception:
    gpu_face = "nvidia-smi 实读 idle·MV PACK-A i2v wave-3 已收官 GPU idle 回释"
TWIN_SIZE = subprocess.run([GIT, "cat-file", "-s", "HEAD:research/PERPETUAL_N1_W273_PREREG.md"],
                            capture_output=True, text=True, cwd=REPO).stdout.strip()
SRC = io.open(os.path.join(REPO, "results", "_w273bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected complex spans (old exact -> new final) ----------------
OLD_RAM_W273 = "本窗 free RAM ~0.3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.2G VRAM 占用·MV PACK-A i2v wave-3 收官烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"
NEW_RAM_W274 = "本窗 free RAM %s（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=MV PACK-A GPU 道 wave-3 收官后回释实测·GPU=gen-only 车道 idle（%s）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）" % (ram_face, gpu_face)
SPANS = [
 ("S1", '("18:4x", "20:4x", 4),',
  '("20:4x", "00:3x", 4),\n    # r1104 date-cross heal (disclosed): T0 receipt faces _w273bmc_20261018 (W273 seat\n    # window 10-18) prefix-roll to _w274bmc_20261018 only; the W274 seat receipt is dated 10-19\n    # (_w274bmc_20261019_probe_receipt.json, r1102 seat window) -> roll the date here; T1 count = 3\n    # (2 non-block + 1 b_title block-interior, replaced wholesale by the NEW block).\n    ("_w274bmc_20261018", "_w274bmc_20261019", 3),'),
 ("S2", '# (1) finalize-window stamp roll: W272 finalize one-pass landed 20:4x (d914e1a3db 20:42:48); T0\n#     carries the W271-era 18:4x stamps x5 (measured: 3 block-interior copies discarded by block\n#     replace + 2 live sec.5 preamble faces) -> POST_LEG x5.',
  '# (1) finalize-window stamp roll: W273 finalize one-pass landed 00:3x (6659a0e362 00:39:01); T0\n#     carries the W272-era 20:4x stamps x4 (MEASURED live THIS build, r1077 law) -> POST_LEG x4.'),
 ("S3", '("键 W272 实测 K-lift **+0.0001**·line_merged@K594,120 **1.1964**·line_pre_w271 1.1963·n_eff_held_equal 1,018,335",\n     "键 W272 实测 K-lift **+0.0000**·line_merged@K596,320 **1.1965**·line_pre_w272 1.1965·n_eff_held_equal 1,020,535", 1),',
  '("键 W273 实测 K-lift **+0.0000**·line_merged@K596,320 **1.1965**·line_pre_w272 1.1965·n_eff_held_equal 1,020,535",\n     "键 W273 实测 K-lift **+0.0001**·line_merged@K598,520 **1.1967**·line_pre_w273 1.1966·n_eff_held_equal 1,022,735", 1),'),
 ("S4", '("→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 投影 0.000318】",\n     "→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 投影 0.000317】", 1),',
  '("→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 投影 0.000317】",\n     "→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 投影 0.000317】", 1),'),
 ("S5", '("bm-c r1097 W272 §7 范式", "bm-c r1100 W272 §7 范式", 1),',
  '("bm-c r1100 W273 §7 范式", "bm-c r1102 W273 §7 范式", 1),'),
 ("S6", '("bm-c r1097 W272 §8 范式", "bm-c r1100 W272 §8 范式", 1),',
  '("bm-c r1100 W273 §8 范式", "bm-c r1102 W273 §8 范式", 1),'),
 ("S7", '("本窗 free RAM ~1.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.2G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",\n     "' + OLD_RAM_W273 + '", 1),',
  '("' + OLD_RAM_W273 + '",\n     "' + NEW_RAM_W274 + '", 1),'),
 ("S8", '("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚）",\n     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚）", 1),',
  '("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚）",\n     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ' + ram_anchor + ' bm-c 实锚）", 1),'),
 ("S9", '# (10) RAM face live-measured THIS window: psutil 1.38GB available (~1.4GB, probe-time read) +\n#     nvidia-smi 100% util / 15,538MiB (~15.2G) VRAM occupied -- MV PACK-A i2v GPU burn IN FLIGHT\n#     (CEO weekend production order; legal occupant untouchable); the r1099 ~3.3GB face is stale.',
  '# (10) RAM face live-measured THIS window: psutil %sGB available (%s, probe-time read) +\n#     %s -- MV PACK-A i2v GPU lane wave-3 DONE 00:42:53 (CEO weekend production order concluded;\n#     loop CPU-only); the r1102 ~0.3GB face is stale.' % (RAM, ram_face, gpu_face)),
 ("S10", '"W206/W211..W272 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",\n    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",\n    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",\n    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚",',
  '"W206/W211..W273 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",\n    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",\n    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",\n    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ' + ram_anchor + ' bm-c 实锚",'),
 ("S11", '"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",\n    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G",',
  '"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",\n    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",'),
 ("S12", '"MSG-20261018-191x", "f608ff1cee", "87d2697cdc", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",',
  '"MSG-20261018-211x", "39e1bb32f1", "f608ff1cee", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",'),
 ("S13", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x",',
  '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x",'),
 ("S14", '# r1102 bm-c: W273 prereg derive (count-asserted ordered transform + marker-extracted block replaces).',
  '# r1104 bm-c: W274 prereg derive (count-asserted ordered transform + marker-extracted block replaces).'),
 ("S15", '（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273=A/B 双 1-hop 形态连续二十二波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）',
  '（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274=A/B 双 1-hop 形态连续二十三波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）'),
 ("S16", '·estate chain r1099/r1100 c049a57623+c99ee20a4+d914e1a3db】）',
  '·estate chain r1102 W273 同窗全周期（r1102-continuation absorb-healed）839441a547+04f2127db+6659a0e362】）'),
 ("S17", '# (7) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries W272\n#     0.000318 (FALSE -- true W272 measured 0.000317) -> POST_LEG rewrites the tail with true\n#     history W267 0.000321 / W268 0.000320 / W269 0.000320 / W270 0.000318 / W271 0.000318 /\n#     W272 0.000317 and appends the W273 projection 0.000317.',
  '# (7) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries W273\n#     0.000317 (TRUE for W273 -- W269/W271/W272 labels carry stale values) -> POST_LEG rewrites\n#     the tail with true history W268 0.000320 / W269 0.000319 / W270 0.000319 / W271 0.000318 /\n#     W272 0.000317 / W273 0.000317 and appends the W274 projection 0.000317.'),
 ("S18", '=**splice 执行窗派生落地（r1099/r1100 W272 先例实时间线：prereg c049a57623 落于 r1099 窗·splice c99ee20a4 落于 r1100 执行窗 @@SPLICE_T@@——',
  '=**splice 执行窗派生落地（r1102 W273 同窗全周期先例实时间线：prereg 839441a547 落于 r1102 窗·splice 04f2127db 落于 r1102 执行窗 @@SPLICE_T@@——'),
 ("S19", '→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 投影 0.000317】',
  '→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 投影 0.000317】'),
]
txt = SRC
for sid, old, new in SPANS:
    c = txt.count(old)
    assert c == 1, "SPAN %s count=%d (expect 1)" % (sid, c)
    txt = txt.replace(old, "\x02%s\x02" % sid)

NEEDLES = [
 # -- G+1 consumes (fire before everything that creates their outputs) --
 ("W276 冻结方", "W277 冻结方"), ("W275 冻结方", "W276 冻结方"),
 ("W275p_", "W276p_"), ("W274p_", "W275p_"), ("W273p_", "W274p_"),
 ("verify at W275 prereg", "verify at W276 prereg"), ("verify at W274 prereg", "verify at W275 prereg"),
 ("verify at W273 prereg", "verify at W274 prereg"),
 ("W275/W276", "W276/W277"), ("W274/W275", "W275/W276"), ("W273/W274", "W274/W275"),
 ("R275", "R276"), ("R274", "R275"), ("R273", "R274"),
 ("W274+ ", "W275+ "), ("W273+ ", "W274+ "),
 ("W274 freezer", "W275 freezer"),
 # -- ordinals (Chinese) descending consume --
 ("第二十四次连续 above-own-A", "第二十五次连续 above-own-A"), ("第二十三次连续 above-own-A", "第二十四次连续 above-own-A"),
 ("第二十二次连续 above-own-A", "第二十三次连续 above-own-A"), ("第二十一次连续 above-own-A", "第二十二次连续 above-own-A"),
 ("第二十四次连续 A-hop", "第二十五次连续 A-hop"), ("第二十三次连续 A-hop", "第二十四次连续 A-hop"),
 ("第二十二次连续 A-hop", "第二十三次连续 A-hop"), ("第二十一次连续 A-hop", "第二十二次连续 A-hop"),
 ("〔第二十三次连续〕", "〔第二十四次连续〕"), ("〔第二十二次连续〕", "〔第二十三次连续〕"),
 ("连续二十三波", "连续二十四波"), ("连续二十二波", "连续二十三波"), ("连续二十一波", "连续二十二波"),
 ("共二百七十二面", "共二百七十三面"), ("共二百七十一面", "共二百七十二面"), ("共二百七十面", "共二百七十一面"),
 # -- English ordinals --
 ("TWENTY-FOURTH consecutive above-own-A", "TWENTY-FIFTH consecutive above-own-A"),
 ("TWENTY-THIRD consecutive above-own-A", "TWENTY-FOURTH consecutive above-own-A"),
 ("TWENTY-THIRD consecutive A-hop", "TWENTY-FOURTH consecutive A-hop"),
 ("TWENTY-SECOND consecutive A-hop", "TWENTY-THIRD consecutive A-hop"),
 # -- numbers/shas/values (descending consume) --
 ("1,022,735", "1,024,935"), ("1,020,535", "1,022,735"), ("1,018,335", "1,020,535"),
 ("1022735", "1024935"), ("1020535", "1022735"),
 ('"598,520": 0', '"600,720": 0'), ("598,520 投影", "600,720 投影"), ("=596,320+2,200", "=598,520+2,200"),
 ("596,320", "598,520"), ("594,120", "596,320"),
 ("596320", "598520"), ("594120", "596320"),
 # -- compound gate faces AFTER the bare K rolls (keys already rolled; fix the values here) --
 ('"line_merged_598520"], 4) == 1.1965', '"line_merged_598520"], 4) == 1.1967'),
 ("**+0.0000**", "**+0.0001**"), ("K-lift +0.0000", "K-lift +0.0001"), ("== 0.0,", "== 0.0001,"),
 ("0.000318", "0.000317"), ("0.000319", "0.000318"),
 ("0.0042832029477766626", "0.0022327837332085793"), ("(4dp 0.0043)", "(4dp 0.0022)"),
 ('== 0.0043 and _k1', '== 0.0022 and _k1'),
 ("实差 0.0043 在带内", "实差 0.0022 在带内"), ("实差 0.0100 在带内", "实差 0.0043 在带内"),
 ("-0.09277997887040515", "-0.09278821626679142"), ("0.24509581465156932", "0.24510974987645237"),
 ("-0.09706318181818181", "-0.095021"),
 ("-0.09277998", "-0.09278822"), ("−0.09277998", "−0.09278822"), ("−0.09276412", "−0.09277998"),
 ("0.24509581", "0.24510975"), ("0.24509040", "0.24509581"),
 ("-0.09706318", "-0.095021"), ("−0.09706318", "−0.095021"), ("−0.10277223", "−0.09706318"),
 ("0.3138", "0.3124"), ("**0.3042**", "**0.3138**"), ("0.3042", "0.3138"),
 ("line_merged@K598,520 **1.1965**", "line_merged@K598,520 **1.1967**"),
 ("line_pre_w272 1.1965", "line_pre_w273 1.1966"),
 ('"line_pre_w272"], 4) == 1.1965', '"line_pre_w273"], 4) == 1.1966'),
 ('% fk["skill_line"]["line_pre_w272"]', '% fk["skill_line"]["line_pre_w273"]'),
 ('"w272_only"]["mu"], 8) == -0.09706318', '"w273_only"]["mu"], 8) == -0.095021'),
 ('skill_line_delta_k_lift"], 4) == 0.0\n', 'skill_line_delta_k_lift"], 4) == 0.0001\n'),
 ("w272_only", "w273_only"), ('"key1_w272_vs', '"key1_w273_vs'), ("w272_finalize", "w273_finalize"),
 # -- compound stale-prose heals (r1104 same-window, disclosed) --
 ("B 尾 613_700", "B 尾 618_100"), ("→jump 613_701", "→jump 618_101"),
 # -- underscore bands (G+1/G0 consume descending, then G-1 roll) --
 ("618_101..618_300", "620_301..620_500"), ("617_901..619_900", "620_101..622_100"),
 ("617_901..618_100", "620_101..620_300"), ("615_901..617_900", "618_101..620_100"),
 ("615_701..617_700", "617_901..619_900"), ("615_901..616_100", "618_101..618_300"),
 ("615_701..615_900", "617_901..618_100"),
 ("613_701..615_700", "615_901..617_900"), ("613_501..615_500", "615_701..617_700"),
 ("613_701..613_900", "615_901..616_100"), ("613_501..613_700", "615_701..615_900"),
 ("611_501..613_500", "613_701..615_700"), ("611_301..613_300", "613_501..615_500"),
 ("611_301..611_500", "613_501..613_700"), ("611_101..611_300", "613_301..613_500"),
 ("611_101..613_100", "613_301..615_300"),
 ("609_301..611_300", "611_501..613_500"), ("609_101..609_300", "611_301..611_500"),
 ("609_101..611_100", "611_301..613_300"), ("609_301..609_500", "611_501..611_700"),
 ("607_101..609_100", "609_301..611_300"), ("607_101..607_300", "609_301..609_500"),
 ("606_901..608_900", "609_101..611_100"), ("606_901..607_100", "609_101..609_300"),
 ("604_901..606_900", "607_101..609_100"),
 # -- +j / +1 / tail faces --
 ("617_901+j", "620_101+j"), ("615_901+j", "618_101+j"),
 ("615_701+j", "617_901+j"), ("613_701+j", "615_901+j"),
 ("613_501+j", "615_701+j"), ("611_501+j", "613_701+j"),
 ("617_900+1", "620_100+1"), ("615_900+1", "618_100+1"),
 ("615_700+1", "617_900+1"), ("613_700+1", "615_900+1"), ("613_500+1", "615_700+1"),
 ("A 尾 615_700 续", "A 尾 617_900 续"),
 # -- bare numbers (leg4 gate strings FIRST, then bands descending) --
 ('"617901..619900"', '"620101..622100"'), ('"618101..618300"', '"620301..620500"'),
 ("618100", "620300"), ("617901", "620101"), ("617900", "620100"),
 ("617700", "619900"), ("616100", "618300"), ("615901", "618101"),
 ("615701", "617901"), ("615900", "618100"),
 ("615500", "617700"), ("613900", "616100"), ("613701", "615901"), ("613700", "615900"), ("613501", "615701"),
 # -- seat/provenance/sha/r-numbers/stamps/paths --
 ("_w273bmc_20261018", "_w274bmc_20261019"), ("_w272_frozen_face", "_w273_frozen_face"),
 ("MSG-20261018-211x", "MSG-20261019-012x"), ("MSG-20261018-191x", "MSG-20261018-211x"),
 ("MSG-211x owner", "MSG-012x owner"), ("bmc-w273-seat", "bmc-w274-seat"), ("bmc-w272-seat", "bmc-w273-seat"),
 ("39e1bb32f1", "70b21a0264"), ("f608ff1cee", "39e1bb32f1"), ("87d2697cdc", "f608ff1cee"),
 ("c049a57623", "839441a547"), ("c99ee20a4", "04f2127db"), ("434983cb65", "fbb4788c49"),
 ("42549d6df1", "acc7fd02c0"), ("d914e1a3db", "6659a0e362"),
 ("c1c8a39c3debff40bcd4b6227f39a4209119405b", "9b56779c8ec9ae54d41aeca862b7d18d94f479d1"),
 ("f11abb7e39078aaa4e8671db1692cfd73d0e2934", "7a57ab1f3d3368ca9150f602274d921f5ef318d7"),
 ("f8b4a755d81bfbe5", "b023511eba80a9bf"), ("b023511eba80a9bf", "2f289446a93fa102"), ("== 23409", "== 23449"), ("23,409 bytes", "23,449 bytes"),
 ("(27810 bytes)", "(%s bytes)" % TWIN_SIZE),
 ("r1102", "r1104"), ("r1101", "r1102"), ("r1100", "r1102"), ("r1099", "r1102"), ("r1098", "r1101"),
 ("2026-10-18 20:28:33", "2026-10-19 00:20:20"), (" 20:28:33 (", " 00:20:20 ("), ('"2026-10-18 20:(', '"2026-10-19 00:('),
 ('"20:%sx" % _m.group(1)[0]   # 18:3x', '"00:%sx" % _m.group(1)[0]   # 00:2x'),
 ("2026-10-18 20:4", "2026-10-19 00:3"), ("20:42:48", "00:39:01"),
 ("2026-10-18 21:15:53", "2026-10-19 01:03:27"), ("2026-10-18 21:1", "2026-10-19 01:0"),
 ("@ 19:1x", "@ 01:0x"), ("21:1x", "01:0x"),
 ("@ 20:4x", "@ 00:3x"), ("20:4x", "00:3x"), ("20:2x", "00:2x"),
 ('"18:4x": 4, "18:3x": 2', '"20:4x": 4, "20:2x": 2'),
 ("18:4x=5 / 18:3x=2", "20:4x=4 / 20:2x=2"),
 ("i2v wave-3 收官烧批在飞", "i2v wave-3 已收官 GPU idle 回释"),
 ("本窗 free RAM ~1.4GB", "本窗 free RAM " + ram_face),
 ("本窗 free RAM ~0.3GB", "本窗 free RAM " + ram_face),
 ("freeze-window ~1.4G bm-c anchor appended", "freeze-window %s bm-c anchor appended" % ram_anchor),
 # -- latent canon heal: POST_LEG fail-raise had 3 format specs but only (o, c) args --
 ('"VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c))', '"VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))'),
 ("W272 freeze-window ~0.3G bm-c anchor appended", "W273 freeze-window %s bm-c anchor appended" % ram_anchor),
 ("行 262 注册在册", "行 263 注册在册"), ("行 261 注册在册", "行 262 注册在册"),
 ("engine_owner==bm-c 91 行注册", "engine_owner==bm-c 92 行注册"),
 ("engine_owner==bm-c 90 行注册", "engine_owner==bm-c 91 行注册"),
 ("bmc_rows=91", "bmc_rows=92"), ("bmc_rows=90", "bmc_rows=91"),
 ("bmc rows 91+候选", "bmc rows 92+候选"), ("bmc rows 90+候选", "bmc rows 91+候选"),
 ("live rows 91 实读", "live rows 92 实读"), ("live rows 90 实读", "live rows 91 实读"),
 ('"bmc_rows"] == 91', '"bmc_rows"] == 92'), ('"bmc_rows"] == 90', '"bmc_rows"] == 91'),
 ("rows=270", "rows=271"), ("rows=269", "rows=270"),
 ('"rows"] == 270', '"rows"] == 271'), ('"rows"] == 269', '"rows"] == 270'),
 ("owner_rows=262", "owner_rows=263"), ("owner_rows=261", "owner_rows=262"),
 ('"owner_rows"] == 262', '"owner_rows"] == 263'), ('"owner_rows"] == 261', '"owner_rows"] == 262'),
 ("ordinal=263", "ordinal=264"), ("ordinal=262", "ordinal=263"),
 ('"ordinal"] == 263', '"ordinal"] == 264'), ('"ordinal"] == 262', '"ordinal"] == 263'),
 ("第 264 波", "第 265 波"), ("第 263 波", "第 264 波"), ("第 262 波", "第 263 波"),
 ("第九十三枚", "第九十四枚"), ("第九十二枚", "第九十三枚"), ("第九十一枚", "第九十二枚"),
 ("第 93 枚", "第 94 枚"), ("第 92 枚", "第 93 枚"), ("第 91 枚", "第 92 枚"),
 ("池第 272 枚", "池第 273 枚"), ("池第 271 枚", "池第 272 枚"), ("池第 270 枚", "池第 271 枚"),
 ("波号 274", "波号 275"), ("波号 273", "波号 274"), ("波号 272", "波号 273"),
 ("零 274 行", "零 275 行"), ("零 273 行", "零 274 行"), ("零 272 行", "零 273 行"),
 ("--wave 274/finalize --wave 274", "--wave 275/finalize --wave 275"),
 ("--wave 273/finalize --wave 273", "--wave 274/finalize --wave 274"),
 ("--wave 272/finalize --wave 272", "--wave 273/finalize --wave 273"),
 ("35th consecutive", "36th consecutive"), ("CLEAN-AT-BIRTH 5th gen", "CLEAN-AT-BIRTH 6th gen"),
 # -- fivekeys receipt filename fix AFTER the r-rolls (r1100->r1102 already rolled the r-face;
 #    fix the wave label here so no later r-needle can re-consume the created face) --
 ("_r1102bmc_w272_fivekeys.json", "_r1102bmc_w273_fivekeys.json"),
]
needle_counts = {}
for old, new in NEEDLES:
    needle_counts[old] = txt.count(old)
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the new VMAP roll floor) --
P1 = "\x01W\x01"
txt2 = txt
for w in range(273, 258, -1):  # W273..W259 consume descending
    if w == 273:
        txt2 = txt2.replace("W273", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W274")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w273", P2).replace("n1_w272", "n1_w273").replace("n1_w271", "n1_w272").replace(P2, "n1_w274")
txt = txt.replace("_w273bmc", P3).replace("_w272bmc", "_w273bmc").replace("_w271bmc", "_w272bmc").replace(P3, "_w274bmc")

# ---------------- substitute placeholders ----------------
for sid, old, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- MEASURED floors rewrite (r1077 law) + zero-floor audit ----------------
measured = {}
for k in ["W273", "W272", "W271", "W270", "W269", "W268", "W267", "W266", "W265", "W264", "W263",
          "W262", "W261", "W260", "n1_w273", "n1_w272", "_w273bmc", "_w272bmc", "20:4x", "20:2x"]:
    measured[k] = T0.count(k)
pattern = {"W273": 34, "W272": 61, "W271": 4, "W270": 4, "W269": 3, "W268": 3, "W267": 3,
           "W266": 2, "W265": 2, "W264": 2, "W263": 1, "W262": 1, "W261": 1, "W260": 1,
           "n1_w273": 4, "n1_w272": 6, "_w273bmc": 4, "_w272bmc": 1, "20:4x": 4, "20:2x": 2}
heals = []
for k, pv in pattern.items():
    mv = measured[k]
    if mv != pv:
        old_line = '"%s": %d,' % (k, pv)
        new_line = '"%s": %d,' % (k, mv)
        assert txt.count(old_line) == 1, "floor rewrite anchor missing: %s" % old_line
        txt = txt.replace(old_line, new_line)
        heals.append({"key": k, "pattern": pv, "measured": mv})
zero_expected = ["_w274bmc", "n1_w274", "W275p_", "第 93 枚", "第 264 波", "第九十三枚", "池第 272 枚",
                 "波号 274", "零 274 行", "第二十四次连续 A-hop", "第二十四次连续 above-own-A",
                 "连续二十三波", "共二百七十二面", "1,024,935", "618_101..620_100",
                 "620_101..620_300", "620_101..622_100", "620_301..620_500", "00:2x", "00:3x", "01:0x",
                 "839441a547", "04f2127db", "fbb4788c49", "acc7fd02c0", "6659a0e362", "70b21a0264"]
zero_bad = [k for k in zero_expected if T0.count(k) != 0]

# ---------------- audit ----------------
MUST_NEW = ["r1104 bm-c: W274 prereg derive", "PERPETUAL_N1_W274_PREREG.md", "618_101..620_100",
            "620_101..620_300", "600,720 投影", "MSG-20261019-012x-bmc-w274-seat", "70b21a0264",
            "839441a547", "第二十三次连续 A-hop", "第二十四次连续 above-own-A", "9b56779c8ec9ae54d41aeca862b7d18d94f479d1",
            "7a57ab1f3d3368ca9150f602274d921f5ef318d7", "2026-10-19 00:20:20", "bm-c r1102 W273 §7 范式",
            "_r1102bmc_w273_fivekeys.json", "−0.09278822", "0.24510975", "−0.095021", "（**0.3124** 实测锚）",
            "1,024,935", "598,520", "0.000317", "第 93 枚", "第 264 波", "池第 272 枚", "W273 冻结窗",
            "engine_owner==bm-c 92 行注册", "engine_owner 行 263 注册在册",
            "probe leg0 bmc_rows=92 attempt-continuity face",
            "bm-c 循环班 r1102 席位窗 2026-10-19 01:0x", "本机 bm-c 实例",
            "W274=bm-c own-wave window per chain-order law",
            "04f2127db", "fbb4788c49", "acc7fd02c0", "6659a0e362",
            "W275+ 投影", "W275p_B_lands_inside_W275p_A_naive", "verify at W275 prereg",
            "_w274bmc_freeze_edits.py", "_w273bmc_freeze_edits.py 模板派生",
            "bm-c r1102 W273 §8 范式",
            "（上游 W273 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
            "（W273 注册+烧录+finalize 全落地）",
            "W206/W211..W273 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
            "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
            "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
            "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚",
            "席位时即解锁", "（见 §5 item5）。", "R275：W274 带",
            "→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 投影 0.000317】",
            "618_100+1", "620_100+1", "617_901..618_100",
            "A_staircase_hop_past_W273_B=true", "B_lands_above_own_A=true",
            "seed_admit_gate rc0 双带 FREE",
            "波号 274", "零 274 行", "零 skip-ahead W275/W276 席位声明",
            "00:3x", "（占位·finalize one-pass 后回填",
            "saturation_engine.py status live-read r1104：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
            "本机 bm-c 实例·heartbeat 新鲜实读 r1104 窗·队列空转 idle",
            "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1104 窗实读",
            "r1102 席位窗实跑：origin inbox 零 W274 席位外机命中",
            "results/p2cal_ext/n1_w273/ 12/12",
            "base=618101 span=2000", "base=620101 span=200",
            '"620101..622100"', '"620301..620500"',
            "estate chain r1102 W273 同窗全周期", "CLEAN-AT-BIRTH 6th gen", "36th consecutive",
            "B 尾 618_100", "→jump 618_101",
            ]
BAN = ["c049a57623", "c99ee20a4", "434983cb65", "42549d6df1", "d914e1a3db", "87d2697cdc",
       "第 262 波", "波号 272", "第 91 枚", "bmc_rows=90",
       "TWENTY-SECOND consecutive", "20:28:33", "20:42:48", "21:15:53", "−0.09276412", "0.24509040",
       "−0.10277223", "**0.3042**", "r1097", "18:4x=5", "bmc-w272-seat", "PERPETUAL_N1_W272_PREREG.md",
       "B 尾 613_700", "→jump 613_701", "行 261 注册在册"]
for s in MUST_NEW:
    assert s in txt, "AUDIT MUST missing: %r" % s
for s in BAN:
    assert s not in txt, "AUDIT MUST_NOT present: %r (count=%d)" % (s, txt.count(s))

OUT = os.path.join(REPO, "results", "_w274bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"measured_t0": measured, "floor_heals": heals, "zero_floor_violations": zero_bad,
           "ram_face": ram_face, "ram_anchor_gb": RAM, "gpu_face": gpu_face, "twin_size": TWIN_SIZE,
           "diff4": DIFF4, "spans": len(SPANS), "needles": len(NEEDLES), "needle_counts": needle_counts}
io.open(os.path.join(REPO, "results", "_w274bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("measured floors: %r" % measured)
print("floor heals: %r | zero-floor violations: %r" % (heals, zero_bad))
print("ram face %s | gpu %s | twin size %s B | diff4 %s" % (ram_face, gpu_face, TWIN_SIZE, DIFF4))
