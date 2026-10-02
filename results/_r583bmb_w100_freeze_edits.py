# -*- coding: utf-8 -*-
"""r583 bm-b W100 freeze five-face edits (r560-law generator, r578 five-in-one).

Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W100 bullet  -> research/PERPETUAL_FACES.md, after the W99 row
  2. pf N1_BANDS[100]   -> scripts/perpetual_faces.py, after the 99 entry
  3. n1 WAVE_CONFIGS[100] -> scripts/perpetual_faces_n1.py, after the 99 entry
  4. n1 selftest W100 materializer leg -> after the W99 leg
  5. n1 selftest PASS-print W100 fragment -> after the W99 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
Byte-level in/out (r530 law). Multi-line assert messages parenthesized
(r580 bracket law). Post-anchor guards: next line after the W99 leg must
be the T-141 s2 lane face (no anchor-tail backfill -- r580 law).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "research", "PERPETUAL_FACES.md")
PF = os.path.join(ROOT, "scripts", "perpetual_faces.py")
N1 = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, b):
    with open(p, "wb") as f:
        f.write(b)


def insert_after(data, needle, block, tag, guard=None):
    i = data.find(needle)
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    assert j > i, f"{tag}: anchor line has no newline"
    nxt = data[j:j + 60]
    if guard:
        assert guard(nxt), f"{tag}: post-anchor guard fail: {nxt[:60]!r}"
    return data[:j] + block + data[j:]


def insert_after_entry(data, needle, block, tag, close_line, guard=None):
    """Insert block after the dict ENTRY starting at the needle line,
    walking to the entry's engine_owner close line (parameterized owner)."""
    i = data.find(needle)
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    k = j
    target = close_line.encode("ascii")
    while True:
        kend = data.find(b"\n", k) + 1
        ln = data[k:kend]
        if ln.strip() == target:
            k = kend
            break
        k = kend
        assert k < len(data), f"{tag}: entry close not found"
    nxt = data[k:k + 40]
    if guard:
        assert guard(nxt), f"{tag}: post-anchor guard fail: {nxt[:40]!r}"
    return data[:k] + block + data[k:]


# --- 1. canon W100 bullet ------------------------------------------------------
CANON_BLOCK = (
    "- N1 波100（r583 bm-b 冻·prereg 时展行）："
    "**第九十枚引擎波·bm-b 第三十四枚自有波"
    "〔机面 derive：engine_owner 行 89+本候选／"
    "engine_owner==bm-b 行 33+本候选〕**·engine_owner=bm-b"
    "·SATURATION_ENGINE_LAW §1/§2 同 W10-W99 合同·不入池"
    "·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 "
    "§二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 "
    "commit 后下一 tick 新进程重读活树自见新行=免杀重启免做"
    "·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W89/W91/W93/W95/W97 "
    "同窗实证·点火验证唯一证据=产物增长面 r325 律】·"
    "【never-dry 供给律常设步·**波号 100=注册表 W99 行后首个自由号"
    "（零席位空档：W2..W99 全行已注册·单态；r511 表尾锁例冻结前 "
    "fetch 实核表尾时 W100 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查"
    "+leg0b 全 inbox/processed/ 扫描 W100 席位零外机命中机验·本机席位"
    "公示豁免=MSG-20261002-1615-bmb 已推 origin 6b8c9fa7c r582 先于本"
    "冻结 r565 律）**；**席位公示=MSG-20261002-1615-bmb**"
    "（published=reserved r518-① 律·先于冻结 commit 推 origin r565 "
    "早可见性律）；带位=**A-ext seed=243_004..245_003**（==W99 行 A 尾 "
    "243_003+1 起·步长 2_000·**CLEAN 零拒绝点·算术续带**）+"
    "**B-ext exit seed=58_751..58_950**（==W99 行 B 尾 58_750+1 起·步长 "
    "200·**CLEAN 零拒绝点·双侧算术续带无 pin 链无跳位〔W92 r370 同式"
    "先例族·零跳位净走〕**）；ADMIT 回执=results/_r583bmb_w100_band_gate.py "
    "rc0（单态 97 行表·扫描面=pre-W100 全行注册带+W1 ext+v1 在用带"
    "+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带 70_000..70_005 "
    "MSG-183x r529 强制腿+runner 设计探针种子簇 95_000..95_003 r335 腿"
    "+N2/N4 探针点+N2-W15 草案探针点+lfc/options 实际流避让腿）；"
    "per-wave prereg=research/PERPETUAL_N1_W100_PREREG.md（预测锚=W97 "
    "finalize 实测值·锚滚动律自 W76 滚动至 W97·本波=零命中 banned gate "
    "ADMIT 0 matched）；**W101+ 投影（gate 机证·下波冻结方必复核非转抄）**："
    "A 245_004..247_003 **CLEAN**；B 58_951..59_150 **REFUSED at "
    "[59_000]**（D-20261002-05 钉死行适用·bm-a W101 席位已公示·hit+1 "
    "起窗待其 gate 机导）。\n"
).encode("utf-8")

data = rd(CANON)
if "- N1 波100（r583 bm-b 冻".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data2 = insert_after(
        data, "- N1 波99".encode("utf-8"), CANON_BLOCK, "canon",
        guard=lambda nxt: (not nxt.startswith("- N1 ".encode("utf-8")))
        or nxt.startswith("- N1 波101".encode("utf-8")))
    assert data2.count(CANON_BLOCK) == 1
    wr(CANON, data2)
    print("canon: W100 bullet inserted (+%d bytes)" % len(CANON_BLOCK))

# --- 2. pf N1_BANDS[100] --------------------------------------------------------
PF_BLOCK = (
    "    # NINETIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r583 bm-b\n"
    "    # freeze): engine_owner rows 89 + candidate; bm-b's\n"
    "    # thirty-fourth owned per machine-derive (engine_owner==bm-b\n"
    "    # rows 33 + candidate). Wave 100 = first free number after the\n"
    "    # registered W99 row (zero seat gaps: W2..W99 all registered;\n"
    "    # single state, no skip-past-published chain).\n"
    "    # W1..W97 finalizes ALL LANDED (landed chain head 577,948 = W97\n"
    "    # bm-b r583 one-pass; K=211,320 merged pool). TWO in-flight\n"
    "    # upstream seats (W98 bm-a 12/12 burned finalize-pending + W99\n"
    "    # bm-c 12/12 burned finalize-pending, ALL REGISTERED) -- finalize\n"
    "    # merge loop stays FAIL-CLOSED r307 at run time.\n"
    "    # BOTH SIDES = ARITHMETIC CONTINUATION from the registered W99\n"
    "    # tails, CLEAN zero refusal points (honest forward walk, no\n"
    "    # pin chain, no skips -- W92 r370 precedent family).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r583bmb_w100_band_gate.py ADMIT receipt rc0 single\n"
    "    # state vs the 97-row pre-W100 table + live SEED_REGISTRY values\n"
    "    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n"
    "    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n"
    "    # origin slot vacancy machine-checked; seat published=reserved\n"
    "    # MSG-20261002-1615-bmb pushed BEFORE this freeze per r565\n"
    "    # law). W101+ projection: A 245_004..247_003 CLEAN; B\n"
    "    # 58_951..59_150 REFUSED at [59_000] (D-20261002-05 pin for\n"
    "    # the next freezer; bm-a W101 seat published).\n"
    "    # NOT a re-pick (R250: W100 bands were never assigned).\n"
    "    100: {\"a\": (243_004, 245_003), \"b_exit\": (58_751, 58_950),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(PF)
if b'100: {"a": (243_004, 245_003)' in data:
    print("SKIP pf: already present")
else:
    data2 = insert_after_entry(
        data, '99: {"a": (241_004, 243_003)'.encode("utf-8"),
        PF_BLOCK, "pf", close_line='"engine_owner": "bm-c"},',
        guard=lambda nxt: nxt.startswith(b"}") or nxt.strip().startswith(b"#"))
    assert data2.count(b'100: {"a": (243_004, 245_003)') == 1
    wr(PF, data2)
    print("pf: N1_BANDS[100] inserted (+%d bytes)" % len(PF_BLOCK))

# --- 3. n1 WAVE_CONFIGS[100] -----------------------------------------------------
N1_CFG_BLOCK = (
    "                       100: {\"batch\": \"PERPETUAL-N1-W100\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W100_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; NINETIETH ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 89 + candidate), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W99 row, \"\n"
    "                                       \"zero seat gaps: W2..W99 all registered, single state; \"\n"
    "                                       \"seat published=reserved MSG-20261002-1615-bmb PUSHED to \"\n"
    "                                       \"origin 6b8c9fa7c r582 BEFORE this freeze per r565 \"\n"
    "                                       \"early-visibility law), \"\n"
    "                                       \"engine_owner=bm-b, wave 100: BOTH SIDES = ARITHMETIC \"\n"
    "                                       \"CONTINUATION from the registered W99 tails (A \"\n"
    "                                       \"243_004..245_003 CLEAN + B 58_751..58_950 CLEAN, \"\n"
    "                                       \"zero refusal points, honest forward walk, no pin \"\n"
    "                                       \"chain, no skips, W92 r370 precedent family; ADMIT \"\n"
    "                                       \"receipt results/_r583bmb_w100_band_gate.py rc0 single \"\n"
    "                                       \"state; W101+ projection: A 245_004..247_003 CLEAN / \"\n"
    "                                       \"B 58_951..59_150 REFUSED at [59_000], disclosed for \"\n"
    "                                       \"the next freezer); W97 finalize LANDED (net chain \"\n"
    "                                       \"head 577,948 = bm-b r583 one-pass, K=211,320 merged \"\n"
    "                                       \"pool) + TWO IN-FLIGHT UPSTREAM SEATS at this \"\n"
    "                                       \"freeze (W98 bm-a 12/12 burned finalize-pending + \"\n"
    "                                       \"W99 bm-c 12/12 burned finalize-pending, ALL \"\n"
    "                                       \"REGISTERED -- finalize merge loop stays \"\n"
    "                                       \"FAIL-CLOSED r307 at run time)\"),\n"
    "                            \"a_seed_base\": 243_004,        # law sec.4 W100 A: 243_004..245_003 (arithmetic continuation from W99 A tail)\n"
    "                            \"b_exit_seed_base\": 58_751,   # law sec.4 W100 B: 58_751..58_950 (arithmetic continuation from W99 B tail, no pin)\n"
    "                            \"shard_subdir\": \"n1_w100\", \"out_name\": \"n1_w100_results.json\",\n"
    "                            \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(N1)
if b'"shard_subdir": "n1_w100"' in data:
    print("SKIP n1 cfg: already present")
else:
    data2 = insert_after_entry(
        data,
        '"shard_subdir": "n1_w99", "out_name": "n1_w99_results.json",'.encode("utf-8"),
        N1_CFG_BLOCK, "n1cfg", close_line='"engine_owner": "bm-c"},',
        guard=lambda nxt: nxt.strip().startswith(b"}")
        or b'101: {"batch"' in nxt or nxt.strip().startswith(b"#"))
    assert data2.count(b'"shard_subdir": "n1_w100"') == 1
    wr(N1, data2)
    print("n1: WAVE_CONFIGS[100] inserted (+%d bytes)" % len(N1_CFG_BLOCK))

# --- 4. n1 selftest W100 materializer leg ----------------------------------------
LEG_MARK = "W100 materializer face (r583 bm-b freeze"
N1_LEG_BLOCK = (
    "\n"
    "    # --- W100 materializer face (r583 bm-b freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's\n"
    "    #     thirty-fourth owned per machine-derive (engine_owner==bm-b\n"
    "    #     rows 33 + candidate); wave 100 = first free number after\n"
    "    #     the registered W99 row (zero seat gaps: W2..W99 all\n"
    "    #     registered; single state, no skip-past chain). NINETIETH\n"
    "    #     engine wave BY MACHINE-DERIVE (engine_owner rows 89 +\n"
    "    #     candidate). Seat published=reserved MSG-20261002-1615-bmb\n"
    "    #     pushed to origin 6b8c9fa7c r582 BEFORE this freeze per\n"
    "    #     r565 law. ADMIT receipt results/_r583bmb_w100_band_gate.py\n"
    "    #     rc0 single state (B99 registered W99).\n"
    "    _set_wave(100)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[100][\"a_seed_base\"] == pf.N1_BANDS[100][\"a\"][0], \\\n"
    "            \"W100 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[100][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[100][\"b_exit\"][0], \"W100 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[100].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[100].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W100 engine_owner drift (law mirror parity)\"\n"
    "        w100_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w100_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w100_a & w100_b), \"W100 A/B band overlap\"\n"
    "        assert not (w100_a & reg_ints) and not (w100_b & reg_ints), \\\n"
    "            \"W100 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w100_a), (\"B\", w100_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W100 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W100 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W100 {nm} hits probe seeds\"\n"
    "        assert pf.N1_BANDS[95] == {\"a\": (233_004, 235_003),\n"
    "                                   \"b_exit\": (57_501, 57_700),\n"
    "                                   \"engine_owner\": \"bm-b\"}, (\n"
    "            \"registered W95 row parity drift (r307 two-state; bm-b \"\n"
    "            \"r580)\")\n"
    "        assert pf.N1_BANDS[96] == {\"a\": (235_004, 237_003),\n"
    "                                   \"b_exit\": (57_701, 57_900),\n"
    "                                   \"engine_owner\": \"bm-a\"}, (\n"
    "            \"registered W96 row parity drift (r307 two-state; bm-a \"\n"
    "            \"r581)\")\n"
    "        assert pf.N1_BANDS[97] == {\"a\": (237_004, 239_003),\n"
    "                                   \"b_exit\": (58_001, 58_200),\n"
    "                                   \"engine_owner\": \"bm-b\"}, (\n"
    "            \"registered W97 row parity drift (r307 two-state; bm-b \"\n"
    "            \"r581)\")\n"
    "        assert pf.N1_BANDS[98] == {\"a\": (239_004, 241_003),\n"
    "                                   \"b_exit\": (58_201, 58_400),\n"
    "                                   \"engine_owner\": \"bm-a\"}, (\n"
    "            \"registered W98 row parity drift (r307 two-state; bm-a \"\n"
    "            \"r582)\")\n"
    "        assert pf.N1_BANDS[99] == {\"a\": (241_004, 243_003),\n"
    "                                   \"b_exit\": (58_551, 58_750),\n"
    "                                   \"engine_owner\": \"bm-c\"}, (\n"
    "            \"registered W99 row parity drift (r307 two-state; bm-c \"\n"
    "            \"r374)\")\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 100)]:\n"
    "            assert not (w100_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W100 A hits W{wprev}\"\n"
    "            assert not (w100_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W100 B hits W{wprev}\"\n"
    "        assert not (w100_a & set(range(241_004, 243_004))) and \\\n"
    "            not (w100_b & set(range(58_551, 58_751))), (\n"
    "            \"W100 bands must clear the W99 registered bands (prior-wave \"\n"
    "            \"loop belt-and-braces)\")\n"
    "        n3r1_used100 = set(range(70_000, 70_006))\n"
    "        assert not (w100_a & n3r1_used100) and not (w100_b & n3r1_used100), \\\n"
    "            \"W100 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w100_a & lfc_actual12) and not (w100_b & lfc_actual12), \\\n"
    "            \"W100 bands must clear the lfc actual draw range\"\n"
    "        assert not (w100_a & options_actual12) and \\\n"
    "            not (w100_b & options_actual12), \\\n"
    "            \"W100 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[100][\"a_seed_base\"] == 243_004 == 243_003 + 1, (\n"
    "            \"W100 A must be the arithmetic continuation from the \"\n"
    "            \"registered W99 A tail\")\n"
    "        arith_a100 = set(range(243_004, 245_004))\n"
    "        assert not (arith_a100 & reg_ints), (\n"
    "            \"W100 A window must be CLEAN (arithmetic continuation ADMIT face)\")\n"
    "        assert WAVE_CONFIGS[100][\"b_exit_seed_base\"] == 58_751 == 58_750 + 1, (\n"
    "            \"W100 B must be the arithmetic continuation from the \"\n"
    "            \"registered W99 B tail (no pin chain, W92 r370 family)\")\n"
    "        arith_b100 = set(range(58_751, 58_951))\n"
    "        b_hit100 = sorted(p for p in arith_b100 if p in reg_ints)\n"
    "        assert b_hit100 == [], (\n"
    "            \"W100 B arithmetic window must be CLEAN (zero hits)\")\n"
    "        assert not (w100_b & reg_ints), \\\n"
    "            \"W100 B window 58_751..58_950 must be CLEAN\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W100-SHARD-0\",\n"
    "                                          \"n1w100-0of12\"), \"W100 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W100-SHARD-11\",\n"
    "                                          \"n1w100-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w100\") and OUT.endswith(\n"
    "            \"n1_w100_results.json\"), \"W100 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 100)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W100 shard dir collides with W{wprev}\"\n"
    "        for _depw in range(17, 98):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W100 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        # finalize wave-set derivation face (r511 derive law):\n"
    "        # prior-wave set derives from registry keys below 100 (no 15).\n"
    "        # Single state: W2..W99 all registered.\n"
    "        _priors100 = sorted(w for w in WAVE_CONFIGS if w < 100)\n"
    "        assert _priors100 == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 100)], (\n"
    "            \"W100 prior-wave set must derive from registry keys (no 15; \"\n"
    "            \"W2..W99 all registered, single state)\")\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W100_PREREG.md\")), \\\n"
    "            \"W100 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    i = data.find(b"# --- W99 materializer face")
    assert i >= 0, "leg anchor: W99 leg not found"
    j = data.find(b"_set_wave(2)", i)
    assert j > i, "leg anchor: W99 leg finally not found"
    j_end = data.find(b"\n", j) + 1
    nxt = data[j_end:j_end + 60]
    assert b"T-141 s2" in nxt or b"W101 materializer face" in nxt, \
        f"leg post-anchor guard (T-141 s2 lane face OR co-registered W101 leg next): {nxt[:60]!r}"
    data2 = data[:j_end] + N1_LEG_BLOCK + data[j_end:]
    assert data2.count(LEG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W100 materializer leg inserted (+%d bytes)" % len(N1_LEG_BLOCK))

# --- 5. n1 selftest PASS-print W100 fragment --------------------------------------
FRAG_MARK = "W100 row, r583 bm-b]"
N1_FRAG_BLOCK = (
    "          \"+ W100 materializer face [same guard set, dep=W17..W97 outputs \"\n"
    "          \"ALL PRESENT (landed chain head 577,948 = W97 bm-b r583 \"\n"
    "          \"one-pass; K=211,320 merged pool; TWO in-flight upstream \"\n"
    "          \"seats at freeze: W98 bm-a + W99 bm-c both 12/12 burned \"\n"
    "          \"finalize-pending, ALL REGISTERED, finalize merge loop \"\n"
    "          \"stays FAIL-CLOSED r307 at run time), \"\n"
    "          \"NINETIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE \"\n"
    "          \"(engine_owner rows 89 + candidate) bm-b's THIRTY-FOURTH \"\n"
    "          \"owned claim per machine-derive (engine_owner==bm-b rows 33 \"\n"
    "          \"+ candidate), engine_owner=bm-b per engine de-throttle law \"\n"
    "          \"O-20261001-2355 sec.2 own-continuous-series (wave 100 = \"\n"
    "          \"first FREE number after the registered W99 row, zero seat \"\n"
    "          \"gaps; seat published=reserved MSG-20261002-1615-bmb pushed \"\n"
    "          \"to the origin BEFORE the freeze per r565 law), BOTH SIDES = \"\n"
    "          \"ARITHMETIC CONTINUATION from the registered W99 tails \"\n"
    "          \"(A 243_004..245_003 + B 58_751..58_950 both CLEAN zero \"\n"
    "          \"refusal points, honest forward walk, no pin chain no \"\n"
    "          \"skips, W92 r370 precedent family; ADMIT receipt \"\n"
    "          \"results/_r583bmb_w100_band_gate.py rc0 single state; W101+ \"\n"
    "          \"projection A 245_004..247_003 CLEAN / B 58_951..59_150 \"\n"
    "          \"REFUSED at [59_000] disclosed for the next freezer (bm-a \"\n"
    "          \"W101 seat published, D-20261002-05 pin projected by their \"\n"
    "          \"gate); not a free pick -- R250; \"\n"
    "          \"probe-seed cluster leg, N3-R1 used-seed leg, \"\n"
    "          \"law sec.4 W100 row, r583 bm-b] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    # r581 bm-b note: bm-c's W99 fragment tail is the single line
    # literal "W99 row, r374 bm-c] " (anchor = that line, NOT the
    # concatenated phrase).
    anchor = b'"W99 row, r374 bm-c] "'
    i = data.find(anchor)
    assert i >= 0, "frag anchor: W99 fragment end not found"
    j = data.find(b"\n", i) + 1
    nxt = data[j:j + 40]
    assert b'"+ T-141 s2' in nxt or b"W101 materializer face" in nxt, \
        f"frag post-anchor guard: {nxt[:40]!r}"
    data2 = data[:j] + N1_FRAG_BLOCK + data[j:]
    assert data2.count(FRAG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W100 PASS fragment inserted (+%d bytes)" % len(N1_FRAG_BLOCK))

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")
