# -*- coding: utf-8 -*-
"""r578 bm-b W91 freeze five-face edits (r560-law generator).

Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W91 bullet  -> research/PERPETUAL_FACES.md, after the W89 bullet
  2. pf N1_BANDS[91]   -> scripts/perpetual_faces.py, after the [89] entry
  3. n1 WAVE_CONFIGS[91] -> scripts/perpetual_faces_n1.py, after the 89 entry
  4. n1 selftest W91 materializer leg -> after the W89 leg
  5. n1 selftest PASS-print W91 fragment -> after the W89 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "research", "PERPETUAL_FACES.md")
PF = os.path.join(ROOT, "scripts", "perpetual_faces.py")
N1 = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")

MARK = "PERPETUAL-N1-W91"


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, b):
    with open(p, "wb") as f:
        f.write(b)


def insert_after(data, needle, block, tag):
    """Insert block (bytes) right after the line containing needle.
    Aborts if needle absent or not pure insertion (r560 FIX-A law)."""
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    assert j > i, f"{tag}: anchor line has no newline"
    # r560 post-anchor guard: the line after the anchor must NOT be another
    # machine's registered row that would turn insertion into replacement
    nxt = data[j:j + 40]
    assert b"90:" not in nxt and b"| 90" not in nxt, \
        f"{tag}: post-anchor line looks like a W90 row ({nxt!r})"
    out = data[:j] + block + data[j:]
    return out


def insert_after_entry(data, needle, block, tag):
    """Insert block after the 2-line dict ENTRY starting at the needle line
    (needle line + its 'engine_owner' closing line). Abort on any mismatch."""
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    # the entry's closing line must be the engine_owner line
    k = data.find(b"\n", j) + 1
    mid = data[j:k]
    assert b"engine_owner" in mid, \
        f"{tag}: line after needle is not an entry close ({mid[:60]!r})"
    nxt = data[k:k + 40]
    assert b"90:" not in nxt and b'"engine_owner": "bm-a"' not in nxt, \
        f"{tag}: post-anchor line looks like a W90 row ({nxt!r})"
    out = data[:k] + block + data[k:]
    return out


# --- 1. canon bullet -----------------------------------------------------------
CANON_BLOCK = (
    "\n"
    "- N1 波91（r578 bm-b 冻·prereg 时展行）：**第八十枚引擎波·bm-b 第三十枚自有波〔机面 derive：engine_owner 行 79+本候选／engine_owner==bm-b 行 29+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W89 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W89 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 91=注册表 W89 行后首个自由号·跳过 bm-a 已公示 W90 席**（r511 表尾锁例冻结前 fetch 实核表尾时 W91 号位净空·pf 行+prereg 路径双查+**leg0b 全 inbox+processed/ 扫描 W91 席位零命中机验**；**W89=表尾行 bm-b r578 estate adoption 五面冻结落账 27a8d9712·12/12 烧毕·finalize 未落账**；**W90=bm-a 席位公示〔MSG-20261002-1415-bma〕未注册冻结在飞**；**席位公示=MSG-20261002-1425-bmb**〔published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律〕）·本窗实况=**W87 bm-a finalize 已落账（净链头 555,948·K=189,320）+三在飞上游席（W88 bm-c 已注册 finalize 未落账+W89 本机已注册 12/12 烧毕 finalize 未落账+W90 bm-a 席位公示未注册）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律）**·**带位（r535 机闸 derive 律·活注册表机证·三态收敛门·ADMIT 回执=results/_r578bmb_w91_band_gate.py rc0·mode A90 表尾=W89）**：**A-ext seed=225_004..227_003**（**A 面 skip-past-published 链**==W89 行 A 尾→W90 公示带 223_004..225_003→首净窗·步长 2_000·CLEAN 零拒绝点〔r518-① 先例族〕）；**B-ext exit seed=56_501..56_700**（**B 侧中位命中钉死链**：算术位 56_201..56_400==W90 公示带→skip→56_401..56_600 于带内中位〔位置 99/199 非边缘端点〕撞 **SEED_REGISTRY p4_batch3_dca=56_500**→**D-20261002-05 集团钉死=越 hit 起窗** 56_501..56_700 CLEAN〔窗步链读法 56_601..56_800=钉死行所禁读法·W68-B 中位先例族正锚·pf selftest 第 9 腿 pin leg 正反断言〕）·【机证净空——leg0 八十七行注册表形（87 注册行·表尾=W89 bm-b r578）+leg0b bm-a W90 席位 MSG 在场机验+W91 席位零命中+leg1 双侧 skip-past-published/钉死链 CLEAN+leg2 A/B 首净窗==候选恒等+leg3 origin 号位净空机验（pf 行+WAVE_CONFIGS+prereg 路径三查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W92+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 227_004..229_003 **CLEAN**；B 56_701..56_900 **CLEAN**（双侧算术预期零拒绝点）。R250：W91 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W91 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W91_PREREG.md（冻结件）·本波 §5 锚=W87 finalize 实测值（锚滚动律·单波跨锚自 W76 滚动至 W87）·finalize 链序前置=起草窗三在飞上游席（FAIL-CLOSED r307 两态律跑时复核）。\n"
).encode("utf-8")

data = rd(CANON)
if "波91（r578 bm-b 冻".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data = insert_after(data, "N1 波89（r577 bm-b 冻", CANON_BLOCK, "canon")
    wr(CANON, data)
    print("canon: W91 bullet inserted (+%d bytes)" % len(CANON_BLOCK))

# --- 2. pf N1_BANDS[91] ---------------------------------------------------------
PF_BLOCK = (
    "    # EIGHTIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r578 bm-b\n"
    "    # freeze): engine_owner rows 79 + candidate; bm-b's\n"
    "    # thirtieth owned per machine-derive (engine_owner==bm-b\n"
    "    # rows 29 + candidate). Wave 91 = first free number after the\n"
    "    # registered W89 row SKIPPING the bm-a-declared W90 seat\n"
    "    # (MSG-20261002-1415-bma, published=reserved r518-1).\n"
    "    # W90 seat-published, unregistered at this freeze (bm-a freeze\n"
    "    # in flight) -- one in-flight upstream seat, finalize merge loop\n"
    "    # stays FAIL-CLOSED r307 at run time.\n"
    "    # A-SIDE SKIP-PAST-PUBLISHED CHAIN (r518-1): W89 tail 223_003 ->\n"
    "    # W90 pub A 223_004..225_003 -> first clean 225_004..227_003\n"
    "    # (= W90 published A end + 1) CLEAN.\n"
    "    # B-SIDE PIN CHAIN: 56_201..56_400 == W90 pub B -> skip ->\n"
    "    # 56_401..56_600 REFUSED in-band at SEED_REGISTRY\n"
    "    # p4_batch3_dca=56_500 (median position 99/199, non-endpoint) ->\n"
    "    # D-20261002-05 pin: PAST-HIT start-window hit+1 restart\n"
    "    # 56_501..56_700 CLEAN (window-step-chain reading 56_601..56_800\n"
    "    # BANNED by the pin; W68-B positive anchor).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r578bmb_w91_band_gate.py ADMIT receipt vs the\n"
    "    # 87-row pre-W91 table + live SEED_REGISTRY values + probe\n"
    "    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n"
    "    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot\n"
    "    # vacancy machine-checked). W92+ projection: A 227_004..229_003\n"
    "    # CLEAN; B 56_701..56_900 CLEAN (next freezer must re-derive).\n"
    "    91: {\"a\": (225_004, 227_003), \"b_exit\": (56_501, 56_700),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(PF)
if b'91: {"a": (225_004, 227_003)' in data:
    print("SKIP pf: already present")
else:
    data = insert_after_entry(
        data,
        '89: {"a": (221_004, 223_003), "b_exit": (56_001, 56_200),',
        PF_BLOCK, "pf")
    wr(PF, data)
    print("pf: N1_BANDS[91] inserted (+%d bytes)" % len(PF_BLOCK))

# --- 3. n1 WAVE_CONFIGS[91] ------------------------------------------------------
N1_CFG_BLOCK = (
    "                       91: {\"batch\": \"PERPETUAL-N1-W91\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W91_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; EIGHTIETH ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 79 + candidate; prose \"\n"
    "                                       \"ordinal -1 drift disclosed since W80, r359 law), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W89 row \"\n"
    "                                       \"SKIPPING the published-but-unregistered W90 seat \"\n"
    "                                       \"bm-a MSG-20261002-1415-bma; seat published=reserved \"\n"
    "                                       \"MSG-20261002-1425-bmb PUSHED to origin BEFORE this \"\n"
    "                                       \"freeze per r565 early-visibility law), \"\n"
    "                                       \"engine_owner=bm-b, wave 91: A-SIDE \"\n"
    "                                       \"SKIP-PAST-PUBLISHED CHAIN (W89 tail -> W90 pub A -> \"\n"
    "                                       \"first clean A 225_004..227_003 CLEAN) + \"\n"
    "                                       \"B-SIDE PIN CHAIN (56_201..56_400 == W90 pub B -> \"\n"
    "                                       \"skip -> 56_401..56_600 REFUSED in-band at \"\n"
    "                                       \"SEED_REGISTRY p4_batch3_dca=56_500 median position \"\n"
    "                                       \"99/199 non-endpoint -> D-20261002-05 pin: past-hit \"\n"
    "                                       \"restart 56_501..56_700 CLEAN; window-step-chain \"\n"
    "                                       \"reading 56_601..56_800 BANNED; W68-B positive \"\n"
    "                                       \"anchor; ADMIT receipt \"\n"
    "                                       \"results/_r578bmb_w91_band_gate.py; W92+ projection: \"\n"
    "                                       \"A 227_004..229_003 CLEAN / B 56_701..56_900 CLEAN, \"\n"
    "                                       \"disclosed for the next freezer); W87 finalize LANDED \"\n"
    "                                       \"(net chain head 555,948 = W87 bm-a r578, K=189,320 \"\n"
    "                                       \"merged pool) + THREE IN-FLIGHT UPSTREAM SEATS at this \"\n"
    "                                       \"freeze (W88 bm-c registered finalize-pending + W89 \"\n"
    "                                       \"bm-b registered 12/12-burned finalize-pending + W90 \"\n"
    "                                       \"bm-a seat-published-unregistered -- unregistered-gap \"\n"
    "                                       \"honest notes per the W19/W18/W49 precedent; finalize \"\n"
    "                                       \"merge loop stays FAIL-CLOSED r307 at run time)\"),\n"
    "                            \"a_seed_base\": 225_004,        # law sec.4 W91 A: 225_004..227_003 (skip-past-published chain)\n"
    "                            \"b_exit_seed_base\": 56_501,   # law sec.4 W91 B: 56_501..56_700 (median-hit pin D-20261002-05 at p4_batch3_dca=56_500)\n"
    "                            \"shard_subdir\": \"n1_w91\", \"out_name\": \"n1_w91_results.json\",\n"
    "                            \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(N1)
if MARK.encode("utf-8") in data:
    print("SKIP n1 cfg: already present")
else:
    data = insert_after_entry(
        data,
        '"shard_subdir": "n1_w89", "out_name": "n1_w89_results.json",',
        N1_CFG_BLOCK, "n1cfg")
    wr(N1, data)
    print("n1: WAVE_CONFIGS[91] inserted (+%d bytes)" % len(N1_CFG_BLOCK))

# --- 4. n1 selftest W91 materializer leg ----------------------------------------
LEG_MARK = "W91 materializer face (r578 bm-b freeze"
N1_LEG_BLOCK = (
    "    # --- W91 materializer face (r578 bm-b freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's\n"
    "    #     thirtieth owned per machine-derive (engine_owner==bm-b\n"
    "    #     rows 29 + candidate); wave 91 = first free number after the\n"
    "    #     registered W89 row SKIPPING the published-but-unregistered\n"
    "    #     W90 seat (bm-a, MSG-20261002-1415-bma). EIGHTIETH engine\n"
    "    #     wave BY MACHINE-DERIVE (engine_owner rows 79 + candidate;\n"
    "    #     prose ordinal -1 drift disclosed since W80, r359 law). Seat\n"
    "    #     published=reserved MSG-20261002-1425-bmb pushed to origin\n"
    "    #     BEFORE this freeze per r565 law. ADMIT receipt\n"
    "    #     results/_r578bmb_w91_band_gate.py tri-state rc0 (mode A90).\n"
    "    _set_wave(91)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[91][\"a_seed_base\"] == pf.N1_BANDS[91][\"a\"][0], \\\n"
    "            \"W91 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[91][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[91][\"b_exit\"][0], \"W91 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[91].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[91].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W91 engine_owner drift (law mirror parity)\"\n"
    "        w91_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w91_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w91_a & w91_b), \"W91 A/B band overlap\"\n"
    "        assert not (w91_a & reg_ints) and not (w91_b & reg_ints), \\\n"
    "            \"W91 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w91_a), (\"B\", w91_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W91 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W91 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W91 {nm} hits probe seeds\"\n"
    "        assert pf.N1_BANDS[73] == {\"a\": (189_004, 191_003),\n"
    "                                   \"b_exit\": (51_601, 51_800),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W73 row parity drift (r307 two-state)\"\n"
    "        assert pf.N1_BANDS[74] == {\"a\": (191_004, 193_003),\n"
    "                                   \"b_exit\": (52_001, 52_200),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W74 row parity drift (r307 two-state)\"\n"
    "        assert pf.N1_BANDS[75] == {\"a\": (193_004, 195_003),\n"
    "                                   \"b_exit\": (52_201, 52_400),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W75 row parity drift (r307 two-state)\"\n"
    "        assert pf.N1_BANDS[76] == {\"a\": (195_004, 197_003),\n"
    "                                   \"b_exit\": (52_401, 52_600),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W76 row parity drift (r307 two-state)\"\n"
    "        assert pf.N1_BANDS[77] == {\"a\": (197_004, 199_003),\n"
    "                                   \"b_exit\": (52_601, 52_800),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W77 row parity drift (r307 two-state; bm-a r572)\"\n"
    "        assert pf.N1_BANDS[78] == {\"a\": (199_004, 201_003),\n"
    "                                   \"b_exit\": (53_201, 53_400),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W78 row parity drift (r307 two-state; bm-c r363)\"\n"
    "        assert pf.N1_BANDS[79] == {\"a\": (201_004, 203_003),\n"
    "                                   \"b_exit\": (53_401, 53_600),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W79 row parity drift (r307 two-state; bm-b r573)\"\n"
    "        assert pf.N1_BANDS[80] == {\"a\": (203_004, 205_003),\n"
    "                                   \"b_exit\": (53_601, 53_800),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W80 row parity drift (r307 two-state; bm-c r364)\"\n"
    "        assert pf.N1_BANDS[81] == {\"a\": (205_004, 207_003),\n"
    "                                   \"b_exit\": (54_001, 54_200),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W81 row parity drift (r307 two-state; bm-a r574)\"\n"
    "        assert pf.N1_BANDS[82] == {\"a\": (207_004, 209_003),\n"
    "                                   \"b_exit\": (54_201, 54_400),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W82 row parity drift (r307 two-state; bm-b r574)\"\n"
    "        assert pf.N1_BANDS[83] == {\"a\": (209_004, 211_003),\n"
    "                                   \"b_exit\": (54_401, 54_600),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W83 row parity drift (r307 two-state; bm-c r365)\"\n"
    "        assert pf.N1_BANDS[84] == {\"a\": (211_004, 213_003),\n"
    "                                   \"b_exit\": (54_601, 54_800),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W84 row parity drift (r307 two-state; bm-a r575)\"\n"
    "        assert pf.N1_BANDS[85] == {\"a\": (213_004, 215_003),\n"
    "                                   \"b_exit\": (55_001, 55_200),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W85 row parity drift (r307 two-state; bm-b r576)\"\n"
    "        assert pf.N1_BANDS[86] == {\"a\": (215_004, 217_003),\n"
    "                                   \"b_exit\": (55_201, 55_400),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W86 row parity drift (r307 two-state; bm-a r576)\"\n"
    "        assert pf.N1_BANDS[87] == {\"a\": (217_004, 219_003),\n"
    "                                   \"b_exit\": (55_501, 55_700),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W87 row parity drift (r307 two-state; bm-a r577)\"\n"
    "        assert pf.N1_BANDS[88] == {\"a\": (219_004, 221_003),\n"
    "                                   \"b_exit\": (55_701, 55_900),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W88 row parity drift (r307 two-state; bm-c r368)\"\n"
    "        assert pf.N1_BANDS[89] == {\"a\": (221_004, 223_003),\n"
    "                                   \"b_exit\": (56_001, 56_200),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W89 row parity drift (r307 two-state; bm-b r578)\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 90)]:\n"
    "            assert not (w91_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W91 A hits W{wprev}\"\n"
    "            assert not (w91_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W91 B hits W{wprev}\"\n"
    "        assert not (w91_a & set(range(223_004, 225_004))) and \\\n"
    "            not (w91_b & set(range(56_201, 56_401))), \\\n"
    "            \"W91 bands must clear the W90 published projection (r518-1)\"\n"
    "        n3r1_used91 = set(range(70_000, 70_006))\n"
    "        assert not (w91_a & n3r1_used91) and not (w91_b & n3r1_used91), \\\n"
    "            \"W91 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w91_a & lfc_actual12) and not (w91_b & lfc_actual12), \\\n"
    "            \"W91 bands must clear the lfc actual draw range\"\n"
    "        assert not (w91_a & options_actual12) and \\\n"
    "            not (w91_b & options_actual12), \\\n"
    "            \"W91 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[91][\"a_seed_base\"] == 225_004 == \\\n"
    "            pf.N1_BANDS[89][\"a\"][1] + 2_001, \\\n"
    "            \"W91 A must start past the W90 published seat (skip-past-\" \\\n"
    "            \"published chain: W89 tail + 2_001 = 225_004; \" \\\n"
    "            \"window 225_004..227_003 CLEAN)\"\n"
    "        arith_a91 = set(range(225_004, 227_004))\n"
    "        assert not (arith_a91 & reg_ints), \\\n"
    "            \"W91 A window must be CLEAN (skip-past-published ADMIT face)\"\n"
    "        assert WAVE_CONFIGS[91][\"b_exit_seed_base\"] == 56_501 == 56_500 + 1, \\\n"
    "            \"W91 B must start at the 56_500 hit + 1 (D-20261002-05 pin: \" \\\n"
    "            \"past-hit start-window; arithmetic window 56_401..56_600 \" \\\n"
    "            \"REFUSED in-band at p4_batch3_dca=56_500 median, non-endpoint)\"\n"
    "        assert WAVE_CONFIGS[91][\"b_exit_seed_base\"] != 56_601, \\\n"
    "            \"W91 B window-step-chain reading 56_601..56_800 is BANNED \" \\\n"
    "            \"by D-20261002-05 (past-hit start-window pinned; W68-B \" \\\n"
    "            \"anchor)\"\n"
    "        arith_b91 = set(range(56_401, 56_601))\n"
    "        b_hit91 = sorted(p for p in arith_b91 if p in reg_ints)\n"
    "        assert b_hit91 == [56_500], \\\n"
    "            \"W91 B pre-window must hit exactly [56_500] (median 99/199)\"\n"
    "        assert not (w91_b & reg_ints), \\\n"
    "            \"W91 B restart window 56_501..56_700 must be CLEAN\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W91-SHARD-0\",\n"
    "                                          \"n1w91-0of12\"), \"W91 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W91-SHARD-11\",\n"
    "                                          \"n1w91-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w91\") and OUT.endswith(\n"
    "            \"n1_w91_results.json\"), \"W91 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 90)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W91 shard dir collides with W{wprev}\"\n"
    "        assert [w for w in WAVE_CONFIGS if w < 90] == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 90)], \\\n"
    "            \"W91 prior-wave set must derive from registry keys (no 15; \" \\\n"
    "            \"incl. 48..89 -- W88/W89 registered, W90 in flight, \" \\\n"
    "            \"FAIL-CLOSED)\"\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W91_PREREG.md\")), \\\n"
    "            \"W91 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
    "\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    i = data.find("W89 per-wave prereg missing (materializer requirement)"
                  .encode("utf-8"))
    assert i >= 0, "leg anchor: W89 prereg assert not found"
    j = data.find(b"        _set_wave(2)\n", i)
    assert j > i, "leg anchor: W89 finally not found"
    j_end = j + len(b"        _set_wave(2)\n")
    nxt = data[j_end:j_end + 30]
    assert b"W91" not in nxt and b"W90" not in nxt, \
        f"leg post-anchor guard: {nxt!r}"
    out = data[:j_end] + N1_LEG_BLOCK + data[j_end:]
    wr(N1, out)
    print("n1: W91 materializer leg inserted (+%d bytes)" % len(N1_LEG_BLOCK))

# --- 5. n1 selftest PASS-print W91 fragment -------------------------------------
FRAG_MARK = "law sec.4 W91 row, r578 bm-b]"
N1_FRAG_BLOCK = (
    "          \"+ W91 materializer face [same guard set, dep=W17..W87 outputs \"\n"
    "          \"ALL PRESENT (landed chain head 555,948, K=189,320, W87 bm-a \"\n"
    "          \"r578 one-pass), W88 bm-c + W89 bm-b + W90 bm-a = THREE \"\n"
    "          \"in-flight upstream seats at freeze (W88/W89 registered \"\n"
    "          \"finalize-pending; W90 seat-published unregistered; \"\n"
    "          \"FAIL-CLOSED r307 at run time), EIGHTIETH ENGINE-OWNED WAVE \"\n"
    "          \"BY MACHINE-DERIVE (engine_owner rows 79 + candidate; prose \"\n"
    "          \"ordinal -1 drift disclosed since W80, r359 law) bm-b's \"\n"
    "          \"THIRTIETH owned claim per machine-derive (engine_owner==bm-b \"\n"
    "          \"rows 29 + candidate), engine_owner=bm-b per engine de-throttle \"\n"
    "          \"law O-20261001-2355 sec.2 own-continuous-series (wave 91 = \"\n"
    "          \"first FREE number SKIPPING the published W90 seat bm-a \"\n"
    "          \"MSG-20261002-1415-bma; seat published=reserved \"\n"
    "          \"MSG-20261002-1425-bmb pushed BEFORE the freeze per r565 law), \"\n"
    "          \"A-SIDE SKIP-PAST-PUBLISHED CHAIN (W89 tail -> W90 pub \"\n"
    "          \"223_004..225_003 -> first clean window 225_004..227_003 \"\n"
    "          \"CLEAN) + B-SIDE MEDIAN-HIT PIN CHAIN per D-20261002-05 \"\n"
    "          \"(arithmetic 56_401..56_600 REFUSED in-band at SEED_REGISTRY \"\n"
    "          \"p4_batch3_dca=56_500 median position 99/199 non-endpoint -> \"\n"
    "          \"past-hit restart 56_501..56_700 CLEAN; window-step-chain \"\n"
    "          \"reading 56_601..56_800 BANNED, W68-B positive anchor; ADMIT \"\n"
    "          \"receipt results/_r578bmb_w91_band_gate.py rc0 tri-state mode \"\n"
    "          \"A90; W92+ projection A 227_004..229_003 CLEAN / B \"\n"
    "          \"56_701..56_900 CLEAN disclosed for the next freezer; not a \"\n"
    "          \"free pick -- R250), N3-R1 used-seed leg, probe-seed cluster \"\n"
    "          \"leg, law sec.4 W91 row, r578 bm-b] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    i = data.find("r578 bm-b estate adoption] ".encode("utf-8"))
    assert i >= 0, "frag anchor: W89 fragment end not found"
    j = data.find(b"\n", i) + 1
    nxt = data[j:j + 30]
    assert b"+ T-141" in nxt, f"frag post-anchor guard: {nxt!r}"
    out = data[:j] + N1_FRAG_BLOCK + data[j:]
    wr(N1, out)
    print("n1: W91 PASS fragment inserted (+%d bytes)" % len(N1_FRAG_BLOCK))

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")

