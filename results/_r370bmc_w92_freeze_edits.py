# -*- coding: utf-8 -*-
"""r370 bm-c W92 freeze five-face edits (r560-law generator).

Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W92 bullet  -> research/PERPETUAL_FACES.md, after the W91 bullet
  2. pf N1_BANDS[92]   -> scripts/perpetual_faces.py, after the [91] entry
  3. n1 WAVE_CONFIGS[92] -> scripts/perpetual_faces_n1.py, after the 91 entry
  4. n1 selftest W92 materializer leg -> after the W91 leg
  5. n1 selftest PASS-print W92 fragment -> after the W91 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "research", "PERPETUAL_FACES.md")
PF = os.path.join(ROOT, "scripts", "perpetual_faces.py")
N1 = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")

MARK = "PERPETUAL-N1-W92"


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, b):
    with open(p, "wb") as f:
        f.write(b)


def eol_of(data):
    """Detect the file's dominant line ending (CRLF vs LF) -- r530 bytes-law."""
    i = data.find(b"\n")
    if i > 0 and data[i - 1:i] == b"\r":
        return b"\r\n"
    return b"\n"


def to_eol(block, eol):
    """Convert an LF-authored block to the file's on-disk line ending."""
    if eol == b"\r\n":
        return block.replace(b"\n", b"\r\n")
    return block


def insert_after(data, needle, block, tag):
    """Insert block (bytes) right after the line containing needle.
    Aborts if needle absent or not pure insertion (r560 FIX-A law)."""
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    assert j > i, f"{tag}: anchor line has no newline"
    nxt = data[j:j + 60]
    assert b"92:" not in nxt and b"| 92" not in nxt and b"W93" not in nxt, \
        f"{tag}: post-anchor line looks like a foreign W92/W93 row ({nxt!r})"
    out = data[:j] + block + data[j:]
    return out


def insert_after_entry(data, needle, block, tag):
    """Insert block after the 2-line dict ENTRY starting at the needle line
    (needle line + its 'engine_owner' closing line). Abort on any mismatch."""
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    k = data.find(b"\n", j) + 1
    mid = data[j:k]
    assert b"engine_owner" in mid, \
        f"{tag}: line after needle is not an entry close ({mid[:60]!r})"
    nxt = data[k:k + 60]
    assert b"92:" not in nxt and b'"engine_owner"' not in nxt, \
        f"{tag}: post-anchor line looks like a foreign row ({nxt!r})"
    out = data[:k] + block + data[k:]
    return out


# --- 1. canon bullet -----------------------------------------------------------
CANON_BLOCK = (
    "\n"
    "- N1 波92（r370 bm-c 冻·prereg 时展行）：**第八十二枚引擎波·bm-c 第二十八枚自有波〔机面 derive：engine_owner 行 81+本候选／engine_owner==bm-c 行 27+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W91 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻 v0.4 per-tick 重读活树——冻结 commit 后下一 tick 重读自见新行自燃·免杀重启·W80/W83/W88 免重启实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 92=注册表 W91 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W92 号位净空·pf 行+prereg 路径双查+**leg0b 全 inbox+processed/ 扫描 W92 席位零命中机验·单态零席位空档=全行 W2..W91 已注册**〔W89 bm-b 烧毕 finalize 未落账+W90 bm-a 烧录中 6/12+W91 bm-b 烧毕 finalize 未落账〕）·**席位公示=MSG-20261002-1447-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin=766daf77a·r565 早可见性律〕】·本窗实况=**W88 bm-c finalize 已落账（净链头 558,148·K=191,520）+三在飞上游席（W89 bm-b+W90 bm-a+W91 bm-b·全已注册）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r370bmc_w92_band_gate.py rc0·表尾=W91）**：**A-ext seed=227_004..229_003**（W91 A 尾 227_003 算术续带·步长 2_000·**CLEAN 零拒绝点**·诚实前向走窗〔算术续带先例族〕）；**B-ext exit seed=56_701..56_900**（W91 B 尾 56_700 算术续带·**CLEAN 零拒绝点**·无 pin 链无跳位）。R250：W92 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W92 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W92_PREREG.md（§5 预测锚=W88 finalize 实测值〔merged mu −0.0925512·K=191,520·A p95 0.3172·K-lift −0.0002@555,948〕·单波跨锚锚滚动律 r576·写死于跑前）·**W93+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 229_004..231_003 CLEAN；B 56_901..57_100 **REFUSED [57_000, 57_100]**（算术位撞 SEED_REGISTRY 值——下波按法典 §4 钉死行/pin 链 derive 首净窗）。\n"
).encode("utf-8")

data = rd(CANON)
if "波92（r370 bm-c 冻".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data = insert_after(data, "N1 波91（r578 bm-b 冻",
                        to_eol(CANON_BLOCK, eol_of(data)), "canon")
    wr(CANON, data)
    print("canon: W92 bullet inserted")

# --- 2. pf N1_BANDS[92] ---------------------------------------------------------
PF_BLOCK = (
    "    # EIGHTY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE (r370 bm-c\n"
    "    # freeze): engine_owner rows 81 + candidate; bm-c's\n"
    "    # twenty-eighth owned per machine-derive (engine_owner==bm-c\n"
    "    # rows 27 + candidate). Wave 92 = first free number after the\n"
    "    # registered W91 row (bm-b r578 freeze 636dab137); SINGLE STATE\n"
    "    # zero seat gap: all rows W2..W91 registered (W89/W90/W91 =\n"
    "    # three in-flight upstream seats, finalize merge loop stays\n"
    "    # FAIL-CLOSED r307 at run time).\n"
    "    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W91\n"
    "    # tails: A 227_004..229_003 (227_003 + 1, width 2_000) and\n"
    "    # B 56_701..56_900 (56_700 + 1, width 200), both CLEAN zero\n"
    "    # refusal points (honest forward walk, no pin chain needed).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r370bmc_w92_band_gate.py ADMIT receipt vs the\n"
    "    # 89-row pre-W92 table + live SEED_REGISTRY values + probe\n"
    "    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n"
    "    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot\n"
    "    # vacancy machine-checked). Seat published=reserved\n"
    "    # MSG-20261002-1447-bmc pushed to origin (766daf77a) BEFORE\n"
    "    # this freeze per r565 law. W93+ projection: A 229_004..231_003\n"
    "    # CLEAN; B 56_901..57_100 REFUSED [57_000, 57_100] (next\n"
    "    # freezer must re-derive per the sec.4 pin law).\n"
    "    92: {\"a\": (227_004, 229_003), \"b_exit\": (56_701, 56_900),\n"
    "         \"engine_owner\": \"bm-c\"},\n"
).encode("utf-8")

data = rd(PF)
if b'92: {"a": (227_004, 229_003)' in data:
    print("SKIP pf: already present")
else:
    data = insert_after_entry(
        data,
        '91: {"a": (225_004, 227_003), "b_exit": (56_501, 56_700),',
        to_eol(PF_BLOCK, eol_of(data)), "pf")
    wr(PF, data)
    print("pf: N1_BANDS[92] inserted")

# --- 3. n1 WAVE_CONFIGS[92] ------------------------------------------------------
N1_CFG_BLOCK = (
    "                       92: {\"batch\": \"PERPETUAL-N1-W92\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W92_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; EIGHTY-SECOND ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 81 + candidate; prose \"\n"
    "                                       \"ordinal -1 drift disclosed since W80, r359 law), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W91 row; \"\n"
    "                                       \"SINGLE STATE zero seat gap: all rows W2..W91 registered; \"\n"
    "                                       \"seat published=reserved MSG-20261002-1447-bmc PUSHED to \"\n"
    "                                       \"origin 766daf77a BEFORE this freeze per r565 law), \"\n"
    "                                       \"engine_owner=bm-c, wave 92: BOTH SIDES ARITHMETIC \"\n"
    "                                       \"CONTINUATION from the registered W91 tails (A \"\n"
    "                                       \"227_004..229_003 + B 56_701..56_900 both CLEAN zero \"\n"
    "                                       \"refusal points, honest forward walk, no pin chain \"\n"
    "                                       \"needed; ADMIT receipt results/_r370bmc_w92_band_gate.py; \"\n"
    "                                       \"W93+ projection: A 229_004..231_003 CLEAN / B \"\n"
    "                                       \"56_901..57_100 REFUSED [57_000, 57_100] disclosed for \"\n"
    "                                       \"the next freezer); W88 finalize LANDED (net chain head \"\n"
    "                                       \"558,148, K=191,520, W88 bm-c r369 one-pass) + THREE \"\n"
    "                                       \"IN-FLIGHT UPSTREAM SEATS at this freeze (W89 bm-b \"\n"
    "                                       \"registered 12/12-burned finalize-pending + W90 bm-a \"\n"
    "                                       \"registered burning 6/12 + W91 bm-b registered \"\n"
    "                                       \"12/12-burned finalize-pending -- ALL REGISTERED, no \"\n"
    "                                       \"unregistered gap; finalize merge loop stays \"\n"
    "                                       \"FAIL-CLOSED r307 at run time)\"),\n"
    "                            \"a_seed_base\": 227_004,        # law sec.4 W92 A: 227_004..229_003 (arithmetic continuation from W91 tail 227_003)\n"
    "                            \"b_exit_seed_base\": 56_701,   # law sec.4 W92 B: 56_701..56_900 (arithmetic continuation from W91 tail 56_700)\n"
    "                            \"shard_subdir\": \"n1_w92\", \"out_name\": \"n1_w92_results.json\",\n"
    "                            \"engine_owner\": \"bm-c\"},\n"
).encode("utf-8")

data = rd(N1)
if MARK.encode("utf-8") in data:
    print("SKIP n1 cfg: already present")
else:
    data = insert_after_entry(
        data,
        '"shard_subdir": "n1_w91", "out_name": "n1_w91_results.json",',
        to_eol(N1_CFG_BLOCK, eol_of(data)), "n1cfg")
    wr(N1, data)
    print("n1: WAVE_CONFIGS[92] inserted")

# --- 4. n1 selftest W92 materializer leg ----------------------------------------
LEG_MARK = "W92 materializer face (r370 bm-c freeze"
N1_LEG_BLOCK = (
    "    # --- W92 materializer face (r370 bm-c freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's\n"
    "    #     twenty-eighth owned per machine-derive (engine_owner==bm-c\n"
    "    #     rows 27 + candidate); wave 92 = first free number after the\n"
    "    #     registered W91 row, SINGLE STATE zero seat gap (all rows\n"
    "    #     W2..W91 registered). EIGHTY-SECOND engine wave BY\n"
    "    #     MACHINE-DERIVE (engine_owner rows 81 + candidate; prose\n"
    "    #     ordinal -1 drift disclosed since W80, r359 law). Seat\n"
    "    #     published=reserved MSG-20261002-1447-bmc pushed to origin\n"
    "    #     (766daf77a) BEFORE this freeze per r565 law. ADMIT receipt\n"
    "    #     results/_r370bmc_w92_band_gate.py rc0 single state.\n"
    "    _set_wave(92)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[92][\"a_seed_base\"] == pf.N1_BANDS[92][\"a\"][0], \\\n"
    "            \"W92 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[92][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[92][\"b_exit\"][0], \"W92 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[92].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[92].get(\"engine_owner\") == \"bm-c\", \\\n"
    "            \"W92 engine_owner drift (law mirror parity)\"\n"
    "        w92_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w92_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w92_a & w92_b), \"W92 A/B band overlap\"\n"
    "        assert not (w92_a & reg_ints) and not (w92_b & reg_ints), \\\n"
    "            \"W92 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w92_a), (\"B\", w92_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W92 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W92 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W92 {nm} hits probe seeds\"\n"
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
    "        assert pf.N1_BANDS[90] == {\"a\": (223_004, 225_003),\n"
    "                                   \"b_exit\": (56_201, 56_400),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W90 row parity drift (r307 two-state; bm-a r579)\"\n"
    "        assert pf.N1_BANDS[91] == {\"a\": (225_004, 227_003),\n"
    "                                   \"b_exit\": (56_501, 56_700),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W91 row parity drift (r307 two-state; bm-b r578)\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 92)]:\n"
    "            assert not (w92_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W92 A hits W{wprev}\"\n"
    "            assert not (w92_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W92 B hits W{wprev}\"\n"
    "        n3r1_used92 = set(range(70_000, 70_006))\n"
    "        assert not (w92_a & n3r1_used92) and not (w92_b & n3r1_used92), \\\n"
    "            \"W92 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w92_a & lfc_actual12) and not (w92_b & lfc_actual12), \\\n"
    "            \"W92 bands must clear the lfc actual draw range\"\n"
    "        assert not (w92_a & options_actual12) and \\\n"
    "            not (w92_b & options_actual12), \\\n"
    "            \"W92 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[92][\"a_seed_base\"] == 227_004 == \\\n"
    "            pf.N1_BANDS[91][\"a\"][1] + 1, \\\n"
    "            \"W92 A must be the arithmetic continuation from the \" \\\n"
    "            \"registered W91 tail (227_003 + 1 = 227_004; window \" \\\n"
    "            \"227_004..229_003 CLEAN)\"\n"
    "        arith_a92 = set(range(227_004, 229_004))\n"
    "        assert not (arith_a92 & reg_ints), \\\n"
    "            \"W92 A window must be CLEAN (arithmetic continuation ADMIT face)\"\n"
    "        assert WAVE_CONFIGS[92][\"b_exit_seed_base\"] == 56_701 == \\\n"
    "            pf.N1_BANDS[91][\"b_exit\"][1] + 1, \\\n"
    "            \"W92 B must be the arithmetic continuation from the \" \\\n"
    "            \"registered W91 tail (56_700 + 1 = 56_701)\"\n"
    "        arith_b92 = set(range(56_701, 56_901))\n"
    "        assert not (arith_b92 & reg_ints), \\\n"
    "            \"W92 B window 56_701..56_900 must be CLEAN (zero refusal \" \\\n"
    "            \"points, no pin chain needed)\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W92-SHARD-0\",\n"
    "                                          \"n1w92-0of12\"), \"W92 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W92-SHARD-11\",\n"
    "                                          \"n1w92-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w92\") and OUT.endswith(\n"
    "            \"n1_w92_results.json\"), \"W92 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 92)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W92 shard dir collides with W{wprev}\"\n"
    "        assert [w for w in WAVE_CONFIGS if w < 92] == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 92)], \\\n"
    "            \"W92 prior-wave set must derive from registry keys (no 15; \" \\\n"
    "            \"incl. 48..91 -- W89/W90/W91 registered in flight, \" \\\n"
    "            \"FAIL-CLOSED)\"\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W92_PREREG.md\")), \\\n"
    "            \"W92 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
    "\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    eol = eol_of(data)
    i = data.find("W91 per-wave prereg missing (materializer requirement)"
                  .encode("utf-8"))
    assert i >= 0, "leg anchor: W91 prereg assert not found"
    j = data.find(b"        _set_wave(2)", i)  # EOL-tolerant needle
    assert j > i, "leg anchor: W91 finally not found"
    j_end = j + len(b"        _set_wave(2)") + len(eol)
    assert data[j_end - len(eol):j_end] == eol, "leg anchor: eol drift"
    nxt = data[j_end:j_end + 60]
    assert b"W92" not in nxt and b"W91" not in nxt, \
        f"leg post-anchor guard: {nxt!r}"
    assert b"T-141" in nxt, \
        f"leg post-anchor must be the T-141 lane face comment: {nxt!r}"
    out = data[:j_end] + to_eol(N1_LEG_BLOCK, eol) + data[j_end:]
    wr(N1, out)
    print("n1: W92 materializer leg inserted")

# --- 5. n1 selftest PASS-print W92 fragment -------------------------------------
FRAG_MARK = "law sec.4 W92 row, r370 bm-c]"
N1_FRAG_BLOCK = (
    "          \"+ W92 materializer face [same guard set, dep=W17..W88 outputs \"\n"
    "          \"ALL PRESENT (landed chain head 558,148, K=191,520, W88 bm-c \"\n"
    "          \"r369 one-pass), W89 bm-b + W90 bm-a + W91 bm-b = THREE \"\n"
    "          \"in-flight upstream seats at freeze (ALL REGISTERED, no \"\n"
    "          \"seat gap: W89/W91 burned 12/12 finalize-pending, W90 \"\n"
    "          \"burning 6/12; FAIL-CLOSED r307 at run time), EIGHTY-SECOND \"\n"
    "          \"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 81 + \"\n"
    "          \"candidate; prose ordinal -1 drift disclosed since W80, r359 \"\n"
    "          \"law) bm-c's TWENTY-EIGHTH owned claim per machine-derive \"\n"
    "          \"(engine_owner==bm-c rows 27 + candidate), engine_owner=bm-c \"\n"
    "          \"per engine de-throttle law O-20261001-2355 sec.2 \"\n"
    "          \"own-continuous-series (wave 92 = first FREE number after the \"\n"
    "          \"registered W91 row, single state zero seat gap; seat \"\n"
    "          \"published=reserved MSG-20261002-1447-bmc pushed to origin \"\n"
    "          \"766daf77a BEFORE the freeze per r565 law), BOTH-SIDES \"\n"
    "          \"ARITHMETIC CONTINUATION from the registered W91 tails (A \"\n"
    "          \"227_004..229_003 + B 56_701..56_900 both CLEAN zero refusal \"\n"
    "          \"points, honest forward walk, no pin chain needed; ADMIT \"\n"
    "          \"receipt results/_r370bmc_w92_band_gate.py rc0 single state; \"\n"
    "          \"W93+ projection A 229_004..231_003 CLEAN / B 56_901..57_100 \"\n"
    "          \"REFUSED [57_000, 57_100] disclosed for the next freezer; \"\n"
    "          \"not a free pick -- R250), N3-R1 used-seed leg, probe-seed \"\n"
    "          \"cluster leg, law sec.4 W92 row, r370 bm-c] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    eol = eol_of(data)
    i = data.find("law sec.4 W91 row, r578 bm-b] ".encode("utf-8"))
    assert i >= 0, "frag anchor: W91 fragment end not found"
    j = data.find(b"\n", i) + 1
    nxt = data[j:j + 60]
    assert b"+ W90 materializer face" in nxt, \
        f"frag post-anchor guard: {nxt!r}"
    out = data[:j] + to_eol(N1_FRAG_BLOCK, eol) + data[j:]
    wr(N1, out)
    print("n1: W92 PASS fragment inserted")

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")
